# -*- coding: utf-8 -*-
"""getFIPs function to return county FIPs for a given goepandas dataframe
envelope. Can also easily be used to return county name.
"""
import geopandas
import requests
from json import loads
from H2O.utils import py as utils


def strReq(url, data):
    """Use requests lib to print url server request"""
    return requests.Request('GET', url, params=data).prepare().url


def geoQuery(geo, inSR, fields, geoType = "esriGeometryEnvelope"):
    """ Return query as formatted dicitonary"""
    data = {"geometry": geo,
            "geometryType": geoType,
            "inSR": inSR,
            "spatialRel": "esriSpatialRelIntersects",
            "returnGeometry": "false",
            "outFields": ','.join(fields),
            }
    return data


def mapServerRequest(catalog, service, layer, query, server = "arcgis",
                     typ = "MapServer", token = ""):
    """send query to map server using requests"""
    url = "https://{}/{}/rest/services/{}/{}/".format(catalog, server,
                                                      service, typ)
    if layer is not None:
        url += "{}/".format(layer)

    # add query to url
    url += 'query'
    
    # Return json
    query['f'] = 'json'
    if token:
        # This won't actually work as written.
        query["token"] = token
    try:
        res = requests.get(url, query)
        assert res.ok, "Problem with {} response".format(url)
        return loads(res.content.decode('utf-8'))
    except Exception:
        utils.message("Problem with map response: {}".format(strReq(url, data))
        raise


def polyFIPS(poly):
    """Returns county FIPs intersecting polygon extent"""
    envelope = ','.join(map(str, utils.getBoundingBox(poly))) # Get extent as str
    inSR = utils.getCRS(poly) # Get spatial reference
    fields = ["NAME", "GEOID"]
    query = geoQuery(envelope, inSR, fields)
    catalog = "tigerweb.geo.census.gov"
    service = "TIGERweb/tigerWMS_Current"
    layer = 86 #Counties ID: 86
    resultJSON = mapServerRequest(catalog, service, layer, query)
    #counties = [c['attributes'][fields[0]] for c in resultJSON['features']]
    FIPS = [c['attributes'][fields[1]] for c in resultJSON['features']]

    return FIPS
