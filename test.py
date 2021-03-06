#!/usr/bin/env python
import os
import geopandas
from H2O import getNLCD
from H2O import getFIPs
from H2O import getRoads
from H2O import getNHDPlus
from H2O import getWQP
#from future.utils import listvalues
from H2O.utils import py as utils


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

# Test getWQ
data = {'characteristicName': ['Salinity',
                               'Chlorophyll a, uncorrected for pheophytin',
                               'Ammonia-nitrogen', 'Organic Nitrogen',
                               'Dissolved oxygen saturation',
                               'Dissolved oxygen (DO)',
                               'Dissolved Oxygen',
                               'Oxygen',
                               'Dissolved oxygen'
                               ]
        }
#wqList =['Salinity', 'Chlorophyll-All', 'Nitrogen-All','Dissolved Oxygen-All']
## Format data dictionary based on wqList
#for wq in wqList:
#    cKey = 'characteristicName'
#    # Check if data dictionary exists yet
#    if cKey in data.keys():
#        # Characteristics to add
#        newChar = listvalues(getWQP.characteristicName(wq))[0]
#        data[cKey] = data[cKey] + newChar
#    else:
#        data = getWQP.characteristicName(wq)

# Test get by FIPS
list_FIPs = getFIPs.polyFIPS(gpd_df)

for FIP in list_FIPs:
    # Get station data
    getWQP.byFIP(FIP, data, filepath)


# Test get by bbox
bBox = utils.getBoundingBox(gpd_df)

# Get station data
getWQP.byBBox(bBox, data, filepath)

# Get data from narrowResult
data['dataTable'] = 'Result'
data['dataProfile'] = 'narrowResult'
getWQP.byBBox(bBox, data, filepath)
