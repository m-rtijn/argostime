"""
    crawler/shop/simonlevelt.py

    Crawler for simonlevelt.nl

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

import locale
import logging

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult, register_crawler


@register_crawler("Simon Lévelt", "simonlevelt.nl")
def crawl_simonlevelt(url: str) -> CrawlResult:
    """Crawler for simonlevelt.nl"""

    response: requests.Response = requests.get(url, timeout=10)

    if response.status_code != 200:
        logging.debug("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    result = CrawlResult()

    try:
        result.url = soup.find("meta", property="product:product_link").get("content")
    except Exception as exception:
        logging.info("Couldn't find url in soup, using given instead %s", exception)
        result.url = url

    try:
        name = soup.find("meta", property="og:title").get("content")
        result.product_name = name
        result.product_code = name.replace(" ", "_")
    except Exception as exception:
        logging.error("Could not find a product name / code %s", exception)
        raise CrawlerException from exception

    locale.setlocale(locale.LC_NUMERIC, "nl_NL.UTF-8")

    try:
        result.normal_price = locale.atof(
            soup.find("meta", property="product:price").get("content")
            )
    except Exception as exception:
        logging.error("Could not find a price %s", exception)
        raise CrawlerException from exception

    return result
