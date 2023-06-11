#!/usr/bin/env python3
"""
    argostime_update_prices.py

    Standalone script to update prices in the database.

    Copyright (c) 2022, 2023 Martijn <martijn [at] mrtijn.nl>

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

import random
import logging
from multiprocessing import Process
import time

from argostime.models import ProductOffer, Webshop
from argostime import create_app, db

app = create_app()
app.app_context().push()

def update_shop_offers(shop_id: int) -> None:
    """Crawl all the offers of one shop"""

    offers_query = db.session.scalars(db.select(ProductOffer).where(ProductOffer.shop_id == shop_id))

    offer: ProductOffer
    for offer in offers_query.all():
        logging.info("Crawling %s", str(offer))

        try:
            offer.crawl_new_price()
        except Exception as exception:
            logging.error("Received %s while updating price of %s, continuing...", exception, offer)

        next_sleep_time: float = random.uniform(1, 180)
        logging.debug("Sleeping for %f seconds", next_sleep_time)
        time.sleep(next_sleep_time)

if __name__ == "__main__":

    shop_query = db.session.scalars(db.select(Webshop).order_by(Webshop.id)).all()

    for shop in shop_query.all():
        shop_process: Process = Process(
            target=update_shop_offers,
            args=[shop.id],
            name=f"ShopProcess({shop.id})")

        logging.info("Starting process %s", shop_process)
        shop_process.start()
