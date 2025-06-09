import qrcode
import models.salary
from app import app
from os import remove
import models.product
from models import db
from os.path import join
from datetime import datetime
from flask_login import login_required
from routes.main_route import EXCHANGE_DATA
from forms.product_form import CreateProductForm, UpdateProductForm
from flask import render_template, redirect, url_for, flash, request

@app.route("/product/list", methods=["GET"])
@login_required
def product_list_page():
    query_select = request.args.get("select_type", None)
    query_search = request.args.get("search", None)

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

    else: 
        product_list = models.product.Product.query.order_by(models.product.Product.created_at.desc()).all()
    
    product_total_gramm = sum(product.gramm for product in product_list)
    product_total_price = sum(product.price for product in product_list)
    product_total_price = round(product_total_price, 2)
    return render_template("product/product_list.html", product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, query_select=query_select, query_search=query_search)

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
    form = CreateProductForm()
    if form.validate_on_submit():
        title = form.title.data
        gramm = form.gramm.data
        proba = form.proba.data
        type = form.type.data
        number = form.number.data
        size = form.size.data
        dollor = int(EXCHANGE_DATA["UZS"])
        gold = int(EXCHANGE_DATA["GOLD"])
        
        working_salary = models.salary.Salary.query.filter_by(type=type).first()
        if working_salary is None:
            flash("Salary type not found", "danger")
            return redirect(url_for("product_create_page"))
        
        gold_price = gold * dollor
        price = (((gramm * working_salary.amount) + (gramm * gold_price)) / dollor) / gold
        price = round(price, 2)

        qr_data = f"Title: {title}\nGramm: {gramm}\nProba: {proba}\nType: {type}\nNumber: {number}\nSize: {size}\nStatus: NEW\nPrice: {price}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = join(app.config['UPLOAD_FOLDER'], filename)
        img.save(file_path)

        new_product = models.product.Product(title=title, gramm=gramm, proba=proba, type=type, number=number, status="NEW", price=price, qr_code=filename, size=size)
        db.session.add(new_product)
        db.session.commit()

        flash("Product created successfully", "success")
        return redirect(url_for("product_list_page"))
    else:
        return render_template("product/product_create.html", form=form)

@app.route("/product/delete/<product_id>", methods=["GET", "POST"])
@login_required
def product_delete_page(product_id):
    if request.method == "POST":
        deleted_product = models.product.Product.query.filter_by(id=product_id).first()

        if deleted_product.status != "INVOICE":
            db.session.delete(deleted_product)
            db.session.commit()

            remove(join(app.config['UPLOAD_FOLDER'], deleted_product.qr_code))
            flash("Product successfully deleted", "warning")
            return redirect(url_for("product_list_page"))
        else:
            flash("Product has invoiced", "danger")
            return redirect(url_for("product_list_page"))
    else:
        return render_template("product/product_delete.html", product_id=product_id)

@app.route("/product/update/<product_id>", methods=["GET", "POST"])
@login_required
def product_update_page(product_id):
    form = UpdateProductForm()
    if form.validate_on_submit():
        title = form.title.data
        gramm = form.gramm.data
        proba = form.proba.data
        type = form.type.data
        number = form.number.data
        size = form.size.data
        dollor = int(EXCHANGE_DATA["UZS"])
        gold = int(EXCHANGE_DATA["GOLD"])
        
        working_salary = models.salary.Salary.query.filter_by(type=type).first()
        if working_salary is None:
            flash("Salary type not found", "danger")
            return redirect(url_for("product_create_page"))
        
        gold_price = gold * dollor
        price = (((gramm * working_salary.amount) + (gramm * gold_price)) / dollor) / gold
        price = round(price, 2)

        updated_product = models.product.Product.query.filter_by(id=product_id).first()
        updated_product.title = title
        updated_product.gramm = gramm
        updated_product.proba = proba
        updated_product.type = type
        updated_product.number = number
        updated_product.price = price
        updated_product.size = size

        qr_data = f"Title: {title}\nGramm: {gramm}\nProba: {proba}\nType: {type}\nNumber: {number}\nSize: {size}\nStatus: {updated_product.status}\nPrice: {price}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = join(app.config['UPLOAD_FOLDER'], filename)
        img.save(file_path)

        remove(join(app.config['UPLOAD_FOLDER'], updated_product.qr_code))
        updated_product.qr_code = filename
        db.session.commit()

        flash("Product updated successfully", "success")
        return redirect(url_for("product_list_page"))
    else:
        product = models.product.Product.query.filter_by(id=product_id).first()
        form.title.data = product.title
        form.gramm.data = product.gramm
        form.proba.data = product.proba
        form.type.data = product.type
        form.number.data = product.number
        form.size.data = product.size
        return render_template("product/product_update.html", form=form)

@app.route("/product/print/<product_id>", methods=["GET"])
@login_required
def product_print_page(product_id):
    product_print = models.product.Product.query.filter_by(id=product_id).first()
    if product_print:
        return render_template("product/product_print.html", product=product_print)
    else:
        flash("Product not found", "danger")
        return redirect(url_for("product_list_page"))
