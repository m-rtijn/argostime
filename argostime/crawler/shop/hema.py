#!/usr/bin/env python3
"""
    crawler/shop/hema.py

    Crawler for hema.nl

    Copyright (c) 2022 Martijn <martijn [at] mrtijn.nl>

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

import codecs
import json
import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult, register_crawler


@register_crawler("HEMA", "hema.nl")
def crawl_hema(url: str) -> CrawlResult:
    """Crawler for hema.nl"""

    response: requests.Response = requests.get(url, timeout=10)

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    result: CrawlResult = CrawlResult(url=url)

    matches = soup.find_all("script")
    pattern = re.compile(r"var gtmDataObj = JSON\.parse\(.+\);")

    for match in matches:
        re_result: Optional[re.Match] = pattern.search(match.text)

        if re_result is not None:
            raw_json = re_result.group(0)
            logging.debug("Found raw product json %s", raw_json)
            break

    raw_json = raw_json.replace("var gtmDataObj = JSON.parse('", "")
    raw_json = raw_json.replace("');", "")

    raw_json = codecs.decode(raw_json, "unicode-escape")

    try:
        product_dict = json.loads(raw_json)
    except json.decoder.JSONDecodeError as exception:
        logging.error("Could not decode JSON %s, raising CrawlerException", raw_json)
        raise CrawlerException from exception

    logging.debug(product_dict)

    try:
        result.product_name = product_dict["ecommerce"]["detail"]["products"][0]["name"]
    except KeyError as exception:
        logging.error("Could not find product name in %s via %s", raw_json, url)
        raise CrawlerException from exception

    try:
        result.product_code = product_dict["ecommerce"]["detail"]["products"][0]["id"]
    except KeyError as exception:
        logging.error("Could not find product code in %s via %s", raw_json, url)
        raise CrawlerException from exception

    try:
        result.normal_price = float(product_dict["ecommerce"]["detail"]["products"][0]["price"])
    except KeyError as exception:
        logging.error("Could not find a valid price in %s via %s", raw_json, url)
        result.normal_price = -1

    return result
