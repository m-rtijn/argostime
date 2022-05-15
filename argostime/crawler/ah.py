#!/usr/bin/env python3
"""
    crawler/ah.py

    Crawler for ah.nl

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

from datetime import date
import logging
import re
import requests

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from argostime.crawler.crawl_utils import CrawlResult

def crawl_ah(url: str) -> CrawlResult:
    """Crawler for ah.nl"""

    product_id_re = re.search(r"\/wi(\d+)\/", url)
    if not product_id_re:
        logging.error("No product ID found in URL %s", url)
        raise PageNotFoundException(url)

    product_id = product_id_re.group(1)

    response = requests.get(f"https://www.ah.nl/zoeken/api/products/product?webshopId={product_id}")

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s", response.status_code, url)
        raise PageNotFoundException(url)

    try:
        product = response.json()['card']['products'][0]
    except Exception as exception:
        logging.error("Could not obtain product data for product id %s", product_id)
        raise CrawlerException from exception

    result: CrawlResult = CrawlResult(url=url)

    try:
        result.product_name = product["title"]
    except KeyError as exception:
        logging.error("No key title found in json %s", product)
        raise CrawlerException from exception

    try:
        result.ean = product["gtins"][0]
    except KeyError:
        # Don't crash because the ean is not strictly necessarry
        logging.info("No key gtins found in json %s", product)
    except IndexError:
        logging.info("No ean found in json %s", product)

    try:
        result.product_code = f"wi{product['id']}"
    except KeyError as exception:
        logging.error("No key id found in json %s", product)
        raise CrawlerException from exception

    try:
        price = product["price"]
    except KeyError as exception:
        logging.error("No key price found in json %s", product)
        raise CrawlerException from exception

    if price is not dict:
        logging.error("No valid price found for %s", url)

    try:
        price_now : float = float(price["now"])
    except KeyError as exception:
        logging.error("Could not find a price for url %s", url)
        raise CrawlerException from exception

    if "discount" in product:
        discount = product['discount']

        bonus_from : date = date(year=2000, month=1, day=1)
        try:
            bonus_from = date.fromisoformat(discount['startDate'])
        except KeyError:
            logging.error("No key startDate found in dict %s", discount)
        except ValueError:
            logging.error(
                "Failed to parse startDate %s, assuming bonus is valid",
                discount['startDate']
                )

        bonus_until : date = date(year=5000, month=12, day=31)
        try:
            bonus_until = date.fromisoformat(discount['endDate'])
        except KeyError:
            logging.error("No key endDate found in dict %s", discount)
        except ValueError:
            logging.error(
                "Failed to parse priceValidUntil %s, using fallback",
                discount["endDate"]
                )

        if bonus_from <= date.today() <= bonus_until:
            result.discount_price = price_now
        else:
            # "now" price includes discount that isn't active
            try:
                price_was: float = float(price["was"])
            except KeyError:
                logging.error("Could not find old price for product %s, using discounted price", url)
                price_was = price_now

            result.normal_price = price_was
    else:
        result.normal_price = price_now

    return result
