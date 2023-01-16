#!/usr/bin/env python3
"""
    __init__.py

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

# Configure the logger before anything else, so it can be used in decorators!
import logging
logging.basicConfig(
    filename="argostime.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
)

from os.path import dirname
from subprocess import run

import configparser

from flask import Flask

from argostime.products import *
from argostime.exceptions import *
from argostime.models import *

def get_current_commit() -> str:
    """Return the hexadecimal hash of the current running commit."""
    path = dirname(__file__)
    hexsha = run(
        ["git", "-C", path, "log", "-n", "1", "--pretty=format:%H"],
        capture_output=True,
        encoding="UTF-8",
    ).stdout
    return hexsha.strip() if hexsha else ""

def create_app():
    """Return a flask object for argostime, initialize logger and db."""
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

    app.config["GIT_CURRENT_COMMIT"] = get_current_commit()
    db.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()
        return app
