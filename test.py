#!/usr/bin/env python
import os
import geopandas
from H2O_getNLCD import H2O_getNLCD

# Purpose: Test script to get NLCD rasters for bounding box

# Example shapefile
filepath =  os.path.realpath(os.path.join(os.getcwd(),
                                          os.path.dirname(__file__)))
shp = os.path.join(filepath, "tests/example_shp/example_AOI.shp")

# Read example shapefile to geopandas dataframe
gpd_df = geopandas.read_file(shp)

# Test defaults
H2O_getNLCD.getNLCD(gpd_df)

# Test multiple years
years = ["2001", "2006", "2011", "2016",]
datasets = ["Land_Cover", "Impervious", "Canopy_Cartographic",]
for year in years:
    for dataset in datasets:
    H2O_getNLCD.getNLCD(gpd_df, filepath, dataset, year)
