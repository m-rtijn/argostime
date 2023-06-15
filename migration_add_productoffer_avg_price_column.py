#!/usr/bin/env python
"""
    argostime_update_prices.py

    Standalone script to add new columns added in the sqlalchemy-v2 branch.

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
from argostime.models import ProductOffer, Product

app = create_app()
app.app_context().push()

logging.info("Adding average_price column")

try:
    db.session.execute(text('ALTER TABLE ProductOffer ADD COLUMN average_price float'))
except OperationalError:
    logging.info("Column already seems to exist, fine")

try:
    db.session.execute(text('ALTER TABLE ProductOffer ADD COLUMN minimum_price float'))
except OperationalError:
    logging.info("Column already seems to exist, fine")

try:
    db.session.execute(text('ALTER TABLE ProductOffer ADD COLUMN maximum_price float'))
except OperationalError:
    logging.info("Column already seems to exist, fine")

logging.info("Calculate average prices")

offers = db.session.scalars(
    db.select(ProductOffer)
        .join(Product)
        .order_by(Product.name)
).all()

offer: ProductOffer
for offer in offers:
    logging.info("Calculating initial memoization values for %s", offer)
    offer.update_memoized_values()
