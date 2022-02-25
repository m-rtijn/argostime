#!/usr/bin/env python3
"""
    crawler/ikea.py

    Crawler for ikea.com

    Copyright (c) 2022 Kevin

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

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult

def crawl_ikea(url: str) -> CrawlResult:
    """Crawler for ikea.com"""

    result: CrawlResult = CrawlResult(url=url)

    response: requests.Response = requests.get(url)

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    info_wrapper = soup.find(
        "div",
        "range-revamp-pip-price-package__wrapper"
        )

    try:
        result.url = soup.find("meta", property="og:url").get("content")
    except Exception as exception:
        logging.info("Couldn't find Open Graph canonical URL %s", exception)

    try:
        title = info_wrapper.find(
            "div",
            "range-revamp-header-section__title--big"
            ).text
        description = info_wrapper.find(
            "span",
            "range-revamp-header-section__description-text"
            ).text

        result.product_name = f"{title} ({description})"
    except Exception as exception:
        logging.error("Could not find a name in %s", info_wrapper)
        raise CrawlerException from exception

    try:
        result.product_code = soup.find(
            "span",
            "range-revamp-product-identifier__value"
            ).text
    except Exception as exception:
        logging.error("Could not find a product code in %s %s", info_wrapper, exception)
        raise CrawlerException from exception


    try:
        integers = float(
            info_wrapper.find(
                "span",
                "range-revamp-price__integer"
                ).text)

        try:
            decimals = float(
                info_wrapper.find(
                    "span",
                    "range-revamp-price__decimals"
                    ).text)
        except:
            decimals = 0.0

        result.normal_price = integers + decimals
    except Exception as exception:
        logging.error("No normal price found in %s %s", info_wrapper, exception)
        raise CrawlerException from exception

    return result
