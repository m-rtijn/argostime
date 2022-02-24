#!/usr/bin/env python3
"""
    routes.py

    Flask routes

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

from datetime import datetime
import io
import logging
from typing import List
import urllib.parse

from flask import current_app as app
from flask import render_template, abort, request, redirect
from flask import Response

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from argostime.exceptions import CrawlerException
from argostime.exceptions import PageNotFoundException
from argostime.exceptions import WebsiteNotImplementedException
from argostime.graphs import generate_price_bar_graph
from argostime.graphs import generate_price_step_graph
from argostime.models import Webshop, Product, ProductOffer, Price
from argostime.products import ProductOfferAddResult, add_product_offer_from_url

@app.route("/", methods=["GET", "POST"])
def index():
    """Render home page"""
    if request.method == "POST":
        url = request.form["url"]
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
    else:
        products = Product.query.order_by(Product.id.desc()).limit(5).all()
        discounts = Price.query.filter(
            Price.datetime >= datetime.now().date(),
            Price.on_sale == True # pylint: disable=C0121
            ).all()

        discounts.sort(key=lambda x: x.product_offer.product.name)
        shops = Webshop.query.order_by(Webshop.name).all()

        return render_template(
            "index.html.jinja",
            products=products,
            discounts=discounts,
            shops=shops)

@app.route("/product/<product_code>")
def product_page(product_code):
    """Show the page for a specific product, with all known product offers"""
    product: Product = Product.query.filter_by(product_code=product_code).first()

    if product is None:
        abort(404)

    offers: List[ProductOffer] = ProductOffer.query.filter_by(
        product_id=product.id).join(Webshop).order_by(Webshop.name).all()

    return render_template(
        "product.html.jinja",
        p=product,
        offers=offers)

@app.route("/productoffer/<offer_id>/price_bar_graph.png")
def offer_price_bar_graph(offer_id):
    """Generate the price graph of a specific offer"""
    offer: ProductOffer = ProductOffer.query.get(offer_id)

    if offer is None:
        abort(404)

    fig: Figure = generate_price_bar_graph(offer)
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype="image/png")

@app.route("/productoffer/<offer_id>/price_step_graph.png")
def offer_price_step_graph(offer_id):
    """Generate the price step graph of a specific offer"""
    offer: ProductOffer = ProductOffer.query.get(offer_id)

    if offer is None:
        abort(404)

    fig: Figure = generate_price_step_graph(offer)
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype="image/png")

@app.route("/all_offers")
def all_offers():
    """Generate an overview of all available offers"""

    show_variance: bool = False
    if request.args.get("variance") != None:
        show_variance = True

    offers: List[ProductOffer] = ProductOffer.query.all()

    return render_template("all_offers.html.jinja", offers=offers, show_variance=show_variance)

@app.route("/shop/<shop_id>")
def webshop_page(shop_id):
    """Show a page with all the product offers of a specific webshop"""
    shop: Webshop = Webshop.query.get(shop_id)

    if shop is None:
        abort(404)

    show_variance: bool = False
    if request.args.get("variance") != None:
        show_variance = True

    offers: List[ProductOffer] = ProductOffer.query.filter_by(
        shop_id=shop_id).join(Product).order_by(Product.name).all()

    return render_template(
        "shop.html.jinja",
        s=shop,
        offers=offers,
        show_variance=show_variance
        )

@app.errorhandler(404)
def not_found(error):
    """Return the 404 page"""
    return render_template("404.html.jinja", e=error)
