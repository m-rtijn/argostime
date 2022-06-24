#!/usr/bin/env python3
"""
    crawler/crawl_url.py

    Crawler function exposed to the rest of the system to get pricing and product
    information from a given URL.

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

import logging
import urllib.parse

from argostime.exceptions import WebsiteNotImplementedException

from argostime.crawler.crawl_utils import CrawlResult, shops_info, enabled_shops


def crawl_url(url: str) -> CrawlResult:
    """Crawl a product at the given URL

    Returns a CrawlResult object.
    May raise any of the following exceptions:
        PageNotFoundException
        WebsiteNotImplementedException
    """
    logging.debug("Crawling %s", url)
    hostname: str = urllib.parse.urlparse(url).netloc

    if hostname not in enabled_shops or enabled_shops[hostname] not in shops_info:
        raise WebsiteNotImplementedException(url)

    result: CrawlResult = shops_info[enabled_shops[hostname]]["function"](url)  # type: ignore

    if result.discount_price > 0:
        result.on_sale = True
    else:
        result.on_sale = False

    logging.debug("Crawl resulted in %s", result)

    return result
