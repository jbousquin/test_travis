import os
import arcpy
import requests


def arc_getBoundingBox(fc):
    """Returns dataset extent envelope"""
    desc = arcpy.Describe(fc)
    xmin = desc.extent.XMin
    xmax = desc.extent.XMax
    ymin = desc.extent.YMin
    ymax = desc.extent.YMax

    return [xmin, ymin, xmax, ymax]


def getNLCD(poly, directory, dataset ="Land_Cover", year = "2011"):
    """Download NLCD raster tiles by polygon extent
    Currently only works for lower 48
    """
    pathD1 = os.path.join(directory, "D1")

    # Make sure dataset parameter is usable
    datasets = ["Land_Cover", "Canopy", "Impervious"]
    if dataset not in datasets:
        message("Error: specified NLCD dataset not available")

    # Get bounding box
    bBox = arc_getBoundingBox(AOI) #expects ESPG 3857
    
    # Determin landmass 
    landmass = "L48"
    coverage = "NLCD_{}_{}_{}".format(year, dataset, landmass)

    # Source url
    url = "https://www.mrlc.gov/geoserver/mrlc_display/{}/ows".format(coverage)
    # Check url status
    if requests.get(source).status_code != 200:
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
    res = requests.get(source, data)

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
