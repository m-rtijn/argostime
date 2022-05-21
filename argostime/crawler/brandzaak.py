#!/usr/bin/env python3
"""
    crawler/brandzaak.py

    Crawler for brandzaak.nl

    Copyright (c) 2022 Martijn <martijn [at] mrtijn.nl>
    Copyright (c) 2022 semyon

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


import logging

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult

def crawl_brandzaak(url: str) -> CrawlResult:
    """Parse a product from brandzaak.nl"""

    response = requests.get(url)

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    result: CrawlResult = CrawlResult(url=url)

    product_title = soup.find("meta", attrs={ "name": "title"})
    product_price = soup.find("meta", attrs={ "property": "product:price:amount"})

    try:
        result.product_name = product_title['content']
    except KeyError as exception:
        logging.error("Could not find product name in %s", product_title)
        raise CrawlerException from exception
    try:
        result.normal_price = float(product_price['content'])
    except KeyError as exception:
        logging.error("Could not find price in %s", product_price)
        raise CrawlerException from exception
    try:
        result.product_code = product_title['content'].replace(" ", "-")
    except KeyError as exception:
        logging.error("Could not find product code in %s", product_title)
        raise CrawlerException from exception

    return result
