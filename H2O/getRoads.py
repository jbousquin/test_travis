import requests
import geopandas
from os.path import join
from zipfile import ZipFile, is_zipfile

try:
    from H2O.utils import py as utils
except:
    from H2O.utils import arc as utils


def checkYear(year, years = None):
    """Run checks and formatting on year"""
    year = str(year) # coerce to string in case float() or int()
    assert year.isdigit(), "The year parameter must be numeric"
    if years:
        assert year in years, "The year {} is not available".format(year)
    return year


def checkArchive(archive):
    """Quickly return True if valid zip file"""
    return is_zipfile(archive)


def getArchive(response):
    from StringIO import StringIO #only used if no directory
    # Check zip is valid?
    #assert zipfile.is_zipfile(StringIO(response.content))
    # Unpack zip
    with ZipFile(StringIO(response.content), 'r') as archive:
        contents = archive.namelist()
        for f in contents:
            if f.endswith(".shp"):
                return geopandas.read_file(f)


def getRoads(FIP, directory = None, year = "2019"):
    """Download shapefile road lines by county
    """
    # Make sure year is usable   
    if int(year) <= 2008:
        years = ["1992", "1999", "2002", "2003",]
        year = checkYear(year, years)
    else:
        year = checkYear(year)
        assert int(year) < 2020, "Only available through 2019"

    # Make sure FIP is expected length
    assert len(FIP) == 5, "Problem with specified FIP: {}".format(FIP)

    # Source url
    url = "https://www2.census.gov/geo/tiger/TIGER{}/ROADS/".format(year)
    # Check url status
    if requests.get(url).status_code != 200:
        utils.message("Error: No web feature service at {}".format(url))

    # Create file name for county
    download = "tl_{}_{}_roads.zip".format(year, FIP)

    # Save zip to directory if specified
    if directory is not None:
        # Download zip file (stream = True may work better for larger files)
        res = requests.get(url + download)
        assert res.ok, "Problem with response from {}".format(url + download)
        # Save to directory
        out_file = join(directory, download)
        with open(out_file, "wb") as f:
            f.write(res.content)
            utils.message("Download Succeeded: {}".format(download))

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
