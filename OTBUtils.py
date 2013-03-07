# -*- coding: utf-8 -*-

"""
***************************************************************************
    OTBUtils.py
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
import subprocess
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils
import logging
import xml.etree.ElementTree as ET
import traceback

class OTBUtils:

    OTB_FOLDER = "OTB_FOLDER"
    OTB_LIB_FOLDER = "OTB_LIB_FOLDER"
    OTB_SRTM_FOLDER = "OTB_SRTM_FOLDER"
    OTB_GEOID_FILE = "OTB_GEOID_FILE"

    @staticmethod
    def otbPath():
        folder = SextanteConfig.getSetting(OTBUtils.OTB_FOLDER)
        if folder == None:
            folder = ""

            if os.path.exists("/usr/bin/otbcli"):
                folder = "/usr/bin"
        return folder

    @staticmethod
    def otbLibPath():
        folder = SextanteConfig.getSetting(OTBUtils.OTB_LIB_FOLDER)
        if folder == None:
            folder =""

            linuxstandardpath = "/usr/lib/otb/applications"
            if os.path.exists(linuxstandardpath):
                folder = linuxstandardpath
        return folder

    @staticmethod
    def otbSRTMPath():
        folder = SextanteConfig.getSetting(OTBUtils.OTB_SRTM_FOLDER)
        if folder == None:
            folder =""
        return folder

    @staticmethod
    def otbGeoidPath():
        filepath = SextanteConfig.getSetting(OTBUtils.OTB_GEOID_FILE)
        if filepath == None:
            filepath =""
        return filepath

    @staticmethod
    def otbDescriptionPath():
        return os.path.join(os.path.dirname(__file__), "description")

    @staticmethod
    def executeOtb(commands, progress):
        loglines = []
        loglines.append("OTB execution console output")
        os.putenv('ITK_AUTOLOAD_PATH', OTBUtils.otbLibPath())
        fused_command = ''.join(['"%s" ' % c for c in commands])
        proc = subprocess.Popen(fused_command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            if "[*" in line:
                idx = line.find("[*")
                perc = int(line[idx-4:idx-2].strip(" "))
                if perc !=0:
                    progress.setPercentage(perc)
            else:
                loglines.append(line)
                progress.setConsoleInfo(line)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)

def get_choices_of(doc, parameter):
    choices = []
    try:
        t5 = [item for item in doc.findall('.//parameter') if item.find('key').text == parameter]
        choices = [item.text for item in t5[0].findall('options/choices/choice')]
    except:
        logger = logging.getLogger('OTBGenerator')
        logger.warning(traceback.format_exc())
    return choices

def remove_dependant_choices(doc, parameter, choice):
    choices = get_choices_of(doc, parameter)
    choices.remove(choice)
    for a_choice in choices:
        t4 = [item for item in doc.findall('.//parameter') if '.%s' % a_choice in item.find('key').text]
        for t5 in t4:
            doc.remove(t5)

def remove_independant_choices(doc, parameter, choice):
    choices = []
    choices.append(choice)
    for a_choice in choices:
        t4 = [item for item in doc.findall('.//parameter') if '.%s' % a_choice in item.find('key').text]
        for t5 in t4:
            doc.remove(t5)

def remove_parameter_by_key(doc, parameter):
    t4 = [item for item in doc.findall('.//parameter') if item.find('key').text == parameter]
    for t5 in t4:
        doc.remove(t5)

def remove_other_choices(doc, parameter, choice):
    t5 = [item for item in doc.findall('.//parameter') if item.find('key').text == parameter]
    if len(t5) > 0:
        choices = [item for item in t5[0].findall('options/choices/choice') if item.text != choice]
        choice_root = t5[0].findall('options/choices')[0]
        for a_choice in choices:
            choice_root.remove(a_choice)

def remove_choice(doc, parameter, choice):
    t5 = [item for item in doc.findall('.//parameter') if item.find('key').text == parameter]
    if len(t5) > 0:
        choices = [item for item in t5[0].findall('options/choices/choice') if item.text == choice]
        choice_root = t5[0].findall('options/choices')[0]
        for a_choice in choices:
            choice_root.remove(a_choice)

def split_by_choice(doc, parameter):
    result = {}
    choices = get_choices_of(doc, parameter)
    import copy
    for choice in choices:
        working_copy = copy.deepcopy(doc)
        remove_dependant_choices(working_copy, parameter, choice)
        remove_other_choices(working_copy, parameter, choice)
        old_app_name = working_copy.find('key').text
        working_copy.find('key').text = '%s-%s' % (old_app_name, choice)
        old_longname = working_copy.find('longname').text
        working_copy.find('longname').text = '%s (%s)' % (old_app_name, choice)
        result[choice] = working_copy
    return result

def remove_parameter_by_criteria(doc, criteria):
    t4 = [item for item in doc.findall('./parameter') if criteria(item)]
    for t5 in t4:
        doc.getroot().remove(t5)

def defaultWrite(available_app, original_dom_document):
    fh = open("description/%s.xml" % available_app, "w")
    the_root = original_dom_document
    logger = logging.getLogger('OTBGenerator')
    ET.ElementTree(the_root).write(fh)
    fh.close()

def defaultSplit(available_app, original_dom_document, parameter):
    the_root = original_dom_document
    splitted = split_by_choice(the_root, parameter)
    the_list = []
    for key in splitted:
        defaultWrite('%s-%s' % (available_app, key), splitted[key])
        the_list.append(splitted[key])
    return the_list
