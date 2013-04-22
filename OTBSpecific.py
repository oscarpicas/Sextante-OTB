# -*- coding: utf-8 -*-

"""
***************************************************************************
    OTBSpecific.py
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import sys

try:
    import sextante
except ImportError, e:
    raise Exception("Sextante must be installed and available in PYTHONPATH")

try:
    import otbApplication
except ImportError, e:
    raise Exception("OTB python plugins must be installed and available in PYTHONPATH")

import otbApplication

import xml.etree.ElementTree as ET
import traceback

import logging

from sextante.otb.OTBUtils import *

def getBinaryMorphologicalOperation(available_app, original_dom_document):
    the_root = original_dom_document
    remove_dependant_choices(the_root, 'structype', 'ball')
    remove_other_choices(the_root, 'structype', 'ball')
    remove_dependant_choices(the_root, 'filter', 'dilate')
    remove_parameter_by_key(the_root, 'structype.ball.yradius')
    defaultWrite(available_app, the_root)
    return [the_root]

def adaptBinaryMorphologicalOperation(commands_list):
    val = commands_list[commands_list.index("-filter") + 1]

    def replace_dilate(param, value):
        if ".dilate" in str(param):
            return param.replace("dilate", value)
        else:
            return param

    import functools
    com_list = map(functools.partial(replace_dilate, value=val), commands_list)

    val = com_list[com_list.index("-structype.ball.xradius") + 1]

    pos = com_list.index("-structype.ball.xradius") + 2

    com_list.insert(pos, '-structype.ball.yradius')
    com_list.insert(pos + 1, val)

    return com_list

def getEdgeExtraction(available_app, original_dom_document):
    the_root = original_dom_document
    remove_parameter_by_key(the_root, 'filter.touzi.yradius')
    splitted = split_by_choice(the_root, 'filter')
    the_list = []
    for key in splitted:
        defaultWrite('%s-%s' % (available_app, key), splitted[key])
        the_list.append(splitted[key])
    return the_list

def adaptEdgeExtraction(commands_list):
    val = commands_list[commands_list.index("-filter") + 1]
    if val == 'touzi':
        bval = commands_list[commands_list.index("-filter.touzi.xradius") + 1]
        pos = commands_list.index("-filter.touzi.xradius") + 2
        commands_list.insert(pos, "-filter.touzi.yradius")
        commands_list.insert(pos + 1, bval)
    return commands_list

def getGrayScaleMorphologicalOperation(available_app, original_dom_document):
    the_root = original_dom_document
    remove_dependant_choices(the_root, 'structype', 'ball')
    remove_other_choices(the_root, 'structype', 'ball')
    remove_parameter_by_key(the_root, 'structype.ball.yradius')
    defaultWrite(available_app, the_root)
    return [the_root]

def adaptGrayScaleMorphologicalOperation(commands_list):
    val = commands_list[commands_list.index("-structype.ball.xradius") + 1]
    pos = commands_list.index("-structype.ball.xradius") + 2
    commands_list.insert(pos, "-structype.ball.yradius")
    commands_list.insert(pos + 1, val)
    return commands_list

def getDimensionalityReduction(available_app, original_dom_document):
    the_root = original_dom_document
    splitted = split_by_choice(the_root, 'method')
    the_list = []
    for key in splitted:
        if key == 'maf':
            the_doc = splitted[key]
            remove_parameter_by_key(the_doc, 'outinv')
            defaultWrite('%s-%s' % (available_app, key), the_doc)
            the_list.append(the_doc)
        else:
            defaultWrite('%s-%s' % (available_app, key), splitted[key])
            the_list.append(splitted[key])
    return the_list

def getPansharpening(available_app, original_dom_document):
    the_root = original_dom_document
    splitted = split_by_choice(the_root, 'method')
    the_list = []
    for key in splitted:
        defaultWrite('%s-%s' % (available_app, key), splitted[key])
        the_list.append(splitted[key])
    return the_list

def getPixelValue(available_app, original_dom_document):
    the_root = original_dom_document
    remove_parameter_by_key(the_root, 'cl')
    defaultWrite(available_app, the_root)
    return [the_root]

def getExtractROI(available_app, original_dom_document):
    the_root = original_dom_document
    remove_parameter_by_key(the_root, 'cl')
    defaultWrite(available_app, the_root)
    return [the_root]

def getQuicklook(available_app, original_dom_document):
    the_root = original_dom_document
    remove_parameter_by_key(the_root, 'cl')
    defaultWrite(available_app, the_root)
    return [the_root]

def getRigidTransformResample(available_app, original_dom_document):
    the_root = original_dom_document
    splitted = split_by_choice(the_root, 'transform.type')
    the_list = []
    for key in splitted:
        defaultWrite('%s-%s' % (available_app, key), splitted[key])
        the_list.append(splitted[key])
    return the_list

def getHomologousPointsExtraction(available_app, original_dom_document):
    the_list = defaultSplit(available_app, original_dom_document, 'mode')
    return the_list

def getGenerateRPCSensorModel(available_app, original_dom_document):
    the_root = original_dom_document
    remove_dependant_choices(the_root, 'map', 'wgs')
    remove_other_choices(the_root, 'map', 'wgs')
    defaultWrite(available_app, the_root)
    return [the_root]

def getRefineSensorModel(available_app, original_dom_document):
    the_root = original_dom_document
    remove_dependant_choices(the_root, 'map', 'wgs')
    remove_other_choices(the_root, 'map', 'wgs')
    defaultWrite(available_app, the_root)
    return [the_root]

def getSegmentation(available_app, original_dom_document):
    the_root = original_dom_document
    remove_choice(the_root, 'filter', 'edison')
    remove_independant_choices(the_root, 'filter', 'edison')
    remove_choice(the_root, 'filter', 'meanshift')
    remove_independant_choices(the_root, 'filter', 'meanshift')
    remove_choice(the_root, 'mode', 'raster')
    remove_independant_choices(the_root, 'mode', 'raster')
    splitted = split_by_choice(the_root, 'filter')
    the_list = []
    for key in splitted:
        defaultWrite('%s-%s' % (available_app, key), splitted[key])
        the_list.append(splitted[key])
    return the_list

def getKMeansClassification(available_app, original_dom_document):
    the_root = original_dom_document
    remove_parameter_by_key(the_root, 'rand')
    defaultWrite(available_app, the_root)
    return [the_root]

def getTrainSVMImagesClassifier(available_app, original_dom_document):
    the_root = original_dom_document
    remove_parameter_by_key(the_root, 'rand')
    defaultWrite(available_app, the_root)
    return [the_root]

def getComputeConfusionMatrix(available_app, original_dom_document):
    the_root = original_dom_document
    remove_independant_choices(the_root, 'ref', 'vector')
    remove_choice(the_root, 'ref', 'vector')
    defaultWrite(available_app, the_root)
    return [the_root]

def getOpticalCalibration(available_app, original_dom_document):
    the_list = defaultSplit(available_app, original_dom_document, 'level')
    return the_list

def getSarRadiometricCalibration(available_app, original_dom_document):
    # TODO ** before doing anything, check support for SAR data in Qgis
    the_root = original_dom_document
    defaultWrite(available_app, the_root)
    return [the_root]
    
def getSmoothing(available_app, original_dom_document):
    import copy
    the_root = copy.deepcopy(original_dom_document)
    remove_dependant_choices(the_root, 'type', 'anidif')
    remove_other_choices(the_root, 'type', 'anidif')
    defaultWrite('%s-anidif' % available_app, the_root)

    the_root = copy.deepcopy(original_dom_document)
    remove_independant_choices(the_root, 'type', 'anidif')
    remove_choice(the_root, 'type', 'anidif')
    defaultWrite(available_app, the_root)
    return [the_root]
