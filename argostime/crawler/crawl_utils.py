#!/usr/bin/env python3
"""
    crawler/crawl_utils.py

    Utilities for the crawler submodule

    Copyright (c) 2022 Martijn <martijn [at] mrtijn.nl>
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

import configparser
import logging
import re
from typing import Callable, Optional

__config = configparser.ConfigParser()
__config.read("argostime.conf")
__voor_regex = re.compile("voor")

enabled_shops = {}


def register_crawler(name: str, host: str, use_www: bool = True):
    """Decorator to register a new crawler function."""

    def decorate(func: Callable[[str], CrawlResult]):
        if "argostime" in __config and "disabled_shops" in __config["argostime"]:
            if host in __config["argostime"]["disabled_shops"]:
                logging.debug("Shop %s is disabled", host)
                return

        shop_info = {
            "name": name,
            "hostname": host,
            "crawler": func,
        }

        enabled_shops[host] = shop_info
        if use_www:
            enabled_shops[f"www.{host}"] = shop_info
        logging.debug("Shop %s is enabled", host)

    return decorate


class CrawlResult:
    """Data structure for returning the results of a crawler in a uniform way."""

    url: Optional[str]
    product_name: Optional[str]
    product_description: Optional[str]
    product_code: Optional[str]
    ean: Optional[int]

    normal_price: float = -1.0
    discount_price: float = -1.0
    on_sale: bool = False

    def __init__(
        self,
        url: str=None,
        product_name: str=None,
        product_description: str=None,
        product_code: str=None,
        normal_price: float=-1.0,
        discount_price: float=-1.0,
        on_sale: bool=False,
        ean: int=None,
        ):
        self.url = url
        self.product_name = product_name
        self.product_description = product_description
        self.product_code = product_code
        self.normal_price = normal_price
        self.discount_price = discount_price
        self.on_sale = on_sale
        self.ean = ean

    def __str__(self) -> str:
        string = f"CrawlResult(product_name={self.product_name},"\
            f"product_description={self.product_description},"\
            f"product_code={self.product_code},price={self.normal_price},"\
            f"discount={self.discount_price},sale={self.on_sale},ean={self.ean}"

        return string


def parse_promotional_message(message: str, price: float) -> float:
    """Parse a given promotional message, and returns the calculated effective price.

    For example "1+1 GRATIS" will be parsed to meaning a 50% discount.
    "2+1 GRATIS" will be parsed to mean a 33% discount, and will return 2/3.

    Returns -1 if it couldn't find a match
    """

    logging.debug("Parsing promotion %s", message)

    # Remove all whitespace from the message
    message_no_whitespace = "".join(message.split())

    message_no_whitespace = message_no_whitespace.lower()

    logging.debug("Promotion yielded sanitized input %s", message_no_whitespace)

    if message_no_whitespace == "1+1gratis":
        return 1/2 * price
    elif message_no_whitespace == "2+2gratis":
        return 1/2 * price
    elif message_no_whitespace == "2+1gratis":
        return 2/3 * price
    elif message_no_whitespace == "3+1gratis":
        return 3/4 * price
    elif message_no_whitespace == "5+1gratis":
        return 5/6 * price
    elif message_no_whitespace == "2ehalveprijs":
        return 3/4 * price
    elif message_no_whitespace == "50%korting":
        return 1/2 * price
    elif message_no_whitespace == "2eartikel70%":
        return 0.85 * price
    elif message_no_whitespace == "15%korting":
        return 0.85 * price
    elif message_no_whitespace == "1+1":
        return 1/2 * price
    elif message_no_whitespace == "6=5":
        return 5/6 * price
    elif message_no_whitespace == "2egratis":
        return 1/2 * price
    elif message_no_whitespace == "2+3gratis":
        return 0.4 * price
    elif "voor" in message_no_whitespace:
        msg_split = __voor_regex.split(message_no_whitespace)
        try:
            if msg_split[0] == '':
                return float(msg_split[1])
            return float(msg_split[1]) / float(msg_split[0])
        except ArithmeticError as exception:
            logging.error("Calculation error parsing %s %s", message_no_whitespace, exception)
        except IndexError as exception:
            logging.error("IndexError in message %s", message_no_whitespace)

    logging.error("Promotion text did not match any known promotion")
    return -1
