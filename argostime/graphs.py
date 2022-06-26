#!/usr/bin/env python3
"""
    graphs.py

    Create graphs using Apache ECharts

    Copyright (c) 2022 Martijn <martijn [at] mrtijn.nl>
    Copyright (c) 2022 Kevin <kevin [at] 2sk.nl>

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

    dates: List[datetime] = []
    effective_prices: List[float] = []
    sales_index: List[Tuple[int, int]] = []
    sales_dates: List[Tuple[datetime, datetime]] = []

    index = 0
    for price in prices:
        try:
            effective_prices.append(price.get_effective_price())
            dates.append(price.datetime.replace(hour=12, minute=0, second=0, microsecond=0))

            if price.on_sale:
                if len(sales_index) == 0 or sales_index[-1][1] != (index - 1):
                    sales_index.append((index, index))
                else:
                    sales_index[-1] = (sales_index[-1][0], index)
            
            index += 1
        except NoEffectivePriceAvailableException:
            pass
    
    for sale in sales_index:
        start: datetime
        end: datetime

        if sale[0] == 0:
            start = dates[sale[0]] - timedelta(hours=12)
        else:
            start = dates[sale[0]] - (dates[sale[0]] - dates[sale[0]-1]) / 2
        
        if sale[1] == len(dates)-1:
            end = dates[sale[1]] + timedelta(hours=12)
        else:
            end = dates[sale[1]] + (dates[sale[1] + 1] - dates[sale[1]]) / 2

        sales_dates.append((start, end))

    # Choose a font size for the title of the graph based on the expected
    # title length. Longer titles will be rendered using a smaller font size
    # in order to fit on one line.
    title_size = 24
    if len(offer.product.name) + len(offer.webshop.name) > 40:
        title_size = 18
    if len(offer.product.name) + len(offer.webshop.name) > 65:
        title_size = 12

    data = {
        "title": {
            "text": f"Prijsontwikkeling van {offer.product.name} bij {offer.webshop.name}",
            "left": "center",
            "textStyle": {
                "color": "#000",
                "fontSize": title_size,
            },
        },
        "series": {
            "name": offer.product.name,
            "type": "line",
            "symbolSize": 10,
            "step": "middle",
            "data": list(zip([str(date) for date in dates], effective_prices)),
            "markArea": {
                "silent": True,
                "label": {
                    "color": "#000",
                    "fontSize": 18,
                },
                "itemStyle": {
                    "color": "rgba(255, 165, 0, 0.5)",
                },
                "data": [
                    [
                        {
                            "name": "Korting!",
                            "xAxis": str(start)
                        },
                        {
                            "xAxis": str(end)
                        },
                    ]
                    for (start, end) in sales_dates
                ],
            },
        },
    }

    return json.dumps(data)
