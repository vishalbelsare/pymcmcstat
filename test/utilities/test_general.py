#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 06:17:24 2018

@author: prmiles
"""
from pymcmcstat.utilities.general import message
import unittest
import io
import sys

# --------------------------
class MessageDisplay(unittest.TestCase):
    def test_standard_print(self):
        capturedOutput = io.StringIO()                  # Create StringIO object
        sys.stdout = capturedOutput                     #  and redirect stdout.
        flag = message(verbosity = 1, level = 0, printthis = 'test')
        sys.stdout = sys.__stdout__                     # Reset redirect.
        self.assertEqual(capturedOutput.getvalue(), 'test\n', msg = 'Expected string')
        self.assertTrue(flag, msg = 'Statement was printed')
        
    def test_no_print(self):
        capturedOutput = io.StringIO()                  # Create StringIO object
        sys.stdout = capturedOutput                     #  and redirect stdout.
        flag = message(verbosity = 0, level = 1, printthis = 'test')
        sys.stdout = sys.__stdout__                     # Reset redirect.
        self.assertFalse(flag, msg = 'Statement not printed because verbosity less than level')
        