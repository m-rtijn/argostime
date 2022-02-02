#!/usr/bin/env python3
"""
    crawler/pipashop.py

    Crawler for pipa-shop.nl/

    Copyright (c) 2022 Stijn

    This file is part of Argostimè.

    Argostimè is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Argostimè is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Argostimè. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import re

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawlresult import CrawlResult


def crawl_pipashop(url: str) -> CrawlResult:
    result: CrawlResult = CrawlResult(url=url)
    request = requests.get(url, timeout=10)

    if request.status_code == 404:
        raise PageNotFoundException(url)

    soup = BeautifulSoup(request.text, "html.parser")

    try:
        price = re.sub(r"[^0-9.]", "", soup.select_one("div.product-price").text)
        result.name = soup.select_one("div.product-title a").text
        result.product_code = result.url.split("/product/").pop().split("/")[0]
        result.normal_price = float(price)
    except (AttributeError, IndexError, ValueError) as e:
        logging.error("%s, raising CrawlerException" % e)
        raise CrawlerException from KeyError

    return result
