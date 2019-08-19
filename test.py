import os
from H2O_getNLCD import getNLCD

# Purpose: script to get NLCD rasters for bounding box
AOI = r"C:\ArcGIS\Local_GIS\H2O\AOI\Monroe_Parish_3857.shp"
directory = os.path.dir(AOI)
year = "2016"
dataset = "Land_Cover"

getNLCD(AOI, directory, dataset, year)
