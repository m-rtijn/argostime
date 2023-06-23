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
from typing import Callable, Dict, Optional, TypedDict

from argostime.exceptions import CrawlerException

__config = configparser.ConfigParser()
__config.read("argostime.conf")
__voor_regex = re.compile("voor")


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
        url: Optional[str]=None,
        product_name: Optional[str]=None,
        product_description: Optional[str]=None,
        product_code: Optional[str]=None,
        normal_price: float=-1.0,
        discount_price: float=-1.0,
        on_sale: bool=False,
        ean: Optional[int]=None,
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

    def check(self) -> None:
        """
        Check if CrawlResult contains the mandatory data needed to store the
        product in the database and if the data is consistent.
        The mandatory data is:
          - url
          - product_name
          - product_code
        If on_sale is True, discount_price must be non-negative and non-zero.
        If on_sale is False, normal_price must be non-negative and non-zero.
        """

        # Check if url, product name and product code fields are set
        if not self.url or self.url == "":
            raise CrawlerException("No url given for item!")
        if not self.product_name or self.product_name == "":
            raise CrawlerException("No product name given for item!")
        if not self.product_code or self.product_code == "":
            raise CrawlerException("No product code given for item!")

        # Check price and on_sale flag consistency
        if self.discount_price < 0 and self.on_sale:
            raise CrawlerException("No discount price given for item on sale!")
        if self.normal_price < 0 and not self.on_sale:
            raise CrawlerException("No normal price given for item not on sale!")


CrawlerFunc = Callable[[str], CrawlResult]
ShopDict = TypedDict("ShopDict", {"name": str, "hostname": str, "crawler": CrawlerFunc})
enabled_shops: Dict[str, ShopDict] = {}


def register_crawler(name: str, host: str, use_www: bool = True) -> Callable[[CrawlerFunc], None]:
    """Decorator to register a new crawler function."""

    def decorate(func: Callable[[str], CrawlResult]) -> None:
        """
        This function will be called when you put the "@register_crawler" decorator above
        a function defined in a file in the "shop" directory! The argument will be the
        function above which you put the decorator.
        """
        if "argostime" in __config and "disabled_shops" in __config["argostime"]:
            if host in __config["argostime"]["disabled_shops"]:
                logging.debug("Shop %s is disabled", host)
                return

        shop_info: ShopDict = {
            "name": name,
            "hostname": host,
            "crawler": func,
        }

        enabled_shops[host] = shop_info
        if use_www:
            enabled_shops[f"www.{host}"] = shop_info
        logging.debug("Shop %s is enabled", host)

    return decorate


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
        except IndexError:
            logging.error("IndexError in message %s", message_no_whitespace)

    logging.error("Promotion text did not match any known promotion")
    return -1
