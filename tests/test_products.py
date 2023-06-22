"""
    test_products.py

    Part of Argostimè
    Test cases for products.py
"""

import unittest

import argostime.products
import argostime.exceptions

class ProductsTestCases(unittest.TestCase):

    def test_not_implemented_website(self):
        with self.assertRaises(argostime.exceptions.WebsiteNotImplementedException):
            argostime.products.add_product_offer_from_url("https://example.com")
