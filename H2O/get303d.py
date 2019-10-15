#!/usr/bin/env python
import requests
import os
from json import loads
from H2O import geoQuery

try:
    from H2O.utils import py as utils
except:
    from H2O.utils import arc as utils


def mapServerRequest(serverQuery, payload):
    '''Returns string response from query'''
    ret = requests.post(serverQuery, payload)
    return ret.text


def testResultLength(serverQuery, payload):
    """See number of responses query returns"""
    payload['returnIdsOnly'] = True
    ret = mapServerRequest(serverQuery, payload)
    res = loads(ret)
    if(res['objectIds']):
        return len(res['objectIds'])
    return 0


def get303D_byPoly(inAOI, shp_out = None):
    """ Get impaired polygons/lines/points for inAOI geometries
    """
    # Service details (should be object)
    service = {'Name':"Assessed 303(b) Waters",
               'server_url':"watersgeo.epa.gov/arcgis/rest/services/OWRAD_NP21",
               'mapServer':"305B_NP21/MapServer",
               'layer':[{0:"Point"},
                        {1:"Line"},
                        {2:"Area"},],
               }
    service['Name'] = "Impaired 303(d) Waters"
    service['mapServer'] = "303D_NP21/MapServer"
    url = "https://{}/{}".format(service['server_url'], service['mapServer'])

    # Query
    if shp_out is None:
        returnGeo = False
    else:
        returnGeo = True
        
    for layer in service['layer']:
        serverQuery = "{}/{}/query".format(url, layer.keys()[0])

        for inGeo in inAOI.geometry:
            payload = geoQuery.geoQuery(inGeo.JSON, inAOI.SR, "*", inAOI.type)
            payload['returnGeometry'] = returnGeo
            payload['returnTrueCurves'] = True

            #get length of response first
            if testResultLength(serverQuery, payload)>0:
                payload['returnIdsOnly'] = False
                if returnGeo is True:
                    #split query if necessary
                    #write result
                    ret = mapServerRequest(serverQuery, payload)
                    utils.json2shp(ret, shp_out + '_' + layer.values()[0])
                else:
                    res = loads(mapServerRequest(serverQuery, payload))

                    try:
                        if len(res['features'])>0:
                            return res['features'][0]['attributes']
                    except:
                        return res
            else:
                print("No features in {} layer").format(layer.values()[0])
