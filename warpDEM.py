from osgeo import gdal
from pathlib import Path

inputTifs = Path("D:\\PhD v2\\DEM")
outputTif = Path("D:\\PhD v2\\DEM_mosaic_v2.tif")
outputVRT = Path("D:\\PhD v2\\DEM_mosaic_v2.vrt")

# Grab all files and dump in list
tifs =[str(f) for f in sorted(inputTifs.glob("*.tif"))]

# Build vrt
vrt_options = gdal.BuildVRTOptions(resolution='highest')
gdal.BuildVRT(str(outputVRT),tifs,options=vrt_options)
print("Done with VRT")

# Take vrt and make hard copy
gdal.Warp(str(outputTif), str(outputVRT), 
    creationOptions=["COMPRESS=LZW","TILED=YES","BIGTIFF=YES",],
    warpOptions=['NUM_THREADS=ALL_CPUS'])
print("Done with Warp")

# gdal.Warp(str(outputTif), tifs, creationOptions=["COMPRESS=LZW","TILED=YES","BIGTIFF=YES",])
