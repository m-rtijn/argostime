#!/usr/bin/env python3
"""
    graphs.py

    Create graphs using matplotlib

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

import datetime
import logging
from typing import List

from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.axes import Axes
import numpy as np

from argostime.exceptions import NoEffectivePriceAvailableException
from argostime.models import ProductOffer, Price

def generate_price_bar_graph(offer: ProductOffer) -> Figure:
    """Generate a bar graph with the price over time of a specific ProductOffer"""

    prices: List[Price] = Price.query.filter_by(product_offer_id=offer.id).order_by(Price.datetime).all()

    fig: Figure = Figure()
    ax: Axes = fig.subplots()

    effective_prices: List[float] = []
    dates: List[datetime.date] = []
    date_strings: List[str] = []

    for price in prices:
        try:
            effective_prices.append(price.get_effective_price())
            dates.append(price.datetime.date())
            date_strings.append(str(price.datetime.date()))
        except NoEffectivePriceAvailableException:
            pass

    logging.debug("%s", dates)
    logging.debug("%s", effective_prices)

    x_locations: List[float] = np.arange(len(dates))
    bar = ax.bar(x_locations, effective_prices)
    ax.set_ylabel("prijs in €")
    ax.set_xlabel("datum")
    ax.set_title("Prijsontwikkeling van {product} bij {shop}".format(product=offer.product.name, shop=offer.webshop.name))
    ax.set_xticks(x_locations, labels=date_strings)
    ax.bar_label(bar, fmt="€ %0.2f", label_type="edge")

    # Format y-axis ticks
    tick = mticker.StrMethodFormatter("€ {x:.2f}")
    ax.yaxis.set_major_formatter(tick)

    # Rotate x-axis labels
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')

    # Set margin to avoid annotations overlapping with top border
    ax.margins(0.1)

    # Add more space to bottom of plot to fit x-axis ticks and label
    fig.subplots_adjust(left=0.15, bottom=0.2)

    return fig

def generate_price_step_graph(offer: ProductOffer) -> Figure:
    """Generate a step graph with the price over time of a specific ProductOffer"""

    prices: List[Price] = Price.query.filter_by(product_offer_id=offer.id).order_by(Price.datetime).all()

    fig: Figure = Figure()
    ax: Axes = fig.subplots()

    effective_prices: List[float] = []
    dates: List[datetime.date] = []
    date_strings: List[str] = []

    for price in prices:
        try:
            effective_prices.append(price.get_effective_price())
            dates.append(price.datetime.date())
            date_strings.append(str(price.datetime.date()))
        except NoEffectivePriceAvailableException:
            pass

    x_locations: List[float] = np.arange(len(dates))

    ax.step(x_locations, effective_prices, "o-", where="mid")
    ax.grid(True)
    ax.set_ylabel("prijs in €")
    ax.set_xlabel("datum")
    ax.set_title("Prijsontwikkeling van {product} bij {shop}".format(product=offer.product.name, shop=offer.webshop.name))
    ax.set_xticks(x_locations, labels=date_strings)
    #ax.xaxis.set_major_locator(mdates.DayLocator())
    #ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

    # Format y-axis ticks
    tick = mticker.StrMethodFormatter("€ {x:.2f}")
    ax.yaxis.set_major_formatter(tick)

    # Rotate x-axis labels
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')

    # Add data labels in the plot
    for x, effective_price in zip(x_locations, effective_prices):
        label = "{:.2f}".format(effective_price)

        ax.annotate(
            label,
            (x,effective_price),
            textcoords="offset points",
            xytext=(0,5),
            ha="center"
            )

    # Set margin to avoid annotations overlapping with top border
    ax.margins(0.1)

    # Add more space to bottom of plot to fit x-axis ticks and label
    fig.subplots_adjust(left=0.15, bottom=0.2)

    return fig
