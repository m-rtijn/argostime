#!/usr/bin/env python

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

logging.info("Calculate average prices")

offers = db.session.scalars(
    db.select(ProductOffer)
        .join(Product)
        .order_by(Product.name)
).all()

for offer in offers:
    logging.info("Calculating initial average price for %s", offer)
    offer.update_average_price()
