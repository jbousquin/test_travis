# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 12:34:03 2019

@author: jbousqui
"""

import arcpy
import os
import requests
import geopandas


def getBoundingBox(fc):
    """Returns dataset extent envelope"""
    desc = arcpy.Describe(fc)
    xmin = desc.extent.XMin
    xmax = desc.extent.XMax
    ymin = desc.extent.YMin
    ymax = desc.extent.YMax

    return [xmin, ymin, xmax, ymax]


def getCRS(fc):
    """ Returns spatial reference factory code, GCS - WGS 1984 by default"""
    desc = arcpy.Describe(fc)
    code = desc.spatialReference.factoryCode
    if code == 0: # if 0 -> 4326 Geographic Coordinate system "WGS 1984"
        #project? going to be harder without CRS
        code = 4326
    return code


def transform_pnt(pnt, inEPSG, outEPSG):
    """pnt is expected as x,y tuple
    inEPSG/outEPSG expected as factory code
    """
    # Create point geometry
    pt = arcpy.Point()
    pt.X, pt.Y = pnt[0], pnt[1]
    # Manage CRS
    in_CRS = arcpy.SpatialReference(inEPSG)
    out_CRS = arcpy.SpatialReference(outEPSG)
    # Manage transform method for CRS -> CRS
    transforms = arcpy.ListTransformations(in_CRS, out_CRS)
    # Try to ignore any custom tranformations
    new = "New Geographic Transformation"
    transforms = [trans for trans in transforms if not trans.endswith(new)]
    if len(transforms) > 0:
        trans = transforms[0] # first is default
    else:
        trans = '' # problem?
    # Do transform
    ptgeoIn = arcpy.PointGeometry(pt, in_CRS) # assign CRS to point geometry
    ptgeoOut = ptgeoIn.projectAs(out_CRS, trans)
    pt_out = ptgeoOut.lastPoint
    assert pt_out != None, "Error projecting {} from {} to {}".format(pnt,
                                             inEPSG, outEPSG)
    return (pt_out.X, pt_out.Y)


def transform_bBox(bBox, inEPSG, outEPSG):
    """Add function documentation"""
    pnt1 = (bBox[0], bBox[1])
    pnt1_out = transform_pnt(pnt1, inEPSG, outEPSG)
    pnt2 = (bBox[2], bBox[3])
    pnt2_out = transform_pnt(pnt2, inEPSG, outEPSG)

    return [pnt1_out[0], pnt1_out[1], pnt2_out[0], pnt2_out[1]]


def mapServerRequest(serverQuery, payload):
    '''Returns string response from query'''
    ret = requests.post(serverQuery, payload)
    return ret.text


def getNHDPlus_catchment(AOI):
    """catchments from USGS by extent"""
    source = "https://cida.usgs.gov/nwc/geoserver/nhdplus/ows"
    #Check source
    if requests.get(source).status_code != 200:
        print("warning!")
    
    #Query params from AOI
    bBox_in = getBoundingBox(AOI)
    crs = getCRS(AOI)
    #transform to native
    bBox = transform_bBox(bBox_in, crs, 3857)
    
    #Create WFS params dict
    data = {"service": "WFS",
            "request": "GetFeature",
            "typeName": "catchmentsp",
            "maxFeatures": 1000,
            "bbox": str(bBox).strip('[]'),
            "outputFormat": 'json',
            }

    #typenames = ['catchmentsp','nhdwaterbody','nhdarea','nhdflowline_network']
    #crs = [3857, 4269, 4269, 4269]
    res = mapServerRequest(source, data)
    
    return res

example_fld = r"C:\ArcGIS\Local_GIS\ESI\Demo\test_travis-master\tests\example_shp"
AOI = os.path.join(example_fld, "example_AOI.shp")
res = getNHDPlus_catchment(AOI)
red = geopandas.read_file(res)
