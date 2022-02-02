#!/usr/bin/env python3
"""
    crawler/crawlresult.py

    Data structure for returning the results of a crawler in a uniform way.

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

class CrawlResult():
    """Data structure which contains the result of crawling a page."""

    url: str
    product_name: str
    product_code: str
    ean: int

    normal_price: float
    discount_price: float = 0.0
    on_sale: bool = False

    def __init__(
        self,
        url: str=None,
        product_name: str=None,
        product_code: str=None,
        normal_price: float=-1.0,
        discount_price: float=-1.0,
        on_sale: bool=False,
        ean: int=None,
        ):
        self.url = url
        self.product_name = product_name
        self.product_code = product_code
        self.normal_price = normal_price
        self.discount_price = discount_price
        self.on_sale = on_sale
        self.ean = ean
