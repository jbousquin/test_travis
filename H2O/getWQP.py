import requests
import os
from zipfile import ZipFile, is_zipfile

try:
    from H2O.utils import py as utils
except:
    from H2O.utils import arc as utils


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
        utils.message("Error: No web feature service at {}".format(url))

    res = requests.get(url, data)
    assert res.ok, "Problem with response from {}".format(url)

    if directory is not None:
        download = os.path.join(directory, 'wqp_{}_{}.zip'.format(table, name))

        # Save to directory
        with open(download, "wb") as f:
            f.write(res.content)
            utils.message("Download Succeeded: {}".format(download))

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


def characteristicNameList():
    return ['Salinity']


#directory=r'L:\Priv\Ecological Suitability Research\SSWR\Data\WQP\bBox_default'
for val in dataTableDictWQP().values():
	data['dataTable'] = val
	if val not in ['ProjectMonitoringLocationWeighting',
                       'ResultDetectionQuantitationLimit',
                       'Activity']:
            byBBox(bBox, data, directory)
