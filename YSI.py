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

# Plot
def plotter(df,var1,var2,basin=True,pH=False, ci=95):
    df       = df[df[var1].notnull() & df[var2].notnull()].copy()
    df[var1] = pd.to_numeric(df[var1])
    df[var2] = pd.to_numeric(df[var2])
        
    if basin:
        stats_dict = {}
        for group, group_df in df.groupby('Watershed'):
            if len(group_df) > 1:  # Ensure enough data points
                r, p = sp.stats.pearsonr(group_df[var1], group_df[var2])
                stats_dict[group] = {'r': r, 'p': p, 'r2': r ** 2}
            else:
                stats_dict[group] = {'r': np.nan, 'p': np.nan, 'r2': np.nan}
        
        fig  = sns.lmplot(data=df,x=var1,y=var2,
                          hue='Watershed',ci=ci,fit_reg=True,
                          line_kws={"linestyle": "--"})
        
        # Build Legend
        ax = fig.ax
        handles, labels = ax.get_legend_handles_labels()
        new_labels = []
        for label in labels:
            stats = stats_dict.get(label, {})
            if not stats or np.isnan(stats['r']):
                new_label = f"{label} (insufficient data)"
            else:
                new_label = f"{label}\n    r²={stats['r2']:.2f}\n    r={stats['r']:.2f}\n    p={stats['p']:.2g}"
            new_labels.append(new_label)
        
        # Replace legend
        fig._legend.remove()
        ax.legend(handles=handles, labels=new_labels, title="Watershed",
          title_fontproperties=FontProperties(weight='bold'), 
          bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
   
    else:
        fig = sns.lmplot(data=df,x=var1,y=var2,
                         ci=ci,fit_reg=True,line_kws={"linestyle": "--"})
        
        def annotate(data, **kws):
            r, p = sp.stats.pearsonr(data[var1], data[var2])
            r2   = r**2
            ax   = plt.gca()
            ax.text(.8, .8, 'r$^2$={:.4f}\nr={:.2f}\np={:.2g}'.format(r2, r, p),
                    transform=ax.transAxes)
        fig.map_dataframe(annotate)
    
    # Make it pretty
    plt.xlabel(var1)
    plt.ylabel(var2)
    if pH:
        plt.xlim(4,10)
    
# Call
plotter(df,'pH','Elevation (m)',pH=True)
plotter(df,'Conductivity (uS/cm)','Elevation (m)',ci=False)
plotter(df,'Temp (C)','Elevation (m)')
