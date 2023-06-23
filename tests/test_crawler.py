"""
    test_crawler.py

    Part of Argostimè
    Test cases for crawler.py
"""

import unittest

import argostime.exceptions
from argostime.crawler import crawl_url


class ParseProductTestCases(unittest.TestCase):

    def test_not_implemented_website(self):
        with self.assertRaises(
                argostime.exceptions.WebsiteNotImplementedException):
            crawl_url("https://example.com")
