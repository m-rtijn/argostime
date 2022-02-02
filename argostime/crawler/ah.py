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

from argostime.crawler.crawlresult import CrawlResult

ah_date_format: str = "%Y-%m-%d"

def crawl_ah(url: str) -> CrawlResult:
    """Crawler for ah.nl"""
    response: requests.Response = requests.get(url)

    if response.status_code != 200:
        logging.debug("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    product_json = soup.find("script", attrs={ "type": "application/ld+json", "data-react-helmet": "true"})

    result: CrawlResult = CrawlResult(url=url)

    try:
        product_dict = json.loads(product_json.text)
    except json.decoder.JSONDecodeError:
        logging.error("Could not decode JSON %s, raising CrawlerException", product_json)
        raise CrawlerException from json.decoder.JSONDecodeError

    try:
        result.product_name = product_dict["name"]
    except KeyError:
        logging.error("No key name found in json %s", product_dict)
        raise CrawlerException from KeyError

    try:
        result.ean = product_dict["gtin13"]
    except KeyError:
        logging.error("No key gtin13 found in json %s", product_dict)
        # Don't crash because the ean is not strictly necessarry
        pass

    try:
        result.product_code = product_dict["sku"]
    except KeyError:
        logging.error("No key sku found in json %s", product_dict)
        raise CrawlerException from KeyError

    try:
        if product_dict["offers"]["validFrom"] == "undefined":
            # Sometimes the "validFrom" is just undefined, just assume that there is a discount then
            result.discount_price = float(product_dict["offers"]["price"])
            result.normal_price = -1.0
        else:
            bonus_from: datetime = datetime.strptime(product_dict["offers"]["validFrom"], ah_date_format)
            try:
                bonus_until: datetime = datetime.strptime(product_dict["offers"]["priceValidUntil"], ah_date_format)
            except ValueError:
                # If there is no bonus_until, just use this instead
                bonus_until: datetime = datetime(year=5000, month=12, day=31)
            if datetime.now() >= bonus_from and datetime.now() <= bonus_until:
                result.discount_price = float(product_dict["offers"]["price"])
                result.normal_price = -1.0
            else:
                # Ahh, the nice moments when there is just no valid price available. That sucks!
                logging.error("No valid price available for %s", url)
                result.normal_price = -1.0
    except KeyError:
        # No details on if there is bonus data or not, so assume no bonus
        try:
            result.normal_price = float(product_dict["offers"]["price"])
        except KeyError:
            logging.error("Couldn't even find a normal price in %s", product_dict)
            raise CrawlerException from KeyError

    return result
