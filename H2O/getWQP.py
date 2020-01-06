import requests
import os
import pandas
from zipfile import ZipFile, is_zipfile

try:
    from H2O.utils import py as utils
except:
    from H2O.utils import arc as utils

def message(s):
    """Print s"""
    #AddMessage(str(s))
    print(str(s))


def strReq(url, data):
    """Use requests lib to print url server request"""
    return requests.Request('GET', url, params=data).prepare().url


def checkArchive(archive):
    """Quickly return True if valid zip file"""
    return is_zipfile(archive)


def byFIP(FIP, data={}, directory=None):
    """Use FIP code to limit exent of data from water quality portal
    """
    #'12033'
    # Check and format request from FIP
    FIP = str(FIP)
    assert len(FIP) in [2,5], "Problem with specified FIP: {}".format(FIP)
    
    data['countrycode'] = 'US'
    data['statecode'] = 'US:{}'.format(FIP[:2])
    if len(FIP) == 5:
        data['countycode'] = 'US:{}:{}'.format(FIP[:2], FIP[2:])

    # get request using data
    getWQP(data, directory, FIP)


def byBBox(bBox, data={}, directory=None):
    """Use Bounding Box to limit exent of data from water quality portal
    """
    # Reformat order to string where W-S-E-N (minX, minY, maxX, maxY)
    if isinstance(bBox, list):
        assert len(bBox) == 4, 'Bad Bounding Box'
        bBox = ','.join(map(str, bBox))
    #bBox='-88.967285,29.346270,-85.498352,31.393502'
    data['bBox'] = bBox

    # get request using data
    getWQP(data, directory, "bBox")


def getWQP(params, directory, name):
    # Copy dict to avoid in-place changes
    data = params
    
    # Pull dataTable from data
    if 'dataTable' in data.keys():
        table = data['dataTable']
        del data['dataTable']
    else:
        table = 'Station'
        
    # Standard Params
    data['mimeType'] = 'csv'
    data['zip'] = 'yes'

    # Source url
    url = "https://www.waterqualitydata.us/data/{}/search".format(table)
    
    # Check url status
    if requests.get(url).status_code != 200:
        statusCode = requests.get(url).status_code
        message("Warning: {} web service response {}".format(url, statusCode))
    message(data)
    res = requests.get(url, data)
    assert res.ok, "Problem with response from {}".format(strReq(url, data))

    if directory is not None:
        download = os.path.join(directory, 'wqp_{}_{}.zip'.format(table, name))

        # Save to directory
        with open(download, "wb") as f:
            f.write(res.content)
            message("Download Succeeded: {}".format(download))

        # Check & unpack archive
        assert checkArchive(download), "Bad zipfile"
        with ZipFile(download) as archive:
            archive.extractall(directory)


def dataTableDictWQP():
    return {'Organizational Data': 'Organization',
            'Site Data': 'Station',
            'Project Data': 'Project',
            'Project Weighting Data': 'ProjectMonitoringLocationWeighting',
            'Sample Results': 'Result',
            'Sampling Activity': 'Activity',
            'Sampling Activity Metrics': 'ActivityMetric',
            'Result Detection Limit': 'ResultDetectionQuantitationLimit',
            'Biological Habitat Metrics':'BiologicalMetric',
            }


def characteristicName(c):
    """ Notes:
    'oxygen' characteristic (NWIS/STORET) is actually dissolved oxygen
    'Temperature' characteristic is void of data (left in just in case)
    'pH' (STEWARDS ) is also without data (left in just in case)
    
    """
    #pretest values to be no spaces and lowercase
    #            'Nitrate-Nitrogen': ['nitrate-nitrogen', 'nitrogen-nitrate',
    #                             'nitrogen-all',],
    #        'Nitrogen': ['nitrogen'],
    #        'Nitrogen-15': ['nitrogen-15', 'nitrogen-all',],
    #        'Nitrogen ion': ['nitrogenion', 'nitrogen-all',],
    c = c.replace(" ", "")
    c = c.replace("'", "")
    c = c.lower()
    cDict = {'Depth': ['depth',],
             'Salinity': ['salinity',],
             'Temperature, water' : ['tempreature',],
             'Temperature': ['temperature',],
             'Turbidity': ['turbidity', 'clarity-all',],
             'Total suspended solids': ['totalsuspendedsolids', 'clarity-all',],
             'Total Suspended Particulate Matter':['clarity-all',],
             'Secchi depth': ['secchi-all', 'clarity-all', 'sechidepth',],
             'Horizontal Secchi Disk': ['horizontalsecchidisk',
                                        'secchi-all', 'clarity-all',],
             'Depth, Secchi disk depth': ['depth,secchidiskdepth',
                                          'secchi-all', 'clarity-all',],
             'Secchi, Horizontal Distance': ['secchi,horizontaldistance',
                                             'secchi-all', 'clarity-all',],
             'Water transparency, Secchi disc': ['watertransparency,secchidisc',
                                                 'secchi-all', 'clarity-all',],
             'Transparency, Secchi tube with disk': ['transparency,secchitubewithdisk',
                                                     'secchi-all', 'clarity-all',],
             'Depth, Secchi disk depth (choice list)': ['depth,secchidiskdepth(choicelist)',
                                                        'secchi-all', 'clarity-all',],
             'Secchi Reading Condition (choice list)': ['secchireadingcondition(choicelist)',
                                                        'secchi-all', 'clarity-all',],
             'pH': ['ph',],
             'PH': ['ph',],
             'Oxygen': ['dissolvedoxygen-all', 'oxygen'],
             'Dissolved Oxygen': ['dissolvedoxygen-all', 'dissolvedoxygen'],
             'Dissolved oxygen': ['dissolvedoxygen-all', 'dissolvedoxygen'],
             'Dissolved oxygen (DO)': ['dissolvedoxygen-all',
                                       'dissolvedoxygen(do)',],
             'Dissolved oxygen saturation': ['dissolvedoxygen-all',
                                             'dissolvedoxygensaturation',],
             'Ammonia-nitrogen': ['ammonia-nitrogen', 'nitrogen-ammonia',
                                  'nitrogen-all',],
             'Organic Nitrogen': ['organicnitrogen', 'nitrogen-all',],
             'Chlorophyll a, uncorrected for pheophytin': ['chlorophylla',
                                                           'chlorophyll-all',],
            }
    cList = [i[0] for i in cDict.items() if c in i[1]]
    return {'characteristicName': cList}


def orgLimit(s):
    if isinstance(s, list):
        for item in s:
            assert isinstance(item, str), 'item not string'
        return {'organization': s}
    else:
        return {'organization': str(s)}


def dateLimit(date):
    """Take different dates and format into expected parameter."""
    return date


def stationPoints(csv, outEPSG = 4326):
    #outEPSG = 4326
    latCol, lonCol = 'LatitudeMeasure', 'LongitudeMeasure'
    crsCol = 'HorizontalCoordinateReferenceSystemDatumName'
    cols = ['OrganizationIdentifier', 'OrganizationFormalName',
            'MonitoringLocationIdentifier', 'MonitoringLocationTypeName',
            latCol, lonCol, crsCol, 'ProviderName']
    df = pandas.read_csv(csv)
    df = df.filter(items=cols)
#    
#    for crs in set(df[crsCol]):
#        if crs in crsdict().keys():
#            sub_df = df[df[crsCol]==crs]
#            inEPSG = crsdict()[crs]
#            sub_df['lat_lon'] = transDFpoint(sub_df, latCol, lonCol, inEPSG, outEPSG)

    df['lat'] = 0.0
    df['lon'] = 0.0
    
    for i in df.index:
        if df.loc[i, crsCol] in list(crsdict()):
            inEPSG = crsdict()[df.loc[i, crsCol]]
            lat_lon = transSeries(df.loc[i], latCol, lonCol, inEPSG, outEPSG)
            df.loc[i, 'lat'] = lat_lon[0]
            df.loc[i, 'lon'] = lat_lon[1]
    return df


def transDFpoint(df, latCol, lonCol, inEPSG, outEPSG):
    """Transform all points in columns of dataframe"""
    pnts = [(a,b) for a,b in zip(df[latCol], df[lonCol])]
    return [utils.transform_pnt(pnt, inEPSG, outEPSG) for pnt in pnts]


def transSeries(series, latCol, lonCol, inEPSG, outEPSG):
    """Transform point in series"""
    return utils.transform_pnt((series[latCol], series[lonCol]), inEPSG, outEPSG)


def crsdict():
    return {'NAD27': 4267, 'NAD83': 4269, 'WGS84': 4326,}

    
#directory=r'L:\Priv\Ecological Suitability Research\SSWR\Data\WQP\bBox_default'
##for val in dataTableDictWQP().values():
##	data['dataTable'] = val
##	if val not in ['ProjectMonitoringLocationWeighting',
##                       'ResultDetectionQuantitationLimit',
##                       'Activity']:
##            byBBox(bBox, data, directory)
