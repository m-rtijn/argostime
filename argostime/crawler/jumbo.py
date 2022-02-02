#!/usr/bin/env python3
"""
    crawler/jumbo.py

    Crawler for jumbo.com

    Copyright (c) 2022 Martijn <martijn [at] mrtijn.nl>

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

import json
import logging

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawlresult import CrawlResult

def crawl_jumbo(url: str) -> CrawlResult:
    """Crawler for jumbo.com

    May raise CrawlerException or PageNotFoundException.
    """
    headers = {
        "Referer": "https://www.jumbo.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "nl,en-US;q=0.7,en;q=0.3",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
    }

    request = requests.get(url, timeout=10, headers=headers)

    if request.status_code == 404:
        raise PageNotFoundException(url)

    soup = BeautifulSoup(request.text, "html.parser")
    product_json = soup.find("script", attrs={"type": "application/ld+json", "data-n-head": "ssr"})
    raw_json = product_json.string

    result: CrawlResult = CrawlResult(url=url)

    try:
        product = json.loads(raw_json)
    except json.decoder.JSONDecodeError:
        logging.error("Could not decode JSON %s, raising CrawlerException", raw_json)
        raise CrawlerException from json.decoder.JSONDecodeError

    if product["offers"]["@type"] == "AggregateOffer":
        offer = product["offers"]
    else:
        logging.error("No price info available, raising CrawlerException", raw_json)
        raise CrawlerException()

    try:
        result.url = str(product["url"])
    except KeyError:
        logging.info("No url found in product data, using the given url")
        result.url = url

    try:
        result.product_name = str(product["name"])
    except KeyError:
        logging.error("No product name found in %s", raw_json)
        raise CrawlerException from KeyError

    try:
        result.ean = int(product["gtin13"])
    except KeyError:
        logging.info("No EAN found")

    try:
        result.product_code = str(product["sku"])
    except KeyError:
        logging.error("No product code found in %s", raw_json)
        raise CrawlerException from KeyError

    try:
        result.discount_price = float(offer["lowPrice"])
    except KeyError:
        logging.info("No discount / low price found in %s", raw_json)

    try:
        result.normal_price = float(offer["highPrice"])
    except KeyError:
        logging.error("No normal price found in %s", raw_json)
        raise CrawlerException from KeyError

    return result
