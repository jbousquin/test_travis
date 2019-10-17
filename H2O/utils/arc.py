"""This utils package contains functions written using arcpy based packages"""
import arcpy
import os

def geoList(shp):
    return [geo[0].JSON for geo in arcpy.da.SearchCursor(shp, ['SHAPE@'])]


def json2shp(ret, outFC):
    """Write json text to .json file and then convert to shapefile"""
    gdb = os.path.dirname(outFC)
    jsonFile = os.path.join(os.path.dirname(gdb), "tempjsonOutput.json")
    with open(jsonFile, "wb") as myJSON:
        myJSON.write(ret)
    arcpy.JSONToFeatures_conversion(jsonFile, outFC)
    os.remove(jsonFile)


def shapeType(shp):
    shapeType = arcpy.Describe(shp).shapeType
    return "esriGeometry{}".format(shapeType)


def getBoundingBox(fc):
    """Returns dataset extent envelope"""
    desc = arcpy.Describe(fc)
    xmin = desc.extent.XMin
    xmax = desc.extent.XMax
    ymin = desc.extent.YMin
    ymax = desc.extent.YMax

    return [xmin, ymin, xmax, ymax]


def getCRS(fc):
    """ Returns spatial reference factory code, GCS - WGS 1984 by default"""
    desc = arcpy.Describe(fc)
    code = desc.spatialReference.factoryCode
    if code == 0: # if 0 -> 4326 Geographic Coordinate system "WGS 1984"
        #project? going to be harder without CRS
        code = 4326
    return code


def transform_pnt(pnt, inEPSG, outEPSG):
    """pnt is expected as x,y tuple
    inEPSG/outEPSG expected as factory code
    """
    # Create point geometry
    pt = arcpy.Point()
    pt.X, pt.Y = pnt[0], pnt[1]
    # Manage CRS
    in_CRS = arcpy.SpatialReference(inEPSG)
    out_CRS = arcpy.SpatialReference(outEPSG)
    # Manage transform method for CRS -> CRS
    transforms = arcpy.ListTransformations(in_CRS, out_CRS)
    # Try to ignore any custom tranformations
    new = "New Geographic Transformation"
    transforms = [trans for trans in transforms if not trans.endswith(new)]
    if len(transforms) > 0:
        trans = transforms[0] # first is default
    else:
        trans = '' # problem?
    # Do transform
    ptgeoIn = arcpy.PointGeometry(pt, in_CRS) # assign CRS to point geometry
    ptgeoOut = ptgeoIn.projectAs(out_CRS, trans)
    pt_out = ptgeoOut.lastPoint
    assert pt_out != None, "Error projecting {} from {} to {}".format(pnt,
                                             inEPSG, outEPSG)
    return (pt_out.X, pt_out.Y)


def transform_bBox(bBox, inEPSG, outEPSG):
    """Add function documentation"""
    pnt1 = (bBox[0], bBox[1])
    pnt1_out = transform_pnt(pnt1, inEPSG, outEPSG)
    pnt2 = (bBox[2], bBox[3])
    pnt2_out = transform_pnt(pnt2, inEPSG, outEPSG)

    return [pnt1_out[0], pnt1_out[1], pnt2_out[0], pnt2_out[1]]


def message(msg, severity = 0):
    print(msg)
    if severity == 0: arcpy.AddMessage(msg)
    elif severity == 1: arcpy.AddWarning(msg)
    elif severity == 2: arcpy.AddError(msg)


def unique_values(table, field):
    """Unique Values
    Purpose: returns a sorted list of unique values
    Notes: used to find unique field values in table column
    """
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor if row[0]})


def append_shp(inShapefile, outShapefile):
    """Append inShapefile to outShapefile"""
    if os.path.isfile(outShapefile):
        try:
            arcpy.Append_management(inShapefile, outShapefile, "NO_TEST")
        except Exception:
            message("Could not perform append.")
    else:
        message("Specified file {} does not exist!".format(outShapefile))
