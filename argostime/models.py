#!/usr/bin/env python3
"""
    models.py

    Database model classes using SQLAlchemy

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

from datetime import datetime
import logging
import statistics
from sys import maxsize
from typing import List

from flask_sqlalchemy import SQLAlchemy

from argostime.crawler import crawl_url, CrawlResult
from argostime.exceptions import CrawlerException, WebsiteNotImplementedException
from argostime.exceptions import PageNotFoundException
from argostime.exceptions import NoEffectivePriceAvailableException

db: SQLAlchemy = SQLAlchemy()

class Webshop(db.Model):
    """A webshop, which may offer products."""
    __tablename__ = "Webshop"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(512), unique=True, nullable=False)
    hostname = db.Column(db.Unicode(512), unique=True, nullable=False)
    products = db.relationship("ProductOffer",
                                backref="webshop",
                                lazy=True, cascade="all, delete", passive_deletes=True)


class Product(db.Model):
    """A product, which may be sold by multiple webshops."""
    __tablename__ = "Product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(512), nullable=False)
    ean = db.Column(db.Integer)
    product_code = db.Column(db.Unicode(512), unique=True)
    product_offers = db.relationship("ProductOffer",
                                        backref="product", lazy=True,
                                        cascade="all, delete", passive_deletes=True)


class Price(db.Model):
    """Pricing information of a specific ProductOffer at some point in time."""
    __tablename__ = "Price"
    id = db.Column(db.Integer, primary_key=True)
    normal_price = db.Column(db.Float)
    discount_price = db.Column(db.Float)
    on_sale = db.Column(db.Boolean)
    datetime = db.Column(db.DateTime)
    product_offer_id = db.Column(db.Integer,
                                    db.ForeignKey("ProductOffer.id", ondelete="CASCADE"),
                                    nullable=False)

    def get_effective_price(self) -> float:
        """Return the discounted price if on sale, else the normal price."""
        if self.on_sale:
            return self.discount_price
        else:
            if self.normal_price >= 0:
                return self.normal_price
            else:
                raise NoEffectivePriceAvailableException


class ProductOffer(db.Model):
    """An offer of a Webshop to sell a specific product."""
    __tablename__ = "ProductOffer"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer,
                            db.ForeignKey("Product.id", ondelete="CASCADE"), nullable=False)
    shop_id = db.Column(db.Integer,
                            db.ForeignKey("Webshop.id", ondelete="CASCADE"), nullable=False)
    url = db.Column(db.Unicode(1024), unique=True, nullable=False)
    time_added = db.Column(db.DateTime)
    prices = db.relationship("Price", backref="product_offer", lazy=True,
                                cascade="all, delete", passive_deletes=True)

    def __str__(self):
        return f"ProductOffer(id={self.id}, product_id={self.product_id},"\
            f"shop_id={self.shop_id}, url={self.url}, time_added={self.time_added})"

    def get_current_price(self) -> Price:
        """Get the latest Price object related to this offer."""
        return Price.query.filter_by(product_offer_id=self.id).order_by(Price.datetime.desc()).first()

    def get_average_price(self) -> float:
        """Calculate the average price of this offer."""
        effective_price_values: List[float] = []
        for price in Price.query.filter_by(product_offer_id=self.id).all():
            try:
                effective_price_values.append(price.get_effective_price())
            except NoEffectivePriceAvailableException:
                # Ignore price entries without a valid price in calculating the price.
                pass
        try:
            return statistics.mean(effective_price_values)
        except statistics.StatisticsError:
            logging.info("Called get_average_price but no prices were found...")
            return -1

    def get_lowest_price_since(self, since_time: datetime) -> float:
        """Return the lowest effective price of this offer since a specific time."""
        min_price: float = maxsize
        price: Price
        for price in Price.query.filter(
                Price.product_offer_id == self.id,
                Price.datetime >= since_time).all():
            try:
                if price.get_effective_price() < min_price:
                    min_price = price.get_effective_price()
            except NoEffectivePriceAvailableException:
                # Ignore price entries without a valid price
                pass

        return min_price

    def get_lowest_price(self) -> float:
        """Return the lowest effective price of this offer."""
        return self.get_lowest_price_since(self.time_added)

    def get_highest_price_since(self, since_time: datetime) -> float:
        """Return the highest effective price of this offer since a specific time."""
        max_price: float = -1
        price: Price
        for price in Price.query.filter(
                Price.product_offer_id == self.id,
                Price.datetime >= since_time).all():
            try:
                if price.get_effective_price() > max_price:
                    max_price = price.get_effective_price()
            except NoEffectivePriceAvailableException:
                pass

        return max_price

    def get_highest_price(self) -> float:
        """Return the highest effective price of this offer."""
        return self.get_highest_price_since(self.time_added)

    def crawl_new_price(self) -> None:
        """Crawl the current price if we haven't already checked today."""
        latest_price: Price = self.get_current_price()

        if latest_price.datetime.date() >= datetime.now().date():
            # Don't update if we already checked today.
            logging.info("No update needed for %s", str(self))
            return

        try:
            parse_result: CrawlResult = crawl_url(self.url)
        except PageNotFoundException:
            logging.error("Received a PageNotFoundexception in %s", str(self))
        except CrawlerException:
            logging.error("Received CrawlerException in %s", str(self))
            return
        except WebsiteNotImplementedException:
            logging.error("Disabled website for existing product %s", self)
            raise WebsiteNotImplementedException(self.url) from WebsiteNotImplementedException

        on_sale: bool = False
        if parse_result.discount_price > 0:
            on_sale = True

        price: Price = Price(
            normal_price=parse_result.normal_price,
            discount_price=parse_result.discount_price,
            on_sale=on_sale,
            product_offer_id=self.id,
            datetime=datetime.now()
        )
        db.session.add(price)
        db.session.commit()
