#!/usr/bin/env python
"""
Generic geoQuery functions
"""
import os

try:
    from H2O.utils import py as utils
except:
    from H2O.utils import arc as utils


def geoQuery(geo, inSR, fields, geoType = "esriGeometryEnvelope"):
    """ Return query as formatted dicitonary"""
    #not tested on Mutlipoint, Mutltipatch
    assert geoType in ["esriGeometryEnvelope",
                       "esriGeometryPolygon",
                       "esriGeometryPolyline",
                       "esriGeometryPoint",
                       ], "{} type unexpected".format(geoType)
    data = {"geometry": geo,
            "geometryType": geoType,
            "inSR": inSR,
            "spatialRel": "esriSpatialRelIntersects",
            "returnGeometry": "false",
            "outFields": ','.join(fields),
            "f": "json",
            }
    return data


class AOI:
    def __init__(self, shp):
        self.path = os.path.dirname(shp)
        self.name = os.path.basename(shp)
        self.type = utils.shapeType(shp)
        # List of geometry
        self.geometry = utils.geoList(shp)
        # Extent as string
        self.envelope = ','.join(map(str, utils.getBoundingBox(poly)))
        # SpatialReference Factory Code
        self.SR = utils.getCRS(shp)

    def __str__(self):
        return "AOI object based on %s" % self.name
