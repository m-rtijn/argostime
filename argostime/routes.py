#!/usr/bin/env python3
"""
    routes.py

    Flask routes

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

from datetime import datetime
import logging
from typing import List, Dict
import urllib.parse

from flask import current_app as app
from flask import render_template, abort, request, redirect
from flask import Response

from argostime import db
from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException
from argostime.exceptions import WebsiteNotImplementedException
from argostime.graphs import generate_price_graph_data
from argostime.models import Webshop, Product, ProductOffer, Price
from argostime.products import ProductOfferAddResult, add_product_offer_from_url

def add_product_url(url):
    try:
        res, offer = add_product_offer_from_url(url)
    except WebsiteNotImplementedException:
        hostname: str = urllib.parse.urlparse(url).netloc
        if len(hostname) == 0:
            hostname = url
        return render_template("add_product_result.html.jinja",
            result=f"Helaas wordt de website {hostname} nog niet ondersteund."), 400
    except PageNotFoundException:
        return render_template("add_product_result.html.jinja",
            result=f"De pagina {url} kon niet worden gevonden."), 404
    except CrawlerException as exception:
        logging.info(
            "Failed to add product from url %s, got CrawlerException %s",
            url,
            exception)

        return render_template("add_product_result.html.jinja",
            result=f"Het is niet gelukt om een product te vinden op de gegeven URL {url}."
                    " Verwijst de link wel naar een productpagina?")

    if (
        res == ProductOfferAddResult.ADDED
        or
        res == ProductOfferAddResult.ALREADY_EXISTS and offer is not None
        ):
        return redirect(f"/product/{offer.product.product_code}")

    return render_template("add_product.html.jinja", result=str(res))

@app.route("/", methods=["GET", "POST"])
def index():
    """Render home page"""
    if request.method == "POST":
        return add_product_url(request.form["url"])
    else:
        recently_added_products = db.session.scalars(
                db.select(Product).order_by(Product.id.desc()).limit(5)
            ).all()

        discounts = db.session.scalars(
                db.select(Price).where(
                    Price.datetime >= datetime.now().date(),
                    Price.on_sale == True # pylint: disable=C0121
                )
            ).all()

        discounts.sort(key=lambda x: x.product_offer.product.name)
        shops = db.session.scalars(
            db.select(Webshop)
                .order_by(Webshop.name)
        ).all()

        return render_template(
            "index.html.jinja",
            products=recently_added_products,
            discounts=discounts,
            shops=shops)

@app.route("/product/<product_code>")
def product_page(product_code):
    """Show the page for a specific product, with all known product offers"""

    product: Product = db.session.scalars(
        db.select(Product)
            .where(Product.product_code == product_code)
    ).first()

    logging.debug("Rendering product page for %s based on product code %s", product, product_code)

    if product is None:
        abort(404)

    offers: List[ProductOffer] = db.session.scalars(
        db.select(ProductOffer)
            .where(ProductOffer.product_id == product.id)
            .join(Webshop).order_by(Webshop.name)
    ).all()

    return render_template(
        "product.html.jinja",
        p=product,
        offers=offers)

@app.route("/productoffer/<offer_id>/price_step_graph_data.json")
def offer_price_json(offer_id):
    """Generate the price step graph data of a specific offer"""
    offer: ProductOffer = db.session.execute(
        db.select(ProductOffer)
            .where(ProductOffer.id == offer_id)
    ).scalar_one()

    if offer is None:
        abort(404)

    data: str = generate_price_graph_data(offer)
    return Response(data, mimetype="application/json")

@app.route("/all_offers")
def all_offers():
    """Generate an overview of all available offers"""

    show_variance: bool = False
    if request.args.get("variance") != None:
        show_variance = True

    offers: List[ProductOffer] = db.session.scalars(
        db.select(ProductOffer)
            .join(Product)
            .order_by(Product.name)
    ).all()

    current_prices: Dict[ProductOffer, Price] = {}
    for offer in offers:
        current_prices[offer] = offer.get_current_price()

    return render_template(
        "all_offers.html.jinja",
        offers=offers,
        current_prices=current_prices,
        show_variance=show_variance
        )

@app.route("/shop/<shop_id>")
def webshop_page(shop_id):
    """Show a page with all the product offers of a specific webshop"""
    shop: Webshop = db.session.scalar(
        db.select(Webshop)
            .where(Webshop.id == shop_id)
    )

    if shop is None:
        abort(404)

    show_variance: bool = False
    if request.args.get("variance") != None:
        show_variance = True

    offers: List[ProductOffer] = db.session.scalars(
        db.select(ProductOffer)
            .where(ProductOffer.shop_id == shop_id)
            .join(Product)
            .order_by(Product.name)
    ).all()

    current_prices: Dict[ProductOffer, Price] = {}
    for offer in offers:
        current_prices[offer] = offer.get_current_price()

    return render_template(
        "shop.html.jinja",
        s=shop,
        offers=offers,
        current_prices=current_prices,
        show_variance=show_variance
        )

@app.route("/add_url", methods=['GET'])
def add_url():
    """GET request to allow users to add a URL using a booklet"""
    try:
        url = request.args.to_dict()['url']
    except KeyError:
        abort(404)
    return add_product_url(url)

@app.errorhandler(404)
def not_found(error):
    """Return the 404 page"""
    return render_template("404.html.jinja", e=error)
