#!/usr/bin/python3
"""
    crawler.py

    This file contains all code that is actually interacting with 3rd party websites.

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
import urllib.parse
import requests
from bs4 import BeautifulSoup

from .exceptions import CrawlerException, PageNotFoundException
from .exceptions import WebsiteNotImplementedException

shops_info = {
    "ah": {
        "name": "Albert Heijn",
        "hostname": "ah.nl"
    },
    "jumbo": {
        "name": "Jumbo",
        "hostname": "jumbo.com"
    }
}

enabled_shops = {
    "ah.nl": "ah",
    "www.ah.nl": "ah",
    "jumbo.com": "jumbo",
    "www.jumbo.com": "jumbo"
}

class ParseProduct():
    """The results of parsing a product from a URL"""
    name: str
    url: str
    product_code: str
    ean: int

    normal_price: float
    discount_price: float = 0.0
    on_sale: bool = False

    def __init__(self, url: str):
        """Parse a product from a URL.

        Raises a WebsiteNotImplementedException if the hostname is unknown.
        """

        self.url = url

        hostname: str = urllib.parse.urlparse(url).netloc

        if shops_info["ah"]["hostname"] in hostname:
            self._parse_ah()
        else:
            raise WebsiteNotImplementedException(url)

        if self.discount_price > 0:
            self.on_sale = True

        logging.debug("Crawled %s with results %f, %f, %s, %s",
                        url,
                        self.normal_price,
                        self.discount_price,
                        self.product_code,
                        self.on_sale)

    def _parse_ah(self):
        """Parse a product from ah.nl"""

        ah_date_format: str = "%Y-%m-%d"

        request = requests.get(self.url)

        if request.status_code == 404:
            raise PageNotFoundException(self.url)

        soup = BeautifulSoup(request.text, "html.parser")

        product_json = soup.find("script", attrs={ "type": "application/ld+json", "data-react-helmet": "true"})

        try:
            product_dict = json.loads(product_json.text)
        except json.decoder.JSONDecodeError:
            logging.error("Could not decode JSON %s, raising CrawlerException", product_json)
            raise CrawlerException from json.decoder.JSONDecodeError

        try:
            self.name = product_dict["name"]
        except KeyError:
            logging.error("No key name found in json %s", product_dict)
            raise CrawlerException from KeyError

        try:
            self.ean = product_dict["gtin13"]
        except KeyError:
            logging.error("No key gtin13 found in json %s", product_dict)
            raise CrawlerException from KeyError

        try:
            self.product_code = product_dict["sku"]
        except KeyError:
            logging.error("No key sku found in json %s", product_dict)
            raise CrawlerException from KeyError

        try:
            bonus_from: datetime = datetime.strptime(product_dict["offers"]["validFrom"], ah_date_format)
            bonus_until: datetime = datetime.strptime(product_dict["offers"]["priceValidUntil"], ah_date_format)
            if datetime.now() >= bonus_from and datetime.now() <= bonus_until:
                self.discount_price = float(product_dict["offers"]["price"])
                self.normal_price = -1.0
            else:
                # Ahh, the nice moments when there is just no valid price available. That sucks!
                logging.error("No valid price available for %s", self.url)
                self.normal_price = -1.0
        except KeyError:
            # No details on if there is bonus data or not, so assume no bonus
            try:
                self.normal_price = float(product_dict["offers"]["price"])
            except KeyError:
                logging.error("Couldn't even find a normal price in %s", product_dict)
                raise CrawlerException from KeyError

    def _parse_jumbo(self):
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

        request = requests.get(self.url, timeout=10, headers=headers)

        if request.status_code == 404:
            raise PageNotFoundException(self.url)

        soup = BeautifulSoup(request.text, "html.parser")
        product_json = soup.find("script", attrs={"type": "application/ld+json", "data-n-head": "ssr"})
        raw_json = product_json.string

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
            self.url = product["url"]
            self.name = product["name"]
            self.ean = product["gtin13"]
            self.product_code = product["sku"]
            self.discount_price = offer["lowPrice"]
            self.normal_price = offer["highPrice"]
        except KeyError as e:
            logging.error("%s, raising CrawlerException" % e, raw_json)
            raise CrawlerException from KeyError
