"""This utils package contains functions written using python based packages"""
import geopandas
import pyproj


def getBoundingBox(shp):
    """Use geopandas library instead of arcpy
    param@fc should be a shapefile
    """
    #shp = geopandas.read_file(fc)
    xmin = shp.bounds['minx'][0]
    xmax = shp.bounds['maxx'][0]
    ymin = shp.bounds['miny'][0]
    ymax = shp.bounds['maxy'][0]

    return [xmin, ymin, xmax, ymax]


def getCRS(shp):
    """Return EPSG for shapefile"""
    #shp = geopandas.read_file(fc)
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
    pnt1 = (bBox[0], bBox[2])
    pnt1_out = transform_pnt(pnt1, inEPSG, outEPSG)
    pnt2 = (bBox[1], bBox[3])
    pnt2_out = transform_pnt(pnt2, inEPSG, outEPSG)

    return [pnt1_out[0], pnt2_out[0], pnt1_out[1], pnt2_out[1]]


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
