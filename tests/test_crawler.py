#!/usr/bin/env python3
"""
    test_crawler.py

    Part of Argostimè
    Test cases for crawler.py
"""

import unittest

from argostime.crawler import ParseProduct
import argostime.exceptions

class ParseProductTestCases(unittest.TestCase):

    def test_not_implemented_website(self):
        with self.assertRaises(argostime.exceptions.WebsiteNotImplementedException):
            ParseProduct("https://example.com")
