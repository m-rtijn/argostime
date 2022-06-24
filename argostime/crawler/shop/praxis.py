#!/usr/bin/env python3
"""
    crawler/shop/praxis.py

    Crawler for praxis.nl

    Copyright (c) 2022 Kevin <kevin [at] 2sk.nl>

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

import json
import logging
import re

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult, register_crawler


def __fix_bad_json(bad_json: str) -> str:
    return re.sub(r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'', bad_json)


@register_crawler("praxis", "Praxis", ["praxis.nl", "www.praxis.nl"])
def crawl_praxis(url: str) -> CrawlResult:
    """Crawler for praxis.nl"""

    response: requests.Response = requests.get(url)
    if response.status_code != 200:
        logging.error("Got status code %s while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    result: CrawlResult = CrawlResult()

    try:
        raw_product_json = soup.find(
            "script",
            text=lambda value: value and value.startswith("window.__PRELOADED_STATE_productDetailsFragmentInfo__")
        ).text.split("=", maxsplit=1)[1].strip()
    except Exception as exception:
        logging.error("Could not find a product detail JSON, raising CrawlerException")
        raise CrawlerException from exception

    try:
        json_data = json.loads(__fix_bad_json(raw_product_json))
        product = json_data["productDetails"]
    except json.decoder.JSONDecodeError as exception:
        logging.error("Could not decode JSON %s, raising CrawlerException", raw_product_json)
        raise CrawlerException from exception
    except KeyError as exception:
        logging.error("No key productDetails found in JSON data")
        raise CrawlerException from exception

    try:
        result.url = f"https://www.praxis.nl{json_data['productUrl']}"
    except KeyError as exception:
        logging.error("No key ProductUrl found in JSON")
        raise CrawlerException from exception

    try:
        result.product_name = product["name"]
    except KeyError as exception:
        logging.error("No key name found in JSON")
        raise CrawlerException from exception

    try:
        result.product_code = product["code"].lstrip("0")
    except KeyError as exception:
        logging.error("No key code found in JSON")
        raise CrawlerException from exception

    try:
        result.ean = int(product["ean"])
    except KeyError as exception:
        # Don't raise an exception since EAN is not strictly necessary!
        logging.error("No key ean found in JSON")

    try:
        if "discount" in product.keys() and \
        ("discountClass" not in product.keys() or product["discountClass"] != "excludedproducts"):
            result.discount_price = float(product["discount"]["value"])
            result.on_sale = True
        else:
            result.normal_price = float(product["price"]["value"])
    except KeyError as exception:
        logging.error("Could not find price in product JSON")
        raise CrawlerException from exception

    return result
