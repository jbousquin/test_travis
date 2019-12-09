#!/usr/bin/env python
import os
import geopandas
from H2O import getNLCD
from H2O import getFIPs
from H2O import getRoads
from H2O import getNHDPlus

# Purpose: Test script to get NLCD rasters for bounding box

# Example shapefile
filepath =  os.path.realpath(os.path.join(os.getcwd(),
                                          os.path.dirname(__file__)))
shp = os.path.join(filepath, "tests/example_shp/example_AOI.shp")

# Read example shapefile to geopandas dataframe
gpd_df = geopandas.read_file(shp)

# Test defaults
getNLCD.getNLCD(gpd_df)

# Test multiple years/datasets
years = ["2001", "2006", "2011", "2016",]
datasets = ["Land_Cover", "Impervious", "Tree_Canopy",]
for year in years:
    for dataset in datasets:
        #Canopy isn't available for every year
        if dataset != "Tree_Canopy":
            getNLCD.getNLCD(gpd_df, filepath, dataset, year)
        else:
            if year in ["2011", "2016"]:
                getNLCD.getNLCD(gpd_df, filepath, dataset, year)


#Move this section to getFIPS test
list_FIPs = getFIPs.polyFIPS(gpd_df)

for FIP in list_FIPs:
    getRoads.getRoads(FIP, directory = filepath)

# Test get catchments from USGS  
getNHDPlus.getCatchments_USGS(gpd_df, directory=filepath)
