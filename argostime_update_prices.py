#!/usr/bin/env python3
"""
    argostime_update_prices.py

    Part of Argostimè

    Standalone script to update prices in the database.
"""

import random
import logging
import time

from argostime.models import ProductOffer
from argostime import create_app

initial_sleep_time: float = random.uniform(0, 600)
logging.debug("Sleeping for %f", initial_sleep_time)
time.sleep(initial_sleep_time)

app = create_app()
app.app_context().push()

offer: ProductOffer
for offer in ProductOffer.query.all():
    logging.info("Crawling %s", str(offer))

    try:
        offer.crawl_new_price()
    except Exception as exception:
        logging.error("Received %s while updating price of %s, continuing...", exception, offer)

    next_sleep_time: float = random.uniform(1, 180)
    logging.debug("Sleeping for %f", next_sleep_time)
    time.sleep(next_sleep_time)
