"""
    models.py

    Database model classes using SQLAlchemy

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
import statistics
from datetime import datetime
from sys import maxsize
from typing import List

from argostime import db
from argostime.crawler import CrawlResult, crawl_url
from argostime.exceptions import \
    CrawlerException, WebsiteNotImplementedException
from argostime.exceptions import NoEffectivePriceAvailableException
from argostime.exceptions import PageNotFoundException


class Webshop(db.Model):  # type: ignore
    """A webshop, which may offer products."""
    __tablename__ = "Webshop"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(512), unique=True, nullable=False)
    hostname = db.Column(db.Unicode(512), unique=True, nullable=False)
    products = db.relationship("ProductOffer", backref="webshop", lazy=True,
                               cascade="all, delete", passive_deletes=True)

    def __str__(self) -> str:
        return f"Webshop(id={self.id}, name={self.name}, " \
               f"hostname={self.hostname})"


class Product(db.Model):  # type: ignore
    """A product, which may be sold by multiple webshops."""
    __tablename__ = "Product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(512), nullable=False)
    description = db.Column(db.Unicode(1024))
    ean = db.Column(db.Integer)
    product_code = db.Column(db.Unicode(512), unique=True)
    product_offers = db.relationship("ProductOffer", backref="product",
                                     lazy=True, cascade="all, delete",
                                     passive_deletes=True)

    def __str__(self) -> str:
        return (f"Product(id={self.id}, name={self.name}, "
                f"description={self.description}, ean={self.ean}, "
                f"product_code={self.product_code}, "
                f"product_offers={self.product_offers})")


class Price(db.Model):  # type: ignore
    """Pricing information of a specific ProductOffer at some point in time."""
    __tablename__ = "Price"
    id = db.Column(db.Integer, primary_key=True)
    normal_price = db.Column(db.Float)
    discount_price = db.Column(db.Float)
    on_sale = db.Column(db.Boolean)
    datetime = db.Column(db.DateTime)
    product_offer_id = db.Column(
        db.Integer,
        db.ForeignKey("ProductOffer.id", ondelete="CASCADE"),
        nullable=False
    )

    def __str__(self) -> str:
        return (f"Price(id={self.id}, normal_price={self.normal_price},"
                f"discount_price={self.discount_price}, on_sale={self.on_sale}"
                f"datetime={self.datetime}, "
                f"product_offer_id={self.product_offer_id})")

    def get_effective_price(self) -> float:
        """Return the discounted price if on sale, else the normal price."""
        if self.on_sale:
            return self.discount_price
        else:
            if self.normal_price >= 0:
                return self.normal_price
            else:
                raise NoEffectivePriceAvailableException


class ProductOffer(db.Model):  # type: ignore
    """An offer of a Webshop to sell a specific product."""
    __tablename__ = "ProductOffer"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer,
                           db.ForeignKey("Product.id", ondelete="CASCADE"),
                           nullable=False)
    shop_id = db.Column(db.Integer,
                        db.ForeignKey("Webshop.id", ondelete="CASCADE"),
                        nullable=False)
    url = db.Column(db.Unicode(1024), unique=True, nullable=False)
    time_added = db.Column(db.DateTime)
    average_price = db.Column(db.Float)
    minimum_price = db.Column(db.Float)
    maximum_price = db.Column(db.Float)
    # TODO: Memoize current price with reference to the most recent Price entry

    prices = db.relationship("Price", backref="product_offer", lazy=True,
                             cascade="all, delete", passive_deletes=True)

    def __str__(self):
        return (f"ProductOffer(id={self.id}, product_id={self.product_id}, "
                f"shop_id={self.shop_id}, url={self.url}, "
                f"time_added={self.time_added})")

    def get_current_price(self) -> Price:
        """Get the latest Price object related to this offer."""

        price = db.session.scalar(
            db.select(Price)
                .where(Price.product_offer_id == self.id)
                .order_by(Price.datetime.desc())
                .limit(1)
        )

        return price

    def update_average_price(self) -> float:
        """
        Calculate the average price of this offer and update
        ProductOffer.average_price.
        """
        logging.debug("Updating average price for %s", self)
        effective_price_values: List[float] = []

        prices = db.session.scalars(
            db.select(Price)
                .where(Price.product_offer_id == self.id)
        ).all()

        for price in prices:
            try:
                effective_price_values.append(price.get_effective_price())
            except NoEffectivePriceAvailableException:
                # Ignore price entries without a valid price.
                pass
        try:
            avg: float = statistics.mean(effective_price_values)
            self.average_price = avg
            db.session.commit()
            return avg
        except statistics.StatisticsError:
            logging.debug("Called get_average_price for %s but no prices were "
                          "found...", str(self))
            return -1

    def get_average_price(self) -> float:
        """Stub for new .average_price attribute

        DEPRECATED: Use ProductOffer.average_price instead.
        """
        return self.average_price

    def get_prices_since(self, since_time: datetime) -> list[Price]:
        """Get all prices since given date"""
        prices_since = db.session.scalars(
            db.select(Price)
                .where(Price.product_offer_id == self.id)
                .where(Price.datetime >= since_time)
        ).all()

        prices_since_list: list[Price] = []
        for price in prices_since:
            prices_since_list.append(price)

        return prices_since_list

    def get_lowest_price_since(self, since_time: datetime) -> float:
        """
        Return the lowest effective price of this offer since a specific time.
        """
        logging.debug("Calculating lowest price since %s for %s",
                      since_time, self)
        min_price: float = maxsize
        price: Price

        prices_since = self.get_prices_since(since_time)

        for price in prices_since:
            try:
                if price.get_effective_price() < min_price:
                    min_price = price.get_effective_price()
            except NoEffectivePriceAvailableException:
                # Ignore price entries without a valid price
                pass

        return min_price

    def update_minimum_price(self) -> None:
        """Update the minimum price ever in the minimum column"""

        min_price: float = self.get_lowest_price_since(self.time_added)
        self.minimum_price = min_price
        db.session.commit()

    def get_lowest_price(self) -> float:
        """Return the lowest effective price of this offer.

        DEPRECATED: Use ProductOffer.minimum_price instead
        """
        return self.minimum_price

    def get_highest_price_since(self, since_time: datetime) -> float:
        """
        Return the highest effective price of this offer since a specific time.
        """
        logging.debug("Calculating highest price since %s for %s",
                      since_time, self)
        max_price: float = -1
        price: Price

        prices_since = self.get_prices_since(since_time)

        for price in prices_since:
            try:
                if price.get_effective_price() > max_price:
                    max_price = price.get_effective_price()
            except NoEffectivePriceAvailableException:
                pass

        return max_price

    def update_maximum_price(self) -> None:
        """Update the maximum price ever in the maximum_price column"""

        max_price: float = self.get_highest_price_since(self.time_added)
        self.maximum_price = max_price
        db.session.commit()

    def get_highest_price(self) -> float:
        """Return the highest effective price of this offer.

        DEPRECATED: Use ProductOffer.maximum_price instead.
        """
        return self.maximum_price

    def get_price_standard_deviation_since(self, since_time: datetime) \
            -> float:
        """
        Return the standard deviation of the effective price of this offer
        since a given date.
        """
        effective_prices: List[float] = []
        price: Price

        prices_since = self.get_prices_since(since_time)

        for price in prices_since:
            try:
                effective_prices.append(price.get_effective_price())
            except NoEffectivePriceAvailableException:
                pass

        if len(effective_prices) > 1:
            return statistics.stdev(effective_prices)
        else:
            return 0.0

    def get_price_standard_deviation(self) -> float:
        """
        Return the standard deviation of the effective price of this offer.
        """
        return self.get_price_standard_deviation_since(self.time_added)

    def update_memoized_values(self) -> None:
        """Update all memoized columns"""

        self.update_average_price()
        self.update_minimum_price()
        self.update_maximum_price()

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
            logging.error(
                "Received a PageNotFoundException in %s, is"
                "seems that the product is no longer available?", str(self))
        except CrawlerException as exception:
            logging.error(
                "Received CrawlerException in %s, couldn't update price %s",
                str(self),
                exception
                )
            return
        except WebsiteNotImplementedException as exception:
            logging.error("Disabled website for existing product %s", self)
            raise WebsiteNotImplementedException(self.url) from exception

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

        self.update_memoized_values()
