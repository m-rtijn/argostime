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

import io
from typing import List
import urllib.parse

from flask import current_app as app
from flask import render_template, abort, request, redirect
from flask import Response

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from argostime.exceptions import PageNotFoundException, WebsiteNotImplementedException
from argostime.graphs import generate_price_bar_graph
from argostime.graphs import generate_price_step_graph
from argostime.models import Webshop, Product, ProductOffer
from argostime.products import ProductOfferAddResult, add_product_offer_from_url

@app.route("/", methods=["GET", "POST"])
def index():
    """Render home page"""
    if request.method == "POST":
        form = request.form
        try:
            res, offer = add_product_offer_from_url(form["url"])
        except WebsiteNotImplementedException:
            hostname: str = urllib.parse.urlparse(form["url"]).netloc
            if len(hostname) == 0:
                hostname = form["url"]
            return render_template("add_product_result.html.jinja",
                result=f"Helaas wordt de website {hostname} nog niet ondersteund."), 400
        except PageNotFoundException:
            return render_template("add_product_result.html.jinja",
                result="De pagina {url} kon niet worden gevonden.".format(url=form["url"])), 404

        if res == ProductOfferAddResult.ADDED or res == ProductOfferAddResult.ALREADY_EXISTS and offer is not None:
            return redirect(f"/product/{offer.get_product().product_code}")

        return render_template("add_product.html.jinja", result=str(res))
    else:
        products = Product.query.order_by(Product.id.desc()).all()
        shops = Webshop.query.order_by(Webshop.name).all()

        return render_template(
            "index.html.jinja",
            products=products[:10],
            shops=shops
            )

@app.route("/product/<product_code>")
def product_page(product_code):
    """Show the page for a specific product, with all known product offers"""
    product: Product = Product.query.filter_by(product_code=product_code).first()

    if product is None:
        abort(404)

    offers: List[ProductOffer] = ProductOffer.query.filter_by(product_id=product.id).all()

    return render_template(
        "product.html.jinja",
        p=product,
        offers=offers)

@app.route("/productoffer/<offer_id>/price_bar_graph.png")
def offer_price_bar_graph(offer_id):
    """Generate the price graph of a specific offer"""
    offer: ProductOffer = ProductOffer.query.filter_by(id=offer_id).first()

    if offer is None:
        abort(404)

    fig: Figure = generate_price_bar_graph(offer)
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype="image/png")

@app.route("/productoffer/<offer_id>/price_step_graph.png")
def offer_price_step_graph(offer_id):
    """Generate the price step graph of a specific offer"""
    offer: ProductOffer = ProductOffer.query.filter_by(id=offer_id).first()

    if offer is None:
        abort(404)

    fig: Figure = generate_price_step_graph(offer)
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype="image/png")

@app.route("/shop/<shop_id>")
def webshop_page(shop_id):
    """Show a page with all the product offers of a specific webshop"""
    shop: Webshop = Webshop.query.filter_by(id=shop_id).first()

    if shop is None:
        abort(404)

    offers: List[ProductOffer] = ProductOffer.query.filter_by(shop_id=shop_id).all()
    offers.sort(key=lambda offer: offer.product.name)

    return render_template(
        "shop.html.jinja",
        s=shop,
        offers=offers
        )

@app.errorhandler(404)
def not_found(error):
    """Return the 404 page"""
    return render_template("404.html.jinja", e=error)
