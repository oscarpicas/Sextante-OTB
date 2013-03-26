import unittest
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
from sextante.otb.OTBTester import *

class AlgoTestCase(unittest.TestCase):
    def setUp(self):
        self.logger = get_OTB_log()
        self.the_files = [os.path.join(os.path.join(os.path.abspath(os.curdir), 'description'),each) for each in os.listdir(os.path.join(os.path.abspath(os.curdir), 'description')) if '.xml' in each]
        
    def tearDown(self):
        self.logger = None

class TestSequense(unittest.TestCase):
    pass

def test_generator(a_tuple):
    def test(self):
        logger = get_OTB_log()
        
        ut_command = a_tuple[0]
        self.assertTrue(ut_command != None)
        self.assertTrue(ut_command != "")

        ut_command_validation = a_tuple[1]
        self.assertTrue(ut_command_validation != None)
        self.assertTrue(ut_command_validation != "")

        args = shlex.split(ut_command)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (pout, perr) = p.communicate()
        if "ERROR" in pout:
            logger.error(pout)
        else:
            logger.info(pout)
    return test

if __name__ == '__main__':
    mkf = MakefileParser()
    the_tests = mkf.test_algos()
    for t in the_tests:
        test_name = 'test_%s' % t
        test = test_generator(the_tests[t])
        setattr(TestSequense, test_name, test)
    unittest.main()