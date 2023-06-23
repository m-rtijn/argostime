"""
    exceptions.py

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

import logging


class PageNotFoundException(Exception):
    """Exception to throw when a request gets a 404 returned."""
    def __init__(self, url: str):
        self.url = url

        logging.debug("PageNotFoundException for %s", url)

        super().__init__()


class WebsiteNotImplementedException(Exception):
    """Exception to throw if a certain website has no implemented scraper."""

    def __init__(self, url: str):
        self.url = url

        logging.debug("WebsiteNotImplementedException for %s", url)

        super().__init__()


class NoEffectivePriceAvailableException(Exception):
    """Exception to throw if a Price object has no valid price."""


class CrawlerException(Exception):
    """Exception to throw if something goes wrong in the crawler."""
