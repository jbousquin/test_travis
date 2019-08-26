import os
import requests
from H2O.utils import py as utils
from json import loads


def strReq(url, data):
    """Use requests lib to print url server request"""
    return requests.Request('GET', url, params=data).prepare().url


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
    assert res.ok, "Problem with Soil response: {}".format(strReq(url, data))

    # Write response to directory if provided
    if directory is not None:    
        out_file = os.path.join(directory, "SSA_soils.gml")
        with open(out_file, "wb") as f:
            f.write(res.content)


def getSoil_FIP(FIP, directory = None):
    "Download soils data by FIP"""
    # Figure out survey file name
    SSA_list = getCounty_surveys(FIP) # Get list of SSA for FIP
    # List of dataframes for each SSA
    dfs = [getDF_SSA(SSA, directory) for SSA in SSA_list]

    # Concatenate dataframes if more than 1
    if len(dfs) >1:    
        df = utils.append_shp(dfs)

    # Remove unwanted fields
    delete_fields = ["AREASYMBOL", "SPATIALVER", "MUSYM"]
    for field in fields:
        df = df.drop[field]
    
    # Get "hydgrp" by mukey to populate "Max_Type_N" field
    mukey_list = utils.unique_values(df, "MUKEY") # Unique mukey list

    # Create dictionary where mukey:first hydrgrps
    soil_dict = {key: getMUKEY_val(key, "hydgrp")[0] for key in mukey_list}
    # Reduce dual soil hydrgrps to first, leaving None as None
    soil_dict = {k:None if v == None else v[0] for (k,v) in  soil_dict.items()}

    # Dictionary lookup for soil class -> Max_Type_N
    max_n_lookup = {"A": 1, "B": 2, "C": 3, "D": 4, None: 0}

    # Update Max_Type_N field using soil dictionary
    # Add Max_Type_N field
    df['Max_Type_N'] = df["MUKEY"].map(max_n_lookup)

    # Drop NaN or 0 rows


def getDF_SSA(SSA, directory = None):        
     # Source url
    url = "https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/"
    # Check url status
##    if requests.get(url).status_code != 200:
##        utils.message("Error: No web feature service at {}".format(url))       
    year, mo, da = getSurvey_date(SSA) # Get latest saverest
    download = "wss_SSA_{}_[{}-{}-{}].zip".format(SSA, year, mo, da)

    # Save zip to directory if specified
    if directory is not None:
        # Download SSA
        res = requests.get(url + download)
        assert res.ok, "Problem with response from {}".format(url + download)
        out_file = join(directory, download) # Save to directory
        with open(out_file, "wb") as f:
            f.write(res.content)

        # Check & unpack archive
        assert checkArchive(out_file), "Bad zipfile"
        with ZipFile(out_file) as archive:
            archive.extractall(directory)
        shp = download[:-3] + "shp"
        df = geopandas.read_file(join(directory, shp))

    else:
        # Read url directly to geopandas
        df = geopandas.read_file(url + download)
    return df


def getCounty_surveys(FIP):
    """Create SQL query for survey areasymbol (SSA) based on formated FIP"""
    # Survey area from FIP
    SSA = "{}{}".format(FIP_2_abbr(FIP), FIP[2:5])
    # SQL params
    tblA = "legend" # Legend table
    tblB = "laoverlap" # Legend Area Overlap Table
    aSymbol = "areasymbol" # Area symbol field name used in both tables
    cond1 = "{}.lkey = {}.lkey".format(tblA, tblB) # lkey = lkey
    cond2 = "{}.{} = '{}'".format(tblB, aSymbol, SSA) # areasymbol = SSA
    sJoin = "INNER JOIN {} ON {} AND {}".format(tblB, cond1, cond2)
    query = "SELECT {0}.{1} FROM {0} {2}".format(tblA, aSymbol, sJoin)
            
    response = querySSA(query) # Query server
    
    # Get list of SSA from response
    if len(response)>0:
        return [survey[0] for survey in response['Table']]
    else:
        message("No Soil Survey Area for {}".format(SSA))


def querySSA(query):
    """Do SQL query on NRCS tabular service
    Test SQL at https://sdmdataaccess.nrcs.usda.gov/Query.aspx"""
    
    # Source url
    url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/SDMTabularService/post.rest"
    # Check url status
##    if requests.get(url).status_code != 200:
##        utils.message("Error: No web feature service at {}".format(url)) 

    # Create params dict
    data = {'query': query,
            'format': "JSON"
            }

    # Get response
    res = requests.post(url, data)
    assert res.ok, "Problem with Soil response: {}".format(strReq(url, data))
    
    return loads(res.content)


def getSurvey_date(SSA):
    """Create SQL query for survey save date (saverest) using areasymbol (SSA)
    """
    where = "WHERE sacatalog.areasymbol = '{}'".format(SSA)
    query = "SELECT saverest FROM sacatalog {}".format(where)
    response = querySSA(query) # Query server
    # Get date from response
    if len(response)>0:
        # Return date tuple in desired format (year, mo, da)
        date = response['Table'][0][0].split(" ")[0].split("/")
        return date[2], date[0].zfill(2), date[1].zfill(2)
    else:
        message("No survey for {}".format(SSA))


def getMUKEY_val(mukey, col, table = "Component"):
    """SQl query a value from a column in a table based on a mukey"""
    where = "WHERE {}.mukey = '{}'".format(table, mukey)
    query = 'query: "SELECT {} FROM {} {}"'.format(col, table, where)
    res = querySSA(query)
    
    # Get value
    if len(res)>0:
        # Return list of values
        return [value[0] for value in res['Table']]
        #return list(set([value[0] for value in res['Table']])) #unique
    else:
        message("No {} for {}".format(col, mukey))


def FIP_2_abbr(FIP):
    return state_dict()[FIP[:2]][0]


def state_dict():
    """Construct distionary of states where:
        key = FIP
        value[0] = Abbreviation
        value[1] = AWS state name
    Notes: this is static so the end user can change scope more easily
    """
    states = {'01':['AL', 'Alabama'],
              '53':['WA', 'Washington'],
              '55':['WI', 'Wisconsin'],
              '54':['WV', 'West_Virginia'],
              '12':['FL', 'Florida'],
              '56':['WY', 'Wyoming'],
              '33':['NH', 'New_Hampshire'],
              '34':['NJ', 'New_Jersey'],
              '35':['NM', 'New_Mexico'],
              '37':['NC', 'North_Carolina'],
              '38':['ND', 'North_Dakota'],
              '31':['NE', 'Nebraska'],
              '36':['NY', 'New_York'],
              '44':['RI', 'Rhode_Island'],
              '32':['NV', 'Nevada'],
              '08':['CO', 'Colorado'],
              '06':['CA', 'California'],
              '13':['GA', 'Georgia'],
              '09':['CT', 'Connecticut'],
              '40':['OK', 'Oklahoma'],
              '39':['OH', 'Ohio'],
              '20':['KS', 'Kansas'],
              '45':['SC', 'South_Carolina'],
              '21':['KY', 'Kentucky'],
              '41':['OR', 'Oregon'],
              '46':['SD', 'South_Dakota'],
              '10':['DE', 'Delaware'],
              '15':['HI', 'Hawaii'],
              '48':['TX', 'Texas'],
              '22':['LA', 'Louisiana'],
              '47':['TN', 'Tennessee'],
              '42':['PA', 'Pennsylvania'],
              '51':['VA', 'Virginia'],
              '02':['AK', 'Alaska'],
              '05':['AR', 'Arkansas'],
              '50':['VT', 'Vermont'],
              '17':['IL', 'Illinois'],
              '18':['IN', 'Indiana'],
              '19':['IA', 'Iowa'],
              '04':['AZ', 'Arizona'],
              '16':['ID', 'Idaho'],
              '23':['ME', 'Maine'],
              '24':['MD', 'Maryland'],
              '25':['MA', 'Massachusetts'],
              '49':['UT', 'Utah'],
              '29':['MO', 'Missouri'],
              '27':['MN', 'Minnesota'],
              '26':['MI', 'Michigan'],
              '30':['MT', 'Montana'],
              '28':['MS', 'Mississippi']
              }
    return states
