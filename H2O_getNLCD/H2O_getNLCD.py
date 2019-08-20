#!/usr/bin/env python

import os
import requests
import geopandas
#import arcpy
##
##def arc_getBoundingBox(fc):
##    """Returns dataset extent envelope"""
##    desc = arcpy.Describe(fc)
##    xmin = desc.extent.XMin
##    xmax = desc.extent.XMax
##    ymin = desc.extent.YMin
##    ymax = desc.extent.YMax
##
##    return [xmin, ymin, xmax, ymax]


def gpd_transform_bBox(bBox, inEPSG, outEPSG):
    pnt1 = (bBox[0], bBox[2])
    pnt1_out = arc_transform_pnt(pnt1, inEPSG, outEPSG)
    pnt2 = (bBox[1], bBox[3])
    pnt2_out = arc_transform_pnt(pnt2, inEPSG, outEPSG)

    return [pnt1_out[0], pnt2_out[0], pnt1_out[1], pnt2_out[1]]


def gpd_getBoundingBox(shp):
    """Use geopandas library instead of arcpy
    param@fc should be a shapefile
    """
    #shp = geopandas.read_file(fc)
    xmin = shp.bounds['minx'][0]
    xmax = shp.bounds['maxx'][0]
    ymin = shp.bounds['miny'][0]
    ymax = shp.bounds['maxy'][0]

    return [xmin, ymin, xmax, ymax]


def gpd_prj(shp):
    """Return EPSG for shapefile"""
    #shp = geopandas.read_file(fc)
    return shp.crs['init'][5:]


def py_transform_pnt(pnt, inEPSG, outEPSG):
    """Use pyproj instead of arcpy (pyproj is geopandas dependency)
    from pyproj import Proj, transform
    pnt is expected as x,y tuple
    """
    x1, y1 = pnt[0], pnt[1] #added benefit of checking pnt format
    inProj = pyproj.Proj(init='epsg:{}'.format(inEPSG))
    outProj = pyproj.Proj(init='epsg:{}'.format(outEPSG))

    return pyproj.transform(inProj, outProj, x1, y1)


def getNLCD(poly, directory, dataset ="Land_Cover", year = "2011"):
    """Download NLCD raster tiles by polygon extent
    Currently only works for lower 48
    Currently requires poly be in EPSG 3857
    """
    pathD1 = os.path.join(directory, "D1")

    # Make sure dataset parameter is usable
    datasets = ["Land_Cover", "Canopy", "Impervious"]
    if dataset not in datasets:
        message("Error: specified NLCD dataset not available")

    # Get bounding box
    bBox = gpd_getBoundingBox(poly)
    # Transform bounding box to EPSG 3857
    inSR = gpd_prj(poly) # Determine current EPSG
    bBox = (bBox, inSR, 3857)
    
    # Determine landmass (will use bBox to set landmass in the future)
    landmass = "L48"
    coverage = "NLCD_{}_{}_{}".format(year, dataset, landmass)

    # Source url
    url = "https://www.mrlc.gov/geoserver/mrlc_display/{}/ows".format(coverage)
    # Check url status
    if requests.get(url).status_code != 200:
        message("warning!")
    
    # Create subset X and Y string from extent
    subset = ["X{},{}".format(bBox[0], bBox[2]),
              "Y{},{}".format(bBox[1], bBox[3])]

    # Create params dict
    data = {"service": "WCS",
            "version": "2.0.1",
            "request": "GetCoverage",
            "coverageid": coverage,
            "subset": subset
            }
    # Get response
    res = requests.get(url, data)

    # Write response to D1 (already unpacked)
    out_file = pathDA + os.sep + "NLCD_{}_{}.tif".format(year, dataset)
    with open(out_file, "wb") as f:
        f.write(res.content)


### Purpose: script to get NLCD rasters for bounding box
##AOI = r"C:\ArcGIS\Local_GIS\H2O\AOI\Monroe_Parish_3857.shp"
##directory = os.path.dir(AOI)
##year = "2016"
##dataset = "Land_Cover"
##
##getNLCD(AOI, directory, dataset, year)
