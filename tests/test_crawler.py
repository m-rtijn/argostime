"""
    test_crawler.py

    Part of Argostimè
    Test cases for crawler.py
"""

import unittest

from argostime.crawler import crawl_url
import argostime.exceptions

class ParseProductTestCases(unittest.TestCase):

    def test_not_implemented_website(self):
        with self.assertRaises(argostime.exceptions.WebsiteNotImplementedException):
            crawl_url("https://example.com")
