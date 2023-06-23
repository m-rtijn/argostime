"""
    crawler/shop/steam.py

    Crawler for store.steampowered.com

    Copyright (c) 2022 Martijn <martijn [at] mrtijn.nl>

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

from argostime.crawler.crawl_utils import CrawlResult, register_crawler
from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException

from bs4 import BeautifulSoup

import requests


@register_crawler("Steam", "store.steampowered.com", False)
def crawl_steam(url: str) -> CrawlResult:
    """Crawler for store.steampowered.com"""

    result: CrawlResult = CrawlResult(url=url)

    response: requests.Response = requests.get(url, timeout=10)

    if response.status_code != 200:
        logging.error("Got status code %d while getting url %s",
                      response.status_code, url)
        raise PageNotFoundException(url)

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the divs with class 'game_area_purchase_game'
    game_infos = soup.find_all(
        "div",
        "game_area_purchase_game"
        )

    game_info = None

    # Select first div with only one class attribute, or select last div
    for game_info in game_infos:
        if len(game_info['class']) > 1:
            continue
        break

    if game_info is None:
        logging.error("Couldn't find a valid game_info div crawling %s", url)
        raise CrawlerException()

    try:
        result.url = soup.find("meta", property="og:url").get("content")
    except Exception as exception:
        logging.info("Couldn't find Open Graph canonical URL %s", exception)

    try:
        result.product_name = game_info.find("h1").text.replace("Buy ", "")
    except Exception as exception:
        logging.error("Could not find a name in %s", game_info)
        raise CrawlerException from exception

    try:
        result.product_code = game_info.find(
            "input",
            attrs={
                "name": "subid",
                "type": "hidden"
                }
            ).get("value")
    except Exception as exception:
        logging.error("Could not find a product code in %s %s",
                      game_info, exception)
        raise CrawlerException from exception

    try:
        result.discount_price = float(
            game_info.find(
                "div",
                "discount_block",
                "game_purchase_discount"
                ).get("data-price-final")) / 100.0
        result.on_sale = True
        # There is info in the page about the normal price when there is a
        # discount, it's just more of a hassle to find that information
    except Exception as exception:
        logging.info("No discount found, looking for normal price %s",
                     exception)
        try:
            result.normal_price = float(
                game_info.find(
                    "div",
                    "game_purchase_price"
                    ).get("data-price-final")) / 100.0
        except Exception as inner_exception:
            logging.error("No normal price found in %s %s",
                          game_info, inner_exception)
            raise CrawlerException from inner_exception

    return result
