import pyproj
import geopandas
from json import loads


def py_prj(shp):
    """Return EPSG for shapefile"""
    #shp = geopandas.read_file(fc)
    return shp.crs['init'][5:]


def py_getBoundingBox(shp):
    """Use geopandas library instead of arcpy
    param@shp should be a geopandas dataframe object
    """
    #shp = geopandas.read_file(fc)
    xmin = shp.bounds['minx'][0]
    xmax = shp.bounds['maxx'][0]
    ymin = shp.bounds['miny'][0]
    ymax = shp.bounds['maxy'][0]

    return [xmin, ymin, xmax, ymax]


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
    # Return json
    query['f'] = 'json'
    if token:
        # This won't actually work as written.
        query["token"] = token
    try:
        res = requests.get(url, query)
        assert res.ok
        return loads(res.content)
    except Exception as exc:
        message("Could not get a response using: " + url + query)
        raise


def polyFIPS(poly):
    """Returns county FIPs intersecting polygon extent"""
    envelope = ','.join(map(str, py_getBoundingBox(poly))) # Get extent as str
    inSR = py_prj(poly) # Get spatial reference
    fields = ["NAME", "GEOID"]
    query = geoQuery(envelope, inSR, fields)
    catalog = "tigerweb.geo.census.gov"
    service = "TIGERweb/tigerWMS_Current"
    layer = 86 #Counties ID: 86
    resultJSON = mapServerRequest(catalog, service, layer, query)
    #counties = [c['attributes'][fields[0]] for c in resultJSON['features']]
    FIPS = [c['attributes'][fields[1]] for c in resultJSON['features']]

    return FIPS
