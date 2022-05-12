from datetime import date
import json
import logging
from pprint import pprint


import requests
from bs4 import BeautifulSoup

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException
from argostime.crawler.crawl_utils import CrawlResult


def crawl_ekoplaza(url: str):  # -> CrawlResult:
    """Ekoplaza crawler"""

    info = url.split('product/')[-1]
    response = requests.get(
        f'https://www.ekoplaza.nl/api/aspos/products/url/{info}')

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s",
                      response.status_code, url)
        raise PageNotFoundException(url)
    try:
        product = response.json()["Product"]
    except KeyError as exception:
        logging.error("No product found at %s", url)
        raise CrawlerException from exception

    result = CrawlResult(url=url)

    result.url = url
    try:
        result.product_name = product['Description'].title()
    except KeyError as exception:
        logging.error("No product name found in %s", product)
        raise CrawlerException from exception

    try:
        result.product_code = product['DefaultScanCode']['Code']  # EAN ?
    except KeyError as exception:
        logging.error("No product code found in %s", product)
        raise CrawlerException from exception

    try:
        result.discount_price = float(product['Discount']['PriceInclTax'])
    except KeyError:
        pass

    try:
        result.normal_price = float(product['PriceInclTax'])
    except KeyError as exception:
        logging.error("No normal price found in %s", product)
        raise CrawlerException from exception

    return result
