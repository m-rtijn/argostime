#!/usr/bin/env python3
"""
    crawler/__init__.py

    Abstraction layer between the crawler & database on one hand, and the actual web interface
    on the other.

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

from argostime.crawler.crawlresult import CrawlResult
from argostime.crawler.crawl_url import crawl_url
from argostime.crawler.shop_info import shops_info, enabled_shops