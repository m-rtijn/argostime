"""
    products.py

    Abstraction layer between the crawler & database on one hand, and the
    actual web interface on the other.

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

import urllib.parse
from datetime import datetime
from enum import Enum
from typing import Tuple

from argostime import db
from argostime.crawler import CrawlResult, crawl_url, enabled_shops
from argostime.exceptions import WebsiteNotImplementedException
from argostime.models import Price, Product, ProductOffer, Webshop


class ProductOfferAddResult(Enum):
    """Enum to indicate the result of add_product_offer"""
    GENERIC_FAILURE = 0
    ADDED = 1
    ALREADY_EXISTS = 2
    FAILED_404_NOT_FOUND = 3


def add_product_offer_from_url(url: str) -> \
        Tuple[ProductOfferAddResult, ProductOffer]:
    """
    Try to add a product offer to the database, add product and webshop if
    required.

    Returns a ProductOfferAddResult enum
    """
    hostname: str = urllib.parse.urlparse(url).netloc

    try:
        shop_info = enabled_shops[hostname]
    except KeyError as exception:
        raise WebsiteNotImplementedException(url) from exception

    shop: Webshop = db.session.scalar(
        db.select(Webshop)
            .where(Webshop.hostname.contains(shop_info["hostname"]))
    )

    # Add Webshop if it can't be found in the database
    if shop is None:
        shop = Webshop(name=shop_info["name"], hostname=shop_info["hostname"])
        db.session.add(shop)
        db.session.commit()

    # Check if this ProductOffer already exists
    product_offer: ProductOffer = db.session.scalar(
        db.select(ProductOffer)
            .where(ProductOffer.url == url)
    )
    if product_offer is not None:
        return (ProductOfferAddResult.ALREADY_EXISTS, product_offer)

    parse_results: CrawlResult = crawl_url(url)

    # Check if this Product already exists, otherwise add it to the database
    product: Product = db.session.scalar(
        db.select(Product)
            .where(Product.product_code == parse_results.product_code)
    )
    if product is None:
        product = Product(
            name=parse_results.product_name,
            description=parse_results.product_description,
            product_code=parse_results.product_code
        )
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
    offer.update_memoized_values()

    return (ProductOfferAddResult.ADDED, offer)
