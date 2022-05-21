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
    },
    "brandzaak": {
        "name": "Brandzaak",
        "hostname": "brandzaak.nl"
    },
    "etos": {
        "name": "Etos",
        "hostname": "etos.nl"
    },
    "simonlevelt": {
        "name": "Simon Lévelt",
        "hostname": "simonlevelt.nl"
    },
    "hema": {
        "name": "HEMA",
        "hostname": "hema.nl"
    },
    "steam": {
        "name": "Steam",
        "hostname": "store.steampowered.com"
    },
    "pipashop": {
        "name": "Pipa Shop",
        "hostname": "pipa-shop.nl"
    },
    "ikea": {
        "name": "IKEA",
        "hostname": "ikea.com"
    },
    "praxis": {
        "name": "Praxis",
        "hostname": "praxis.nl"
    },
    "gamma": {
        "name": "Gamma",
        "hostname": "gamma.nl"
    },
    "karwei": {
        "name": "Karwei",
        "hostname": "karwei.nl"
    },
    "ekoplaza": {
        "name": "Ekoplaza",
        "hostname": "ekoplaza.nl"
    }
}

enabled_shops = {
    "ah.nl": "ah",
    "www.ah.nl": "ah",
    "jumbo.com": "jumbo",
    "www.jumbo.com": "jumbo",
    "brandzaak.nl": "brandzaak",
    "www.brandzaak.nl": "brandzaak",
    "etos.nl": "etos",
    "www.etos.nl": "etos",
    "simonlevelt.nl": "simonlevelt",
    "www.simonlevelt.nl": "simonlevelt",
    "hema.nl": "hema",
    "www.hema.nl": "hema",
    "store.steampowered.com": "steam",
    "pipa-shop.nl": "pipashop",
    "www.pipa-shop.nl": "pipashop",
    "www.ikea.com": "ikea",
    "www.praxis.nl": "praxis",
    "www.gamma.nl": "gamma",
    "www.karwei.nl": "karwei",
    "www.ekoplaza.nl": "ekoplaza",
}
