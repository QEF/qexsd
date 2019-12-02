#!/usr/bin/env python3
#
# Copyright (c), 2015-2019, Quantum Espresso Foundation and SISSA (Scuola
# Internazionale Superiore di Studi Avanzati). All rights reserved.
# This file is distributed under the terms of the MIT License. See the
# file 'LICENSE' in the root directory of the present distribution, or
# http://opensource.org/licenses/MIT.
# Authors: Davide Brunato
#
"""
Test classes for Quantum Espresso input converters.
"""
import unittest
import os
import glob
import xml.etree.ElementTree as ElementTree

import qeschema


def make_test_function(xml_file, ref_in_file):
    def test(self):
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()

        element_name = root.tag.split('}')[-1]

        if element_name == 'espresso':
            xml_conf = qeschema.PwDocument()
        elif element_name == 'nebRun':
            xml_conf = qeschema.NebDocument()
        elif element_name == 'espressoph':
            xml_conf = qeschema.PhononDocument()
        elif element_name == 'tddfpt':
            xml_conf = qeschema.TdDocument()
        elif element_name == 'spectrumDoc':
            xml_conf = qeschema.TdSpectrumDocument()
        else:
            raise ValueError("XML file %r is not a Quantum ESPRESSO document!" % xml_file)

        xml_conf.read(xml_file)
        qe_input = xml_conf.get_fortran_input().split('\n')
        with open(ref_in_file, 'r') as qe_input_file:
            k = 0
            are_equals = True
            for ref_line in qe_input_file:
                ref_line = ref_line.rstrip('\n').strip(' \t')
                in_line = qe_input[k].strip(' \t')
                if ref_line != in_line:
                    print("Unmatched lines: '%s' != '%s'" % (in_line, ref_line))
                    are_equals = False
                    break
                else:
                    k += 1
        self.assertTrue(are_equals, xml_file)
    return test


class ConverterTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.pkg_folder = os.path.dirname(cls.test_dir)

    def test_xml2qeinput_script(self):
        xml_filename = os.path.join(self.test_dir, 'examples/pw/Al001_relax_bfgs.xml')
        in_filename = xml_filename[:-4] + '.in'
        conversion_script = os.path.join(self.pkg_folder, 'scripts/xml2qeinput.py')
        if os.path.isfile(in_filename):
            os.system('rm -f %s' % in_filename)
        command = 'python %s -in %s 1> /dev/null 2> /dev/null' % (conversion_script, xml_filename)
        os.system(command)
        self.assertTrue(os.path.isfile(in_filename), 'Test output file %r missing!' % in_filename)

    def test_yaml2qeinput_script(self):
        xml_filename = os.path.join(self.test_dir, 'examples/pw/Al001_relax_bfgs.yml')
        in_filename = xml_filename[:-4] + '.in'
        conversion_script = os.path.join(self.pkg_folder, 'scripts/yaml2qeinput.py')
        if os.path.isfile(in_filename):
            os.system('rm -f %s' % in_filename)
        command = 'python %s -in %s 1> /dev/null 2> /dev/null' % (conversion_script, xml_filename)
        os.system(command)
        self.assertTrue(os.path.isfile(in_filename), 'Test output file %r missing!' % in_filename)


##
# Create test classes for examples
#
test_dir = os.path.dirname(os.path.abspath(__file__))

for filename in glob.glob(os.path.join(test_dir, "examples/*/*.xml")):
    qe_input_filename = '%s.in.test' % filename[:-4]
    if not os.path.isfile(qe_input_filename):
        continue

    test_func = make_test_function(filename, qe_input_filename)
    test_name = os.path.relpath(filename)
    klassname = 'Test_{0}'.format(test_name.replace('/', '__'))
    globals()[klassname] = type(
        klassname, (unittest.TestCase,),
        {'test_converter_{0}'.format(test_name): test_func, 'longMessage': True}
    )


if __name__ == '__main__':
    unittest.main()
