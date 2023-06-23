#!/usr/bin/env python3
"""
    check_url.py

    Standalone script to test the product page crawler.

    Copyright (c) 2022 Kevin

    This file is part of Argostimè.

    Argostimè is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Argostimè is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Argostimè. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import traceback

from argostime.crawler.crawl_url import crawl_url
from argostime.crawler.crawl_utils import CrawlResult

# Print help message if needed...
if len(sys.argv) < 2 or len(sys.argv) > 2 or "help" in sys.argv[1]:
    print(f"usage: {sys.argv[0]} url")
    exit()

# Just call the crawler with the url given by the user
try:
    result: CrawlResult = crawl_url(sys.argv[1])
except:
    print("Exception thrown during crawling:", file=sys.stderr)
    traceback.print_exc()
    exit()

# Crawling was successful, print results...
print("Crawling result:")
print(f"  -> URL:         {result.url}")
print(f"  -> Name:        {result.product_name}")
print(f"  -> Description: {result.product_description}")
print(f"  -> Code:        {result.product_code}")
print(f"  -> Price:       {result.normal_price}")
print(f"  -> Discount:    {result.discount_price}")
print(f"  -> On-sale:     {result.on_sale}")
print(f"  -> EAN:         {result.ean}")
