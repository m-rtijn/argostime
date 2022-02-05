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

time.sleep(random.uniform(0, 600))

app = create_app()
app.app_context().push()

offer: ProductOffer
for offer in ProductOffer.query.all():
    logging.info("Crawling %s", str(offer))
    offer.crawl_new_price()
    time.sleep(1 + random.uniform(1, 60))
