#!/usr/bin/env python3
"""
    graphs.py

    Create graphs using Apache ECharts

    Copyright (c) 2022 Martijn <martijn [at] mrtijn.nl>
    Copyright (c) 2022 Kevin

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

from typing import List
import json

from argostime.exceptions import NoEffectivePriceAvailableException
from argostime.models import ProductOffer, Price

def generate_price_graph_data(offer: ProductOffer) -> str:
    """
        Generate the data needed to render a step graph with the price over
        time of a specific ProductOffer
    """

    prices: List[Price] = Price.query.filter_by(
        product_offer_id=offer.id).order_by(Price.datetime).all()

    effective_prices: List[float] = []
    date_strings: List[str] = []

    for price in prices:
        try:
            effective_prices.append(price.get_effective_price())
            date_strings.append(str(price.datetime.date()))
        except NoEffectivePriceAvailableException:
            pass

    data = {
        "title": {
            "text": f"Prijsontwikkeling van {offer.product.name} bij {offer.webshop.name}",
            "left": "center",
        },
        "tooltip": {
            "trigger": "axis",
            "formatter": "<center>{b}<br>€ {c}</center>",
        },
        "toolbox": {
            "feature": {
                "dataZoom": {
                    "yAxisIndex": "none",
                },
            },
        },
        "dataZoom": [
            {
                "type": "inside",
                "start": 0,
                "end": 100,
            },
            {
                "start": 0,
                "end": 100,
            },
        ],
        "xAxis": {
            "type": "category",
            "data": date_strings,
        },
        "yAxis": {
            "type": "value",
            "min": "dataMin",
            "max": "dataMax",
            "axisLabel": {
                "formatter": "€ {value}",
            },
        },
        "series": {
            "type": "line",
            "symbolSize": 10,
            "step": "middle",
            "data": effective_prices,
        },
    }

    return json.dumps(data)
