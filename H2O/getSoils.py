import os
import requests
from H2O.utils import py as utils


def getPoly_surveys(poly, directory = None):
    """Query survey areassymbol (SSA) based on polygon bounding box
    """
    # Get bounding box
    bBox = utils.getBoundingBox(poly)
    # Transform bounding box to EPSG 4269?
    #asert poly is projected?
    inSR = utils.getCRS(poly) # Determine current EPSG
    bBox = utils.transform_bBox(bBox, inSR, 4269)
    
    # Source url
    url = "https://sdmdataaccess.nrcs.usda.gov/Spatial/SDMNAD83Geographic.wfs"
    # Check url status
    if requests.get(url).status_code != 200:
        utils.message("Error: No web feature service at {}".format(url))    

    # Create params dict
    data = {"service": "WFS",
            "version": "1.0.0",
            "request": "GetFeature",
            "Typename": "SurveyAreaPoly",
            "BBOX": ','.join(map(str,bBox)),
            }
    
    # Get response
    res = requests.get(url, data)
    assert res.ok, "Problem with soil survey response"

    # Write response to directory if provided
    if directory != None:    
        out_file = os.path.join(directory, "SSA_soils.gml")
        with open(out_file, "wb") as f:
            f.write(res.content)


##def querySSA(query):
##    """Do SQL query"""
##    #test SQL at https://sdmdataaccess.nrcs.usda.gov/Query.aspx
##    dataQuery = '{}{}, {}{}'.format('{', query, 'format: "JSON"', '}')
##    url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/SDMTabularService/post.rest"
##    # Make request & return response
##    return json_load_str(api_request(url, dataQuery))
##
##
##def getCounty_surveys(SSA):
##    """Create SQL query for survey areasymbol (SSA) based on formated FIP"""
##    tblA = "legend" # Legend table
##    tblB = "laoverlap" # Legend Area Overlap Table
##    aSymbol = "areasymbol" # Area symbol field name used in both tables
##    cond1 = "{}.lkey = {}.lkey".format(tblA, tblB) # lkey = lkey
##    cond2 = "{}.{} = '{}'".format(tblB, aSymbol, SSA) # areasymbol = SSA
##    sJoin = "INNER JOIN {} ON {} AND {}".format(tblB, cond1, cond2)
##    query = 'query: "SELECT {0}.{1} FROM {0} {2}"'.format(tblA, aSymbol, sJoin)
##    response = querySSA(query) # Query server
##    # Get list of SSA from response
##    if len(response)>0:
##        return [survey[0] for survey in response['Table']]
##    else:
##        message("No Soil Survey Area for {}".format(SSA))
##
##
##def getSurvey_date(SSA):
##    """Create SQL query for survey save date (saverest) using areasymbol (SSA)
##    """
##    where = "WHERE sacatalog.areasymbol = '{}'".format(SSA)
##    query = 'query: "SELECT saverest FROM sacatalog {}"'.format(where)
##    res = querySSA(query)
##    # Get date
##    if len(res)>0:
##        # Return date tuple in desired format (year, mo, da)
##        date = res['Table'][0][0].split(" ")[0].split("/")
##        return date[2], date[0].zfill(2), date[1].zfill(2)
##    else:
##        message("No {} for {}".format("survey", SSA))
##
##
##def getMUKEY_val(mukey, col, table = "Component"):
##    """SQl query a value from a column in a table based on a mukey"""
##    where = "WHERE {}.mukey = '{}'".format(table, mukey)
##    query = 'query: "SELECT {} FROM {} {}"'.format(col, table, where)
##    res = querySSA(query)
##    
##    # Get value
##    if len(res)>0:
##        # Return list of values
##        return [value[0] for value in res['Table']]
##        #return list(set([value[0] for value in res['Table']])) #unique
##    else:
##        message("No {} for {}".format(col, mukey))
