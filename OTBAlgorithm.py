# -*- coding: utf-8 -*-

"""
***************************************************************************
    OTBAlgorithm.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.parameters.ParameterTable import ParameterTable
from sextante.parameters.ParameterMultipleInput import ParameterMultipleInput
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.outputs.OutputRaster import OutputRaster
from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterBoolean import ParameterBoolean
from sextante.parameters.ParameterSelection import ParameterSelection
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils
from sextante.core.WrongHelpFileException import WrongHelpFileException
from sextante.parameters.ParameterFactory import ParameterFactory
from sextante.outputs.OutputFactory import OutputFactory
from sextante.otb.OTBUtils import OTBUtils
from sextante.parameters.ParameterExtent import ParameterExtent
import xml.etree.ElementTree as ET
import traceback
import inspect

class OTBAlgorithm(GeoAlgorithm):

    REGION_OF_INTEREST = "ROI"

    def __init__(self, descriptionfile):
        GeoAlgorithm.__init__(self)
        self.roiFile = None
        self.descriptionFile = descriptionfile
        self.defineCharacteristicsFromFile()
        self.numExportedLayers = 0
        self.hasROI = None;

    def getCopy(self):
        newone = OTBAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/../images/otb.png")

    def helpFile(self):
        folder = os.path.join(OTBUtils.otbDescriptionPath(), 'doc')
        helpfile = os.path.join( str(folder), self.appkey + ".html")
        if os.path.exists(helpfile):
            return helpfile
        else:
            raise WrongHelpFileException("Could not find help file for this algorithm. \nIf you have it put it in: \n"+str(folder))

    def adapt_list_to_string(self, c_list):
        a_list = c_list[1:]
        if a_list[0] in ["ParameterVector", "ParameterMultipleInput"]:
            if c_list[0] == "ParameterType_InputImageList":
                a_list[3] = 3
            else:
                a_list[3] = -1

        a_list[1]="-%s" % a_list[1]
        def mystr(par):
            if type(par) == type([]):
                return ";".join(par)
            return str(par)
        b_list = map(mystr, a_list)
        res = "|".join(b_list)
        return res

    def get_list_from_node(self, myet):
        all_params = []
        for parameter in myet.iter('parameter'):
            rebuild = []
            par_type = parameter.find('parameter_type').text
            key = parameter.find('key').text
            name = parameter.find('name').text
            source_par_type = parameter.find('parameter_type').attrib['source_parameter_type']
            rebuild.append(source_par_type)
            rebuild.append(par_type)
            rebuild.append(key)
            rebuild.append(name)
            for each in parameter[4:]:
                if not each.tag in ["hidden"]:
                    if len(each.getchildren()) == 0:
                        rebuild.append(each.text)
                    else:
                        rebuild.append([item.text for item in each.iter('choice')])
            all_params.append(rebuild)
        return all_params

    def defineCharacteristicsFromFile(self):
        content = open(self.descriptionFile).read()
        dom_model = ET.fromstring(content)

        self.appkey = dom_model.find('key').text
        self.cliName = dom_model.find('exec').text
        self.name = dom_model.find('longname').text
        self.group = dom_model.find('group').text
		
        SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Reading parameters... for %s" % self.appkey)

        rebu = None
        the_result = None

        try:
            rebu = self.get_list_from_node(dom_model)
            the_result = map(self.adapt_list_to_string,rebu)
        except Exception, e:
            SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open OTB algorithm: " + self.descriptionFile + "\n" + traceback.format_exc())
            raise e

        for line in the_result:
            try:
                if line.startswith("Parameter"):
                    param = ParameterFactory.getFromString(line)

                    # Hack for initializing the elevation parameters from Sextante configuration
                    if param.name == "-elev.dem.path":
                        param.default = OTBUtils.otbSRTMPath()
                    if param.name == "-elev.dem.geoid":
                        param.default = OTBUtils.otbGeoidPath()
                    self.addParameter(param)
                elif line.startswith("*Parameter"):
                    param = ParameterFactory.getFromString(line[1:])
                    param.isAdvanced = True
                    self.addParameter(param)
                elif line.startswith("Extent"):
                    self.addParameter(ParameterExtent(self.REGION_OF_INTEREST, "Region of interest", "0,1,0,1"))
                    self.hasROI = True
                else:
                    self.addOutput(OutputFactory.getFromString(line))
            except Exception,e:
                SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open OTB algorithm: " + self.descriptionFile + "\n" + line + "\n" + traceback.format_exc())
                raise e

    def processAlgorithm(self, progress):
        path = OTBUtils.otbPath()
        libpath = OTBUtils.otbLibPath()
        if path == "" or libpath == "":
            raise GeoAlgorithmExecutionException("OTB folder is not configured.\nPlease configure it before running OTB algorithms.")

        commands = []
        commands.append(path + os.sep + self.cliName)

        self.roiVectors = {}
        self.roiRasters = {}
        for param in self.parameters:
            if param.value == None or param.value == "":
                continue
            if isinstance(param, ParameterVector):
                commands.append(param.name)
                if self.hasROI:
                    roiFile = SextanteUtils.getTempFilename('shp')
                    commands.append(roiFile)
                    self.roiVectors[param.value] = roiFile
                else:
                    commands.append(param.value)
            if isinstance(param, ParameterRaster):
                commands.append(param.name)
                if self.hasROI:
                    roiFile = SextanteUtils.getTempFilename('tif')
                    commands.append(roiFile)
                    self.roiRasters[param.value] = roiFile
                else:
                    commands.append(param.value)
            elif isinstance(param, ParameterMultipleInput):
                commands.append(param.name)
                commands.append(str(param.value.replace(";"," ")))
            elif isinstance(param, ParameterSelection):
                commands.append(param.name)
                idx = int(param.value)
                commands.append(str(param.options[idx]))
            elif isinstance(param, ParameterBoolean):
                if param.value:
                    commands.append(param.name)
                    commands.append(str(param.value).lower())
            elif isinstance(param, ParameterExtent):
                self.roiValues = param.value.split(",")
            else:
                commands.append(param.name)
                commands.append(str(param.value))

        for out in self.outputs:
            commands.append(out.name)
            commands.append(out.value)
        for roiInput, roiFile in self.roiRasters.items():
            startX, startY = float(self.roiValues[0]), float(self.roiValues[1])
            sizeX = float(self.roiValues[2]) - startX
            sizeY = float(self.roiValues[3]) - startY
            helperCommands = [
                    "otbcli_ExtractROI",
                    "-in",       roiInput,
                    "-out",      roiFile,
                    "-startx",   str(startX),
                    "-starty",   str(startY),
                    "-sizex",    str(sizeX),
                    "-sizey",    str(sizeY)]
            SextanteLog.addToLog(SextanteLog.LOG_INFO, helperCommands)
            progress.setCommand(helperCommands)
            OTBUtils.executeOtb(helperCommands, progress)

        if self.roiRasters:
            supportRaster = self.roiRasters.itervalues().next()
            for roiInput, roiFile in self.roiVectors.items():
                helperCommands = [
                        "otbcli_VectorDataExtractROIApplication",
                        "-vd.in",           roiInput,
                        "-io.in",           supportRaster,
                        "-io.out",          roiFile,
                        "-elev.dem.path",   OTBUtils.otbSRTMPath()]
                SextanteLog.addToLog(SextanteLog.LOG_INFO, helperCommands)
                progress.setCommand(helperCommands)
                OTBUtils.executeOtb(helperCommands, progress)

        loglines = []
        loglines.append("OTB execution command")
        for line in commands:
            loglines.append(line)
            progress.setCommand(line)

        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)
        import sextante.otb.OTBSpecific
        module = sextante.otb.OTBSpecific

        found = False
        if 'adapt%s' % self.appkey in dir(module):
            found = True
            commands = getattr(module, 'adapt%s' % self.appkey)(commands)
        else:
            the_key = 'adapt%s' % self.appkey
            if '-' in the_key:
                base_key = the_key.split("-")[0]
                if base_key in dir(module):
                    found = True
                    commands = getattr(module, base_key)(commands)

        if not found:
            SextanteLog.addToLog(SextanteLog.LOG_INFO, "Adapter for %s not found" % the_key)

        frames = inspect.getouterframes(inspect.currentframe())[1:]
        for a_frame in frames:
            frame,filename,line_number,function_name,lines,index= a_frame
            SextanteLog.addToLog(SextanteLog.LOG_INFO, "%s %s %s %s %s %s" % (frame,filename,line_number,function_name,lines,index))
    
        OTBUtils.executeOtb(commands, progress)
