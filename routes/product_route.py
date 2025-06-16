from app import app
import models.salary
from models import db
import models.qr_code
import models.product
from flask_login import login_required
from routes.main_route import EXCHANGE_DATA
from flask import render_template, redirect, url_for, flash, request

@app.route("/product/list", methods=["GET"])
@login_required
def product_list_page():
    query_select = request.args.get("select_type", None)
    query_search = request.args.get("search", None)
    query_search_gramm = request.args.get("search-gramm", None)

    if query_search:
        type = query_search[:1].upper()
        number = query_search[1:]
        if number and number.isdigit():
            product_list = models.product.Product.query.filter_by(type=type, number=number).order_by(models.product.Product.created_at.desc()).all()
        else:
            product_list = models.product.Product.query.filter_by(type=type).order_by(models.product.Product.created_at.desc()).all()

    elif query_select:
        if query_select == "ALL":
            product_list = models.product.Product.query.order_by(models.product.Product.created_at.desc()).all()
        elif query_select == "NEW":
            product_list = models.product.Product.query.filter_by(status="NEW").order_by(models.product.Product.created_at.desc()).all()
        elif query_select == "INVOICE":
            product_list = models.product.Product.query.filter_by(status="INVOICE").order_by(models.product.Product.created_at.desc()).all()
        elif query_select == "SOLD":
            product_list = models.product.Product.query.filter_by(status="SOLD").order_by(models.product.Product.created_at.desc()).all()
            
    elif query_search_gramm:
        product_list = models.product.Product.query.filter_by(gramm=query_search_gramm).order_by(models.product.Product.created_at.desc()).all()

    else: 
        product_list = models.product.Product.query.order_by(models.product.Product.created_at.desc()).all()
    
    product_total_gramm = sum(product.gramm for product in product_list)
    product_total_price = sum(product.price for product in product_list)
    product_total_price = round(product_total_price, 2)
    product_total_gramm = round(product_total_gramm, 2)
    salary_list = models.salary.Salary.query.all()
    return render_template("product/product_list.html", product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, query_select=query_select, query_search=query_search, salary_list=salary_list)

@app.route("/product/get/<product_id>", methods=["GET"])
@login_required
def product_get_page(product_id):
    product_get = models.product.Product.query.filter_by(id=product_id).first()
    if product_get:
        return render_template("product/product_get.html", product=product_get)
    else:
        flash("Product not found", "danger")
        return redirect(url_for("product_list_page"))

@app.route("/product/create", methods=["GET", "POST"])
@login_required
def product_create_page():
    id = request.args.get("id")

    qr_code = models.qr_code.QRCode.query.filter_by(id=id).first()

    title = qr_code.title
    gramm = qr_code.gramm
    proba = qr_code.proba
    type = qr_code.type
    number = qr_code.number
    size = qr_code.size

    dollor = float(EXCHANGE_DATA["UZS"])
    gold = float(EXCHANGE_DATA["GOLD"])
        
    working_salary = models.salary.Salary.query.filter_by(type=type).first()
    if working_salary is None:
        flash("Salary type not found", "danger")
        return redirect(url_for("product_create_page"))
        
    gold_price = gold * dollor
    price = (((gramm * working_salary.amount) + (gramm * gold_price)) / dollor) / gold
    price = round(price, 2)

    new_product = models.product.Product(title=title, gramm=gramm, proba=proba, type=type, number=number, status="NEW", price=price, qr_code=qr_code.id, size=size)
    db.session.add(new_product)
    db.session.commit()

    flash("Product created successfully", "success")
    return redirect(url_for("product_list_page"))

@app.route("/product/delete/<product_id>", methods=["GET", "POST"])
@login_required
def product_delete_page(product_id):
    if request.method == "POST":
        deleted_product = models.product.Product.query.filter_by(id=product_id).first()

        if deleted_product.status != "INVOICE":
            db.session.delete(deleted_product)
            db.session.commit()

            flash("Product successfully deleted", "warning")
            return redirect(url_for("product_list_page"))
        else:
            flash("Product has invoiced", "danger")
            return redirect(url_for("product_list_page"))
    else:
        return render_template("product/product_delete.html", product_id=product_id)

@app.route("/product/delete/all", methods=["GET", "POST"])
@login_required
def product_delete_all_page():
    if request.method == "POST":
        deleted_product_list = models.product.Product.query.filter_by(status="NEW").all()

        for deleted_product in deleted_product_list: 
            db.session.delete(deleted_product)
    
        db.session.commit()
        flash("Product successfully deleted", "warning")
        return redirect(url_for("product_list_page"))
    else:
        return render_template("product/product_delete_all.html")
