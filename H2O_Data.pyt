# -*- coding: utf-8 -*-
"""
Version: H2O pyt for arcGIS desktop

Author: Justin Bousquin
bousquin.justin@epa.gov

Description: Download NLCD data for Area of Interest extent
"""

import os
import arcpy
from H2O import getNLCD
from H2O import getFIPs
#from H2O import getRoads
from H2O import get303d


def message(msg, severity = 0):
    print(msg)
    if severity == 0: arcpy.AddMessage(msg)
    elif severity == 1: arcpy.AddWarning(msg)
    elif severity == 2: arcpy.AddError(msg)


def main(poly, outDIR):
    # Check outDIR
    if os.path.exists(outDIR):
        message("Replacing: {}".format(outDIR))
    os.makedirs(outDIR)
    # Create archive (D1) folder in outDIR
    pathD1 = os.path.join(outDIR, "D1")
    if not os.path.exists(pathD1):
        os.makedirs(pathD1)
    # Create workspace (D2) folder in outDIR
    pathD2 = os.path.join(outDIR, "D2")
    if not os.path.exists(pathD2):
        os.makedirs(pathD2)
        
    FIPS = getFIPs.polyFIPS(poly)
    #nlcd(FIPS, outDIR) #landuse and canopy
    getNLCD.getNLCD(poly, pathD2, dataset = "Land_Cover") # landuse
    getNLCD.getNLCD(poly, pathD2, dataset = "Tree_Canopy")
    #soils(FIPS, outDIR)
    #NHD(poly, outDIR)
    #for FIP in FIPS:
        #getRoads(FIP, outDIR)
    # Create gdb
    arcpy.CreateFileGDB_management(pathD2, "downloads.gdb")
    # 303d impairments
    shp_out = os.path.join(os.path.join(pathD2, "downloads.gdb"),
                           "impaired303d")
    inAOI = get303d.AOI(poly)
    get303d.get303D_byPoly(inAOI, shp_out)
    


class Toolbox(object):
    def __init__(self):
        self.label = "EPA H2O Data Generation"
        self.alias = "H2O Data"
        # List of tool classes associated with this toolbox
        self.tools = [H2O_Data]

class H2O_Data(object):
    def __init__(self):
        self.label = "Create database for AOI Polygon"
        self.description = "Download datasets required for assessment of " + \
                           "specified area of interest with EPA H2O."
        self.canRunInBackground = False

    def getParameterInfo(self):
        AOI = arcpy.Parameter()
        AOI.name = name = "inPoly"
        AOI.displayName = "Area of Interest"
        AOI.datatype = "DEFeatureClass"
        AOI.parameterType = "Required"
        AOI.direction = "Input"

        output = arcpy.Parameter()
        output.displayName = "Output Folder"
        output.name = "outDIR"
        output.datatype = "DEFolder"
        output.parameterType = "Required"
        output.direction = "Output"
        
        return [AOI, output]
    
    def isLicensed(self):
        return True
    def updateParameters(self, params):
        return
    def updateMessages(self, params):
        return

    def execute(self, params, messages):
        #try:
        poly = params[0].valueAsText
        #poly = r"C:\ArcGIS\Local_GIS\H2O\AOI\Monroe_Parish.shp"
        outDIR = params[1].valueAsText
        #outDIR = r"C:\ArcGIS\Local_GIS\H2O\testRun"
        main(poly, outDIR)
        #except:
