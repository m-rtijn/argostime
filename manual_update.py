#!/usr/bin/env python3
"""
    manual_update.py

    Standalone script to manually update the price of a product offer by product_offer_id.

    Copyright (c) 2022 Kevin

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

import sys
import logging

from argostime import create_app, db
from argostime.models import ProductOffer

app = create_app()
app.app_context().push()

try:
    product_offer_id: int = int(sys.argv[1])
except:
    print("No number given")
    sys.exit(-1)

offer: ProductOffer = db.session.execute(db.select(ProductOffer).where(ProductOffer.id == product_offer_id)).scalar_one()

logging.debug("Found offer %s", product_offer_id)
logging.debug("Manually updating ProductOffer %s", offer)

try:
    offer.crawl_new_price()
except Exception as exception:
    logging.error("Received %s while updating price of %s, continuing...", exception, offer)
