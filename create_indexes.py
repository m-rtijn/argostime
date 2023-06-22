#!/usr/bin/env python
"""
    create_indexes.py

    Standalone script to add indexes in the database.

    Copyright (c) 2023 Martijn <martijn [at] mrtijn.nl>

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

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from argostime import create_app, db
from argostime.models import ProductOffer, Product, Price, Webshop

app = create_app()
app.app_context().push()

logging.info("Adding indexes")

indexes = [
    db.Index("idx_Price_datetime", Price.datetime),
    db.Index("idx_Price_product_offer", Price.product_offer_id),
    db.Index("idx_Price_product_offer_id_datetime", Price.product_offer_id, Price.datetime),
    db.Index("idx_ProductOffer_shop_id", ProductOffer.shop_id),
    db.Index("idx_ProductOffer_product_id", ProductOffer.product_id),
    db.Index("idx_Webshop_hostname", Webshop.hostname),
    db.Index("idx_Product_product_code", Product.product_code),
]

for index in indexes:
    try:
        index.create(db.engine)
    except OperationalError as e:
        logging.error("%s", e)
