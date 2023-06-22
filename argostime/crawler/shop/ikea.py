"""
    crawler/shop/ikea.py

    Crawler for ikea.com

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
import re

import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult, register_crawler


@register_crawler("IKEA", "ikea.com")
def crawl_ikea(url: str) -> CrawlResult:  # pylint: disable=R0915
    """Crawler for ikea.com"""

    result: CrawlResult = CrawlResult(url=url)

    response: requests.Response = requests.get(url, timeout=10)

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    info_wrapper = soup.find(
        "div",
        id= re.compile("buy-module-content")
        )

    try:
        result.url = soup.find("meta", property="og:url").get("content")
    except Exception as exception:
        logging.info("Couldn't find Open Graph canonical URL %s", exception)

    try:
        result.product_name = info_wrapper.find(
            ["span", "div"],
            class_= re.compile("header-section__title--big")
            ).text
    except Exception as exception:
        logging.error("Could not find a name in %s %s", info_wrapper, exception)
        raise CrawlerException from exception

    try:
        result.product_description = info_wrapper.find(
            "span",
            class_= re.compile("header-section__description-text")
            ).text
    except Exception as exception:
        logging.error("Could not find a description in %s", info_wrapper)


    try:
        result.product_code = soup.find(
            "span",
            class_= re.compile("product-identifier__value")
            ).text
    except Exception as exception:
        logging.error("Could not find a product code in %s %s", info_wrapper, exception)
        raise CrawlerException from exception

    try:
        # Todo: Verify if this is needed with discounted product page...
        price_tag_prev = info_wrapper.find(
            "div",
            class_= re.compile("price-package__previous-price-hasStrikeThrough")
            )

        if not price_tag_prev:
            price_tag_prev = info_wrapper.find(
                "div",
                class_=re.compile("price-module__addon")
            )

        integers = float(
            re.sub(
                ".-", "",
                price_tag_prev.find(
                    "span",
                    class_=re.compile("price__integer")
                ).text))

        try:
            decimals = float(
                price_tag_prev.find(
                    "span",
                    class_= re.compile("price__decimal")
                    ).text)
        except Exception as exception:
            logging.debug("No decimals found, assuming 0 %s", exception)
            decimals = 0.0

        result.normal_price = integers + decimals
    except Exception as exception:
        logging.info("No previous price found %s", exception)

    try:
        price_tag_curr = info_wrapper.find(
            # "div",
            class_= re.compile("price-module__current-price")
            )

        integers = float(
            re.sub(
                ".-", "",
                price_tag_curr.find(
                    "span",
                    class_= re.compile("price__integer")
                    ).text))

        try:
            decimals = float(
                price_tag_curr.find(
                    "span",
                    class_= re.compile("price__decimal")
                    ).text)
        except Exception as exception:
            logging.debug("No decimals found, assuming 0 %s", exception)
            decimals = 0.0

        if result.normal_price > 0:
            result.discount_price = integers + decimals
            result.on_sale = True
        else:
            result.normal_price = integers + decimals
    except Exception as exception:
        logging.error("No current price found in %s %s", info_wrapper, exception)
        raise CrawlerException from exception

    return result
