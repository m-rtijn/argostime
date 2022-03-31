#!/usr/bin/env python3
"""
    crawler/crawl_url.py

    Crawler function exposed to the rest of the system to get pricing and product
    information from a given URL.

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

import logging
import urllib.parse

from argostime.exceptions import WebsiteNotImplementedException

from argostime.crawler.crawl_utils import CrawlResult
from argostime.crawler.shop_info import shops_info, enabled_shops

from argostime.crawler.ah import crawl_ah
from argostime.crawler.brandzaak import crawl_brandzaak
from argostime.crawler.etos import crawl_etos
from argostime.crawler.hema import crawl_hema
from argostime.crawler.jumbo import crawl_jumbo
from argostime.crawler.pipashop import crawl_pipashop
from argostime.crawler.simonlevelt import crawl_simonlevelt
from argostime.crawler.steam import crawl_steam
from argostime.crawler.ikea import crawl_ikea
from argostime.crawler.praxis import crawl_praxis
from argostime.crawler.gamma import crawl_gamma

def crawl_url(url: str) -> CrawlResult:
    """Crawl a product at the given URL

    Returns a CrawlResult object.
    May raise any of the following exceptions:
        PageNotFoundException
        WebsiteNotImplementedException
    """
    logging.debug("Crawling %s", url)
    hostname: str = urllib.parse.urlparse(url).netloc

    if hostname not in enabled_shops:
        raise WebsiteNotImplementedException(url)

    result: CrawlResult
    if shops_info["ah"]["hostname"] in hostname:
        result = crawl_ah(url)
    elif shops_info["jumbo"]["hostname"] in hostname:
        result = crawl_jumbo(url)
    elif shops_info["brandzaak"]["hostname"] in hostname:
        result = crawl_brandzaak(url)
    elif shops_info["etos"]["hostname"] in hostname:
        result = crawl_etos(url)
    elif shops_info["simonlevelt"]["hostname"] in hostname:
        result = crawl_simonlevelt(url)
    elif shops_info["hema"]["hostname"] in hostname:
        result = crawl_hema(url)
    elif shops_info["steam"]["hostname"] in hostname:
        result = crawl_steam(url)
    elif shops_info["pipashop"]["hostname"] in hostname:
        result = crawl_pipashop(url)
    elif shops_info["ikea"]["hostname"] in hostname:
        result = crawl_ikea(url)
    elif shops_info["praxis"]["hostname"] in hostname:
        result = crawl_praxis(url)
    elif shops_info["gamma"]["hostname"] in hostname:
        result = crawl_gamma(url)
    else:
        raise WebsiteNotImplementedException(url)

    if result.discount_price > 0:
        result.on_sale = True
    else:
        result.on_sale = False

    logging.debug("Crawl resulted in %s", result)

    return result
