import os
import geopandas
from H2O_getNLCD import getNLCD

# Purpose: Test script to get NLCD rasters for bounding box

# Example shapefile
filepath =  os.path.realpath(os.path.join(os.getcwd(),
                                          os.path.dirname(__file__)))
shp = os.path.join(filepath, "example_shp/example_AOI.shp"

# Read example shapefile to geopandas dataframe
gpd_df = geopandas.read_file(shp)

year = "2016"
dataset = "Land_Cover"

getNLCD(gpd_df, filepath, dataset, year)
