#!/usr/bin/env python3
"""
    manual_update.py

    Part of Argostimè

    Standalone script to manually update the price of a product offer by product_offer_id.
"""

import sys
import logging

from argostime.models import ProductOffer
from argostime import create_app

app = create_app()
app.app_context().push()


try:
    product_offer_id: int = int(sys.argv[1])
except:
    print("No number given")
    sys.exit(-1)

offer: ProductOffer = ProductOffer.query.get(product_offer_id)

logging.debug("Found offer %s", product_offer_id)
logging.debug("Manually updating ProductOffer %s", offer)

try:
    offer.crawl_new_price()
except Exception as exception:
    logging.error("Received %s while updating price of %s, continuing...", exception, offer)
