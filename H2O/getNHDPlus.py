import requests
import os
from json import loads

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
##def arc_getSR(fc):
##    """ Returns spatial reference factory code, GCS - WGS 1984 by default"""
##    desc = arcpy.Describe(fc)
##    code = desc.spatialReference.factoryCode
##    if code == 0: # if 0 -> 4326 Geographic Coordinate system "WGS 1984"
##        #project? going to be harder without CRS
##        code = 4326
##    return code
##
##
##def arc_getBoundingBox(fc):
##    """Returns dataset extent envelope"""
##    desc = arcpy.Describe(fc)
##    xmin = desc.extent.XMin
##    xmax = desc.extent.XMax
##    ymin = desc.extent.YMin
##    ymax = desc.extent.YMax
##
##    return [(xmin, xmax), (ymin, ymax)]
##
##AOI = r"C:\ArcGIS\Local_GIS\H2O\AOI\Monroe_Parish_3857.shp"
##
##dataset = "NHDPlusAttributes"
##VPU = "11"
##
##out_file = os.path.dirname(AOI) + os.sep + "{}_{}".format(dataset, VPU)
##
##source = "https://cida.usgs.gov/nwc/geoserver/nhdplus/ows"
##
### Check source status
##if requests.get(source).status_code != 200:
##    print("warning!")
##
### Get AOI extent
##bBox = arc_getBoundingBox(AOI) #expects ESPG 4326
##
###create params dict (WFS/WMS)
##data = {"service": "WFS",
##        "request": "GetFeature"
##        
##        }
###https://cida.usgs.gov/nwc/geoserver/nhdplus/ows?service=WFS&request=GetFeature&Envelope=-92.415418,32.258552,-91.90328,32.723003
###https://cida.usgs.gov/nwc/geoserver/nhdplus/ows?service=WFS&request=GetFeature&typeName=feature&Envelope=32.258552,-92.415418,32.723003,-91.90328
##
### STEP1 determine RPU/VPU from boundary and extent
##
### STEP2 intersect catchments using geometry
##url = 'https://dservices6.arcgis.com/2TtZhmoHm5KqwqfS/arcgis/services/Catchment_MS_08/WFSServer'
##data = {"service": "WFS",
##        "request": "GetFeature",
##        }
def getNHD_VPU(inAOI):
    #https://services6.arcgis.com/2TtZhmoHm5KqwqfS/arcgis/rest/services/NHDPlus_V2_BoundaryUnit/FeatureServer
    service = {'server_url':"services6.arcgis.com/2TtZhmoHm5KqwqfS/arcgis/rest/services",
               'mapServer':"NHDPlus_V2_BoundaryUnit/FeatureServer",
               'layer': {0:'NHDPlus_V2_BoundaryUnit'},
               }
    url = "https://{}/{}".format(service['server_url'], service['mapServer'])
    serverQuery = "{}/{}/query".format(url, service['layer'][0].keys()[0])

    fields = ["DrainageID", "UnitID"]

    payload = geoQuery.geoQuery(inAOI.envelope, inAOI.SR, fields)
    payload['returnGeometry'] = False
    res = loads(mapServerRequest(serverQuery, payload))
    try:
        if len(res['features'])>0:
            drainIDs = [f['attributes']['DrainageID'] for f in res['features']]
            VPUs = [f['attributes']['UnitID'] for f in res['features']]
            return ['{}_{}'.format(drainIDs[i], v) for i, v in enumerate(VPUs)]
    except:
        return res
        

def getCatchments_MS_08(inAOI, shp_out = None):
    #https://services6.arcgis.com/2TtZhmoHm5KqwqfS/arcgis/rest/services/Catchment_MS_08/FeatureServer/0
    # Service details (should be object)
    service = {'Name':"Catchment_MS_08",
               'server_url':"services6.arcgis.com/2TtZhmoHm5KqwqfS/arcgis/rest/services",
               'mapServer':"Catchment_MS_08/FeatureServer",
               'layer':[{0:"Catchment_MS_08"},
                        ],
               }
    url = "https://{}/{}".format(service['server_url'], service['mapServer'])

    # Query
    if shp_out is None:
        returnGeo = False
    else:
        returnGeo = True

    # In the future the layer list should include all RPUs ane be subset within
    #this function based on an extent query on RPU boundary service.
    serverQuery = "{}/{}/query".format(url, service['layer'][0].keys()[0])

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
                    utils.json2shp(ret, shp_out + '_res')
                else:
                    res = loads(mapServerRequest(serverQuery, payload))

                    try:
                        if len(res['features'])>0:
                            return res['features'][0]['attributes']
                    except:
                        return res
            else:
                print("No features in {} layer").format(layer.values()[0])