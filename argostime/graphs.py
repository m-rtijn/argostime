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

from typing import List, Tuple
from datetime import datetime, timedelta
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

    price_data: List[Tuple[str, float]] = []
    sales_data: List[List[datetime]] = [[]]

    for price in prices:
        try:
            price_data.append((
                str(price.datetime.replace(hour=0, minute=0, second=0, microsecond=0)),
                price.get_effective_price(),
            ))

            if price.on_sale:
                sales_data[-1].append(price.datetime.replace(hour=0, minute=0, second=0, microsecond=0))
            elif sales_data[-1] != []:
                sales_data.append([])
        except NoEffectivePriceAvailableException:
            pass
    
    if sales_data[-1] == []:
        sales_data = sales_data[:-1]

    data = {
        "title": {
            "text": f"Prijsontwikkeling van {offer.product.name} bij {offer.webshop.name}",
            "left": "center",
        },
        "tooltip": {
            "trigger": "axis",
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
                "filterMode": "none",
                "start": 0,
                "end": 100,
            },
            {
                "start": 0,
                "end": 100,
            },
        ],
        "xAxis": {
            "type": "time",
            "axisLabel": {
                "formatter": "{yyyy}-{MM}-{dd}",
            },
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
            "name": offer.product.name,
            "type": "line",
            "symbolSize": 10,
            "step": "middle",
            "data": price_data,
            "markArea": {
                "silent": True,
                "itemStyle": {
                    "color": "rgba(255, 165, 0, 0.5)",
                },
                "data": [
                    [
                        {
                            "name": "Korting!",
                            "xAxis": str(sale[0] - timedelta(hours=12)),
                        },
                        {
                            "xAxis": str(sale[-1] + timedelta(hours=12)),
                        },
                    ]
                    for sale in sales_data
                ],
            },
        },
    }

    return json.dumps(data)
