#!/usr/bin/env python3
"""
    __init__.py

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

import configparser
import logging

from flask import Flask

from .products import *
from .exceptions import *
from .models import *

def create_app():
    logging.basicConfig(
        filename="argostime.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        )
    logging.getLogger("matplotlib.font_manager").disabled = True

    config = configparser.ConfigParser()
    config.read("argostime.conf")
    app = Flask(__name__)

    logging.debug("Found sections %s in config", config.sections())

    if "mariadb" in config:
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{user}:{password}@{server}/{database}?charset=utf8mb4".format(
            user=config["mariadb"]["user"],
            password=config["mariadb"]["password"],
            server=config["mariadb"]["server"],
            database=config["mariadb"]["database"]
        )
        logging.debug(app.config["SQLALCHEMY_DATABASE_URI"])
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()
        return app
