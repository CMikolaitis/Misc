import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import seaborn as sns
import scipy as sp
import os

pd.set_option('future.no_silent_downcasting', True)

# Import and clean
infile         = pd.read_excel('Colorado WQ.xlsx',sheet_name='Field Data')
df             = infile.replace([-999999,np.nan],'')
df['Date']     = pd.to_datetime(df['Date']).dt.date
df['datetime'] = df['Date'].astype(str) + ' ' + df['Time'].astype(str)
df['datetime'] = pd.to_datetime(df['datetime'],format='mixed')
df             = df.replace('',np.nan)

if not os.path.exists('FieldData.csv'):
    df.to_csv('FieldData.csv',index=False)
else:
    print('FieldData.csv exists, skipping save.')

## Plot
# df is input dataframe
# var1 is x
# var2 is y
# focus allows for filtering of watersheds
# basin is a toggle for multiple groups on same plot
# branch tells what groups to use, coupled with basin (prob refactor later)
# pH, set x-axis to 4-10
# ci, what confidence interval do you want?
def plotter(df,var1,var2,focus='',basin=True,branch='Watershed',
            pH=False,ci=95, outname=''):
    df       = df[df[var1].notnull() & df[var2].notnull()].copy()
    df[var1] = pd.to_numeric(df[var1])
    df[var2] = pd.to_numeric(df[var2])
    if len(focus)>0:
        df = df[df["Watershed"] == focus]
        
    stats_dict = {}
    for group, group_df in df.groupby(branch):
        if len(group_df) > 1:  # Ensure enough data points
            r, p = sp.stats.pearsonr(group_df[var1], group_df[var2])
            stats_dict[group] = {'r': r, 'p': p, 'r2': r ** 2}
        else:
            stats_dict[group] = {'r': np.nan, 'p': np.nan, 'r2': np.nan}    
        
    if basin:
        fig  = sns.lmplot(data=df,x=var1,y=var2,
                          hue=branch,ci=ci,fit_reg=True,
                          line_kws={"linestyle": "--"})
    else:
        fig = sns.lmplot(data=df,x=var1,y=var2,
                         ci=ci,fit_reg=True,line_kws={"linestyle": "--"},
                         legend=True)
    # Build Legend
    if fig._legend:
        fig._legend.set_visible(False)
    
    ax = fig.ax
    handles, labels = ax.get_legend_handles_labels()
    if not handles or not labels:
        unique_group = df[branch].unique()
        if len(unique_group) == 1:
            label = unique_group[0]
            stats = stats_dict.get(label, {})
            if not stats or np.isnan(stats['r']):
                new_label = f"{label} (insufficient data)"
            else:
                new_label = f"{label}\n    r²={stats['r2']:.2f}\n    r={stats['r']:.2f}\n    p={stats['p']:.2g}"
            # Use any existing artist to create a dummy handle
            handle = plt.Line2D([], [], marker='o', color='gray', linestyle='None')
            handles = [handle]
            new_labels = [new_label]
        else:
            new_labels = labels
    else:
        # Multiple groups — build new labels
        new_labels = []
        for label in labels:
            stats = stats_dict.get(label, {})
            if not stats or np.isnan(stats['r']):
                new_label = f"{label} (insufficient data)"
            else:
                new_label = f"{label}\n    r²={stats['r2']:.2f}\n    r={stats['r']:.2f}\n    p={stats['p']:.2g}"
            new_labels.append(new_label)

    # Add custom legend
    ax.legend(handles=handles, labels=new_labels, title="Watershed",
          title_fontproperties=FontProperties(weight='bold'),
          bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    # Make it pretty
    plt.xlabel(var1)
    plt.ylabel(var2)
    if pH:
        plt.xlim(4,10)
    
    # Save
    if len(outname)>0:
        plt.savefig(outname,dpi=600,format='png')
    
# Call
plotter(df,'pH','Elevation (m)',pH=True,focus='Copper Creek',branch='Branch',outname='CC_pH')
plotter(df,'Conductivity (uS/cm)','Elevation (m)',focus='Copper Creek',branch='Branch',outname='CC_Cond')
plotter(df,'Temp (C)','Elevation (m)',focus='Copper Creek',branch='Branch',outname='CC_temp')
