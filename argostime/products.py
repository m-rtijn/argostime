#!/usr/bin/env python3
"""
    products.py

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

from enum import Enum
from datetime import datetime
from typing import Tuple
import urllib.parse

from .exceptions import WebsiteNotImplementedException
from .models import Webshop, Price, Product, ProductOffer, db
from .crawler import ParseProduct, enabled_shops, shops_info

class ProductOfferAddResult(Enum):
    """Enum to indicate the result of add_product_offer"""
    GENERIC_FAILURE = 0
    ADDED = 1
    ALREADY_EXISTS = 2
    FAILED_404_NOT_FOUND = 3

def add_product_offer_from_url(url: str) -> Tuple[ProductOfferAddResult, ProductOffer]:
    """Try to add a product offer to the database, add product and webshop if required.

    Returns a ProductOfferAddResult enum
    """
    hostname: str = urllib.parse.urlparse(url).netloc

    try:
        shop_info = shops_info[enabled_shops[hostname]]
    except KeyError:
        raise WebsiteNotImplementedException(url) from KeyError

    shop: Webshop = Webshop.query.filter(Webshop.hostname.contains(shop_info["hostname"])).first()

    # Add Webshop if it can't be found in the database
    if shop is None:
        shop = Webshop(name=shop_info["name"], hostname=shop_info["hostname"])
        db.session.add(shop)
        db.session.commit()

    # Check if this ProductOffer already exists
    product_offer: ProductOffer = ProductOffer.query.filter_by(url=url).first()
    if product_offer is not None:
        return (ProductOfferAddResult.ALREADY_EXISTS, product_offer)

    parse_results: ParseProduct = ParseProduct(url)

    # Check if this Product already exists, otherwise add it to the database
    product: Product = Product.query.filter_by(product_code=parse_results.product_code).first()
    if product is None:
        product = Product(name=parse_results.name, product_code=parse_results.product_code)
        db.session.add(product)
        db.session.commit()

    offer: ProductOffer = ProductOffer(
        product_id=product.id,
        shop_id=shop.id,
        url=url,
        time_added=datetime.now()
    )
    db.session.add(offer)
    db.session.commit()

    on_sale: bool = False
    if parse_results.discount_price > 0:
        on_sale = True

    price: Price = Price(
        normal_price=parse_results.normal_price,
        discount_price=parse_results.discount_price,
        on_sale=on_sale,
        product_offer_id=offer.id,
        datetime=datetime.now()
    )
    db.session.add(price)
    db.session.commit()

    return (ProductOfferAddResult.ADDED, offer)
