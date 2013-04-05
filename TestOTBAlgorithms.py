# -*- coding: utf-8 -*-

"""
***************************************************************************
    TestOTBAlgorithms.py
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import unittest
import signal
import sys
import os
import traceback
import xml.etree.ElementTree as ET
import shlex, subprocess

try:
    import sextante
except ImportError, e:
    raise Exception("Sextante must be installed and available in PYTHONPATH")

try:
    import otbApplication
except ImportError, e:
    raise Exception("OTB python plugins must be installed and available in PYTHONPATH")

from sextante.otb.OTBAlgorithm import OTBAlgorithm
from sextante.otb.OTBHelper import *
from sextante.otb.OTBTester import MakefileParser

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

class AlgoTestCase(unittest.TestCase):
    def setUp(self):
        self.logger = get_OTB_log()
        self.the_files = [os.path.join(os.path.join(os.path.abspath(os.curdir), 'description'),each) for each in os.listdir(os.path.join(os.path.abspath(os.curdir), 'description')) if '.xml' in each]
        
    def tearDown(self):
        self.logger = None

class TestSequence(unittest.TestCase):
    pass

def ut_generator(a_tuple):
    def test(self):
        logger = get_OTB_log()

        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(5*60)  # 5 minutes

        black_list = []
        
        ut_command = a_tuple[0]
        self.assertTrue(ut_command != None)
        self.assertTrue(ut_command != "")

        ut_command_validation = a_tuple[1]
        self.assertTrue(ut_command_validation != None)
        self.assertTrue(ut_command_validation != "")

        if ut_command.split(" ")[0] in black_list:
            raise Exception("Blacklisted test !")

        args = shlex.split(ut_command)
        failed = False
        logger.info("Running [%s]" % ut_command)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (pout, perr) = p.communicate()
        if ("ERROR" in pout or "ERROR" in perr) or ("FATAL" in pout or "FATAL" in perr) or ("CRITICAL" in pout or "CRITICAL" in perr):
            error_text = "Command [%s] returned [%s]" % (ut_command, pout)
            if "Invalid image filename" in pout or "Invalid vector data filename" in pout or "Failed to open" in pout:
                logger.error(error_text)
            else:
                logger.error(error_text)
                self.fail(error_text)
            failed = True
        else:
            logger.info(pout)

        if (len(ut_command_validation) > 0) and not failed:
            new_ut_command_validation = ut_command_validation + " Execute " +  ut_command

            logger.info("Running Unit test [%s]" % new_ut_command_validation)
            argz = shlex.split(new_ut_command_validation)
            q = subprocess.Popen(argz, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (qout, qerr) = q.communicate()

            if not ("Test EXIT SUCCESS" in qout or "Test EXIT SUCCESS" in qerr):
                error_text = "Unit test [%s] returned [%s]" % (new_ut_command_validation, qout)
                if "Invalid image filename" in qout or "Invalid vector data filename" in qout or "Failed to open" in qout:
                    logger.error(error_text)
                else:
                    logger.error(error_text)
                    self.fail(error_text)
            else:
                logger.info(qout)

        signal.alarm(0)

    return test

def get_client_apps():
    app_clients = []
    for available_app in otbApplication.Registry.GetAvailableApplications():
        app_instance = otbApplication.Registry.CreateApplication(available_app)
        app_instance.UpdateParameters()
        ct = "otbcli_" + available_app
        app_clients.append(ct)
    return app_clients

def unfiltered_sextante_mapping():
    mkf = MakefileParser()
    the_tests = mkf.test_algos()
    for t in the_tests:
        test_name = 'test_std_%s' % t
        test = ut_generator(the_tests[t])
        setattr(TestSequence, test_name, test)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequence)
    unittest.TextTestRunner(verbosity=2).run(suite)

def test_sextante_mapping():
    mkf = MakefileParser()
    the_tests = mkf.test_algos()
    clients = get_client_apps()
    for t in the_tests:
        test_name = 'test_%s' % t
        if the_tests[t][0].split(" ")[0] in clients:
            test = ut_generator(the_tests[t])
            setattr(TestSequence, test_name, test)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequence)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    import sextante
    mkf = MakefileParser()
    the_tests = mkf.test_algos()
    for t in the_tests:
        test_name = 'test_%s' % t
        test = ut_generator(the_tests[t])
        setattr(TestSequence, test_name, test)
    unittest.main()
