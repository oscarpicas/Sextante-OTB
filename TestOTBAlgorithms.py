import unittest
import sys
import os
import traceback
import xml.etree.ElementTree as ET

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
        pass
        
    def tearDown(self):
        pass

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

                ut_command = get_automatic_unit_test_from_xml_description(dom_model)
                self.assertTrue(ut_command != None)
                self.assertTrue(ut_command != "")

                import os
                os.system(ut_command)
            except:
                self.fail("Problem with file %s: %s" % (a_file, traceback.format_exc()))

if __name__ == '__main__':
    unittest.main()