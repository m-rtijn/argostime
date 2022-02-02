#!/usr/bin/env python3
"""
    crawler/ah.py

    Crawler for ah.nl

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

from datetime import datetime
import json
import logging


import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult, parse_promotional_message

ah_date_format: str = "%Y-%m-%d"

def crawl_ah(url: str) -> CrawlResult:
    """Crawler for ah.nl"""
    response: requests.Response = requests.get(url)

    if response.status_code != 200:
        logging.debug("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    product_json = soup.find(
        "script",
        attrs={ "type": "application/ld+json", "data-react-helmet": "true"}
        )

    result: CrawlResult = CrawlResult(url=url)

    try:
        product_dict = json.loads(product_json.text)
    except json.decoder.JSONDecodeError as exception:
        logging.error("Could not decode JSON %s, raising CrawlerException", product_json)
        raise CrawlerException from exception

    try:
        result.product_name = product_dict["name"]
    except KeyError as exception:
        logging.error("No key name found in json %s", product_dict)
        raise CrawlerException from exception

    try:
        result.ean = product_dict["gtin13"]
    except KeyError:
        # Don't crash because the ean is not strictly necessarry
        logging.info("No key gtin13 found in json %s", product_dict)

    try:
        result.product_code = product_dict["sku"]
    except KeyError as exception:
        logging.error("No key sku found in json %s", product_dict)
        raise CrawlerException from exception

    try:
        offer = product_dict["offers"]
    except KeyError as exception:
        logging.error("Could not find a valid offer in the json %s", product_dict)

    if "validFrom" in offer.keys():
        try:
            bonus_from: datetime = datetime.strptime(
                offer["validFrom"],
                ah_date_format
                )
        except ValueError:
            logging.error(
                "Failed to parse validFrom %s, assuming bonus is valid",
                offer["validFrom"]
                )
            bonus_from: datetime = datetime(year=2000, month=1, day=1)
        try:
            bonus_until: datetime = datetime.strptime(
                offer["priceValidUntil"],
                ah_date_format
                )
        except ValueError:
            logging.error(
                "Failed to parse priceValidUntil %s, using fallback",
                offer["priceValidUntil"]
                )
            bonus_until: datetime = datetime(year=5000, month=12, day=31)

        if datetime.now() >= bonus_from and datetime.now() <= bonus_until:
            # Try to find a promotional message
            promo_text_matches = soup.find_all(
                "p",
                attrs={ "class" :lambda x: x and x.startswith("promo-sticker-text") }
                )

            logging.debug(promo_text_matches)

            promotion_message: str = ""
            for match in promo_text_matches:
                promotion_message = promotion_message + match.text

            # Remove all whitespace from the message
            message_no_whitespace = "".join(promotion_message.split())
            message_no_whitespace.lower()

            # If there is a mark with for example "25% Korting", this is already calculated into
            # the price we got from the json.
            if "korting" not in message_no_whitespace:
                promotion = parse_promotional_message(promotion_message)
            else:
                promotion = -1

            logging.debug(
                "Found promotional message %s with result %f",
                promotion_message,
                promotion
                )

            if promotion != -1:
                result.discount_price = float(offer["price"]) * promotion
            else:
                result.discount_price = float(offer["price"])
        else:
            # No valid bonus, so there's no valid price available.
            logging.info("No valid price found for %s", url)
            result.normal_price = -1
    else:
        # No details on if there is bonus data or not, so assume no bonus
        try:
            result.normal_price = float(product_dict["offers"]["price"])
        except KeyError as inner_exception:
            logging.error("Couldn't even find a normal price in %s", product_dict)
            raise CrawlerException from inner_exception

    return result
