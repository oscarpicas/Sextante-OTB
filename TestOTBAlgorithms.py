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

class AlgoTestCase(unittest.TestCase):
    def setUp(self):
        self.logger = get_OTB_log()
        self.the_files = [os.path.join(os.path.join(os.path.abspath(os.curdir), 'description'),each) for each in os.listdir(os.path.join(os.path.abspath(os.curdir), 'description')) if '.xml' in each]
        
    def tearDown(self):
        self.logger = None

    def test_description_algorithms_in_xml_files(self):
        import os
        xml_files = [os.path.join(os.path.join(os.path.abspath(os.curdir), 'description'),each) for each in os.listdir(os.path.join(os.path.abspath(os.curdir), 'description')) if '.xml' in each]
        otb_algos = []
        
        for a_file in xml_files:
            try:
                otb_algo = OTBAlgorithm(a_file)
                otb_algos.append(otb_algo)
            except:
                self.fail("Problem with file %s: %s" % (a_file, traceback.format_exc()))

    def test_exec_of_grayscale(self):
        import os
        xml_files = [os.path.join(os.path.join(os.path.abspath(os.curdir), 'description'),each) for each in os.listdir(os.path.join(os.path.abspath(os.curdir), 'description')) if '.xml' in each]
        xml_files = [each for each in xml_files if "BinaryMorphological" in each]
        
        for a_file in xml_files:
            try:
                content = open(a_file).read()
                dom_model = ET.fromstring(content)

                ut_command = get_automatic_ut_from_xml_description(dom_model)
                self.assertTrue(ut_command != None)
                self.assertTrue(ut_command != "")

                args = shlex.split(ut_command)
                p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (pout, perr) = p.communicate()
                if "ERROR" in pout:
                    self.logger.error(pout)
                else:
                    self.logger.info(pout)
            except:
                self.fail("Problem with file %s: %s" % (a_file, traceback.format_exc()))

    def test_indeed(self):
        print "Running indeed"
        print self.the_files
        for param in self.the_files:
            try:
                yield run_it, param
            except:
                self.fail("Problem with file %s: %s" % (param, traceback.format_exc()))

class TestSequense(unittest.TestCase):
    pass

def test_generator(a_file):
    def test(self):
        logger = get_OTB_log()
        
        content = open(a_file).read()
        dom_model = ET.fromstring(content)

        ut_command = get_automatic_ut_from_xml_description(dom_model)
        self.assertTrue(ut_command != None)
        self.assertTrue(ut_command != "")

        args = shlex.split(ut_command)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (pout, perr) = p.communicate()
        if "ERROR" in pout:
            logger.error(pout)
        else:
            logger.info(pout)
    return test


if __name__ == '__main__':
    l = [(each, os.path.join(os.path.join(os.path.abspath(os.curdir), 'description'),each)) for each in os.listdir(os.path.join(os.path.abspath(os.curdir), 'description')) if '.xml' in each]
    for t in l:
        test_name = 'test_%s' % t[0]
        test = test_generator(t[1])
        setattr(TestSequense, test_name, test)
    unittest.main()