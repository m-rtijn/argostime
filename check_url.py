#!/usr/bin/env python3
"""
    check_url.py

    Part of Argostimè

    Standalone script to test the product page crawler.
"""

import logging
import sys

from argostime.crawler.crawl_url import crawl_url

from argostime.crawler.crawl_utils import CrawlResult

# Print help message if needed...
if len(sys.argv) < 2 or len(sys.argv) > 2 or "help" in sys.argv[1]:
    print(f"usage: {sys.argv[0]} url")
    exit()

# Just call the crawler with the url given by the user
try:
    result: CrawlResult = crawl_url(sys.argv[1])
except Exception as exception:
    print(f"Exception thrown during crawling:\n{exception}\nExiting...", file=sys.stderr)
    exit()

# Crawling was succesful, print results...
print("Crawling result:")
print(f"  -> Name:        {result.product_name}")
print(f"  -> Description: {result.product_description}")
print(f"  -> Code:        {result.product_code}")
print(f"  -> Price:       {result.normal_price}")
print(f"  -> Discount:    {result.discount_price}")
print(f"  -> On-sale:     {result.on_sale}")
print(f"  -> EAN:         {result.ean}")
