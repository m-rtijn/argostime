#!/usr/bin/env python3
"""
    crawler/shop_info.py

    Contains information about supported webshops

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

shops_info = {
    "ah": {
        "name": "Albert Heijn",
        "hostname": "ah.nl"
    },
    "jumbo": {
        "name": "Jumbo",
        "hostname": "jumbo.com"
    }
}

enabled_shops = {
    "ah.nl": "ah",
    "www.ah.nl": "ah",
    "jumbo.com": "jumbo",
    "www.jumbo.com": "jumbo"
}
