#!/usr/bin/env python3
"""
    crawler/shop/intergamma.py

    Crawler for gamma.nl and karwei.nl

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

import logging

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult, register_crawler


@register_crawler("karwei", "Karwei", ["karwei.nl", "www.karwei.nl"])
def crawl_karwei(url: str) -> CrawlResult:
    return crawl_gamma(url)


@register_crawler("gamma", "Gamma", ["gamma.nl", "www.gamma.nl"])
def crawl_gamma(url: str) -> CrawlResult:
    """Crawler for gamma.nl and karwei.nl"""

    response: requests.Response = requests.get(url)
    if response.status_code != 200:
        logging.error("Got status code %s while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    # Use UTF-8 encoding instead of ISO-8859-1
    response.encoding = 'UTF-8'

    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    result: CrawlResult = CrawlResult()

    try:
        result.url = soup.find(
            "link",
            itemprop="url"
        )["href"]
    except Exception as exception:
        logging.error("Could not find canonical URL")
        logging.debug("Got exception: %s", exception)
        # Don't raise an exception, just use the url given by the user.
        result.url = url

    try:
        result.product_name = soup.find(
            "h1",
            itemprop="name"
        ).text
    except Exception as exception:
        logging.error("Could not find product name, raising CrawlerException")
        logging.debug("Got exception: %s", exception)
        raise CrawlerException from exception

    try:
        result.product_code = soup.find(
            "div",
            itemtype="http://schema.org/Product"
        )["data-product-code"]
    except Exception as exception:
        logging.error("Could not find a product code, raising CrawlerException")
        logging.debug("Got exception: %s", exception)
        raise CrawlerException from exception

    try:
        result.ean = int(soup.find(
            "div",
            itemtype="http://schema.org/Product"
        )["data-ean"])
    except Exception as exception:
        # Don't raise an exception since EAN is not strictly necessary!
        logging.error("Could not find EAN code")
        logging.debug("Got exception: %s", exception)

    try:
        price_tag = soup.find(
            "div",
            "product-price"
        )

        price = float(price_tag.find(
            "meta",
            itemprop="price"
        )["content"])

        if "promotion" in price_tag.attrs["class"]:
            result.discount_price = price
            result.on_sale = True
        else:
            result.normal_price = price
    except Exception as exception:
        logging.error("Could not find price, raising CrawlerException")
        logging.debug("Got exception: %s", exception)
        raise CrawlerException from exception

    return result
