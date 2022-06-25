#!/usr/bin/env python3
"""
    crawler/shop/ekoplaza.py

    Crawler for ekoplaza.nl

    Copyright (c) 2022 Anna <anna [at] anna.computer>

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

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult, register_crawler


@register_crawler("Ekoplaza", "ekoplaza.nl")
def crawl_ekoplaza(url: str) -> CrawlResult:
    """Ekoplaza crawler"""

    info = url.split('product/')[-1]
    response = requests.get(
        f'https://www.ekoplaza.nl/api/aspos/products/url/{info}')

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s",
                      response.status_code, url)
        raise PageNotFoundException(url)
    try:
        product = response.json()["Product"]
    except KeyError as exception:
        logging.error("No product found at %s", url)
        raise CrawlerException from exception

    result = CrawlResult(url=url)

    try:
        result.product_name = product['Description'].title()
    except KeyError as exception:
        logging.error("No product name found in %s", product)
        raise CrawlerException from exception

    try:
        # Product codes seem to be valid EANs
        result.product_code = product['DefaultScanCode']['Code']
        result.ean = product['DefaultScanCode']['Code']
    except KeyError as exception:
        logging.error("No product code found in %s", product)
        raise CrawlerException from exception

    try:
        result.discount_price = float(product['Discount']['PriceInclTax'])
    except KeyError:
        pass

    try:
        result.normal_price = float(product['PriceInclTax'])
    except KeyError as exception:
        logging.error("No normal price found in %s", product)
        raise CrawlerException from exception

    return result
