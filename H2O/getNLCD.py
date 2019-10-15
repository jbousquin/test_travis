#!/usr/bin/env python
import requests
from os.path import join

try:
    from H2O.utils import py as utils
except:
    from H2O.utils import arc as utils


def strReq(url, data):
    """Use requests lib to print url server request"""
    return requests.Request('GET', url, params=data).prepare().url


def checkYear(year, years = None):
    """Run checks and formatting on year"""
    year = str(year) # coerce to string in case float() or int()
    assert year.isdigit(), "The year parameter must be numeric"
    if years:
        assert year in years, "The year {} is not available".format(year)
    return year


def getNLCD(poly, directory = None, dataset = "Land_Cover", year = "2016"):
    """Download NLCD raster tiles by polygon extent
    Currently only works for lower 48, add 'AK', 'HI' and 'PR'
    Currently requires poly be in EPSG 3857
    """
    # Make sure dataset parameter is usable
    datasets = ["Land_Cover", "Impervious", "Tree_Canopy"]
    assert dataset in datasets, "Input dataset {} does not match".format(dataset)
    # Make sure year parameter is usable
    year = checkYear(year)
    
    # Get bounding box
    bBox = utils.getBoundingBox(poly)
    # Transform bounding box to EPSG 3857
    #asert poly is projected?
    inSR = utils.getCRS(poly) # Determine current EPSG
    bBox = utils.transform_bBox(bBox, inSR, 3857)
    
    # Determine landmass (will use bBox to set landmass in the future)
    landmass = "L48"
    coverage = "NLCD_{}_{}_{}".format(year, dataset, landmass)

    # Source url
    url = "https://www.mrlc.gov/geoserver/mrlc_display/{}/ows".format(coverage)
    # Check url status
    if requests.get(url).status_code != 200:
        utils.message("Error: No web coverage service at {}".format(url))
    
    # Create subset X and Y string from extent
    subset = ['X("{}","{}")'.format(bBox[0], bBox[2]),
              'Y("{}","{}")'.format(bBox[1], bBox[3])]

    # Create params dict
    data = {"service": "WCS",
            "version": "2.0.1",
            "request": "GetCoverage",
            "coverageid": coverage,
            "subset": subset
            }
    # Get response
    res = requests.get(url, data)
    assert res.ok, "Problem with NLCD response: {}".format(strReq(url, data))

    # Write response to directory if provided
    if directory is not None:    
        out_file = join(directory, "NLCD_{}_{}.tif".format(year, dataset))
        with open(out_file, "wb") as f:
            f.write(res.content)
    #else:
        #return data
