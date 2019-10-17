"""This utils package contains functions written using python based packages"""
import geopandas
import pyproj
import os


def geoList(shp):
    if not isinstance(shp, geopandas.geodataframe.GeoDataFrame):
        shp = geopandas.read_file(shp)
    return shp.geometry.to_json()


def json2shp(ret, outFC):
    """Write json response to .json test file and then read to DataFrame"""
    jsonFile = os.path.join(os.path.dirname(outFC), "tempjsonOutput.json")
    with open(jsonFile, "wb") as myJSON:
        myJSON.write(ret)
    gdf = geopandas.read_file(jsonFile, outFC)
    os.remove(jsonFile)
    return gdf


def shapeType(shp):
    if not isinstance(shp, geopandas.geodataframe.GeoDataFrame):
        shp = geopandas.read_file(shp)
    return "esriGeometry{}".format(shp.geom_type[0])


def getBoundingBox(shp):
    """Use geopandas library instead of arcpy
    param@fc should be a shapefile
    """
    if not isinstance(shp, geopandas.geodataframe.GeoDataFrame):
        shp = geopandas.read_file(shp)
    xmin = shp.bounds['minx'][0]
    xmax = shp.bounds['maxx'][0]
    ymin = shp.bounds['miny'][0]
    ymax = shp.bounds['maxy'][0]

    return [xmin, ymin, xmax, ymax]


def getCRS(shp):
    """Return EPSG for shapefile"""
    if not isinstance(shp, geopandas.geodataframe.GeoDataFrame):
        shp = geopandas.read_file(shp)
    return shp.crs['init'][5:]


def transform_pnt(pnt, inEPSG, outEPSG):
    """Uses pyproj (geopandas dependency)
    pnt is expected as x,y tuple
    inEPSG/outEPSG expected as factory code
    """
    x1, y1 = pnt[0], pnt[1] #added benefit of checking pnt format
    inProj = pyproj.Proj(init='epsg:{}'.format(inEPSG))
    outProj = pyproj.Proj(init='epsg:{}'.format(outEPSG))

    return pyproj.transform(inProj, outProj, x1, y1)


def transform_bBox(bBox, inEPSG, outEPSG):
    """Add function documentation"""
    pnt1 = (bBox[0], bBox[1])
    pnt1_out = transform_pnt(pnt1, inEPSG, outEPSG)
    pnt2 = (bBox[2], bBox[3])
    pnt2_out = transform_pnt(pnt2, inEPSG, outEPSG)

    return [pnt1_out[0], pnt1_out[1], pnt2_out[0], pnt2_out[1]]


def message(string):
    print(string)


def unique_values(df, field):
    """Unique Values
    Purpose: returns a list of unique field values from a dataframe column
    """
    return list(set(df[field]))


def append_shp(geoDFs):
    """Append inShapefile to outShapefile"""
    from pandas import concat

    assert(isinstance(geoDFs, list)), 'type list expected'
    assert len(geoDFs) > 1, 'more than one geodataframe expected'
    
    inCRS = getCRS(geoDFs[0])
    for df in geoDFs:
        assert getCRS(df) == inCRS, "Projections don't match"
    return geopandas.GeoDataFrame(concat(geoDFs,
                                         ignore_index=True), crs=inCRS)
    
#def clipRaster(raster, poly):
#"""Clip raster down to polygon geometry
#"""
#    import rasterio
#    import rasterio.mask
#    features = poly["geometry"]
#    with rasterio.open(raster) as src:
#        out_image, out_transform = rasterio.mask.mask(src, features, crop=True)
#        out_meta = src.meta.copy()
#
#    out_meta.update({"driver": "GTiff",
#                     "height": out_image.shape[1],
#                     "transform": out_transform})
#    with rasterio.open(raster, "w", **out_meta) as src_out:
#        src.write(out_image)
#
#
#def summarizeNLCD(poly, raster):
#"""Summarize raster land uses classes by percent in polygon geometry
#"""
#    import rasterstats
#
#    zonal = rasterstats.zonal_stats()
