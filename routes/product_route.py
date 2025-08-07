from app import app
import models.invoice_product
import models.salary
from models import db
import models.qr_code
import models.product
from datetime import datetime
from flask_login import login_required
from routes.main_route import EXCHANGE_DATA
from flask import render_template, redirect, url_for, flash, request, session, jsonify

@app.route("/api/product/get/<id>", methods=["GET"])
def product_get_api(id):
    product = models.product.Product.query.filter_by(qr_code=id).first()
    if product:
        return jsonify({"result": {
            "id": product.id,
            "title": product.title,
            "gramm": product.gramm,
            "proba": product.proba,
            "type": product.type,
            "number": product.number,
            "price": product.price,
            "size": product.size
        }}), 200
    else:
        return jsonify({"result": "Product not found"}), 404

@app.route("/product/list", methods=["GET"])
@login_required
def product_list_page():
    session.update({"check_product_list": []})
    query_select = request.args.get("select_type", None)
    query_search = request.args.get("search", None)
    query_search_gramm = request.args.get("search-gramm", None)
    query_search_date = request.args.get("search-date", None)

    if query_search:
        _type = query_search[:1].upper()
        number = query_search[1:]
        if number and number.isdigit():
            product_list = models.product.Product.query.filter_by(type=_type, number=number).order_by(models.product.Product.created_at.desc()).all()
            product_list_page = models.product.Product.query.filter_by(type=_type, number=number).order_by(models.product.Product.created_at.desc())
        else:
            product_list = models.product.Product.query.filter_by(type=_type).order_by(models.product.Product.created_at.desc()).all()
            product_list_page = models.product.Product.query.filter_by(type=_type).order_by(models.product.Product.created_at.desc())

    elif query_select:
        if query_select == "ALL":
            product_list = models.product.Product.query.order_by(models.product.Product.created_at.desc()).all()
            product_list_page = models.product.Product.query.order_by(models.product.Product.created_at.desc())
        elif query_select == "NEW":
            product_list = models.product.Product.query.filter_by(status="NEW").order_by(models.product.Product.created_at.desc()).all()
            product_list_page = models.product.Product.query.filter_by(status="NEW").order_by(models.product.Product.created_at.desc())
        elif query_select == "INVOICE":
            product_list = models.product.Product.query.filter_by(status="INVOICE").order_by(models.product.Product.created_at.desc()).all()
            product_list_page = models.product.Product.query.filter_by(status="INVOICE").order_by(models.product.Product.created_at.desc())
        elif query_select == "SOLD":
            product_list = models.product.Product.query.filter_by(status="SOLD").order_by(models.product.Product.created_at.desc()).all()
            product_list_page = models.product.Product.query.filter_by(status="SOLD").order_by(models.product.Product.created_at.desc())
        elif query_select == "BACK":
            product_list = models.product.Product.query.filter_by(status="BACK").order_by(models.product.Product.created_at.desc()).all()
            product_list_page = models.product.Product.query.filter_by(status="BACK").order_by(models.product.Product.created_at.desc())
            
    elif query_search_gramm:
        product_list = models.product.Product.query.filter_by(gramm=query_search_gramm).order_by(models.product.Product.created_at.desc()).all()
        product_list_page = models.product.Product.query.filter_by(gramm=query_search_gramm).order_by(models.product.Product.created_at.desc())

    elif query_search_date:
        old_date = datetime.strptime(query_search_date, "%Y-%m-%dT%H:%M")
        now_date = datetime.now()
        product_list = models.product.Product.query.filter(models.product.Product.created_at.between(old_date, now_date)).all()
        product_list_page = models.product.Product.query.filter(models.product.Product.created_at.between(old_date, now_date))

    else: 
        product_list = models.product.Product.query.order_by(models.product.Product.created_at.desc()).all()
        product_list_page = models.product.Product.query.order_by(models.product.Product.created_at.desc())
    
    product_total_count = len(product_list)
    product_total_gramm = sum(product.gramm for product in product_list)
    product_total_price = sum(product.price for product in product_list)
    product_total_price = round(product_total_price, 2)
    product_total_gramm = round(product_total_gramm, 2)
    salary_list = models.salary.Salary.query.all()

    offset = request.args.get("offset")
    if offset is None:
        offset = 1
    else:
        offset = int(offset)

    product_list_page_list = db.paginate(product_list_page, page=offset, per_page=25, error_out=False)
    
    next_url = url_for('product_list_page', offset=product_list_page_list.next_num) \
        if product_list_page_list.has_next else None
    prev_url = url_for('product_list_page', offset=product_list_page_list.prev_num) \
        if product_list_page_list.has_prev else None

    return render_template("product/product_list.html", product_list_page_list=product_list_page_list.items, product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, salary_list=salary_list, product_total_count=product_total_count, next_url=next_url, prev_url=prev_url)

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

        if deleted_product.status != "INVOICE" and deleted_product.status != "BACK":
            db.session.delete(deleted_product)
            db.session.commit()

            flash("Product successfully deleted", "warning")
            return redirect(url_for("product_list_page"))
        else:
            flash("Product has invoiced", "danger")
            return redirect(url_for("product_list_page"))
    else:
        return render_template("product/product_delete.html", product_id=product_id)

@app.route("/product/delete/new", methods=["GET", "POST"])
@login_required
def product_delete_new_page():
    if request.method == "POST":
        deleted_product_list = models.product.Product.query.filter_by(status="NEW").all()

        for deleted_product in deleted_product_list: 
            db.session.delete(deleted_product)
    
        db.session.commit()
        flash("Product successfully deleted", "warning")
        return redirect(url_for("product_list_page"))
    else:
        return render_template("product/product_delete_new.html")

@app.route("/product/delete/sold", methods=["GET", "POST"])
@login_required
def product_delete_sold_page():
    if request.method == "POST":
        deleted_product_list = models.product.Product.query.filter_by(status="SOLD").all()

        for deleted_product in deleted_product_list: 
            deleted_invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(product_id=deleted_product.id).all()
            for del_invoice_pro in deleted_invoice_product_list:
                db.session.delete(del_invoice_pro)
            db.session.delete(deleted_product)
    
        db.session.commit()
        flash("Product successfully deleted", "warning")
        return redirect(url_for("product_list_page"))
    else:
        return render_template("product/product_delete_sold.html")

@app.route("/product/delete/scan", methods=["GET"])
@login_required
def product_delete_scan_page():
    product_list = models.product.Product.query.order_by(models.product.Product.created_at.desc())
    offset = request.args.get("offset")
    if offset is None:
        offset = 1
    else:
        offset = int(offset)

    product_list_page_list = db.paginate(product_list, page=offset, per_page=10, error_out=False)
    
    next_url = url_for('product_delete_scan_page', offset=product_list_page_list.next_num) \
        if product_list_page_list.has_next else None
    prev_url = url_for('product_delete_scan_page', offset=product_list_page_list.prev_num) \
        if product_list_page_list.has_prev else None
    return render_template("product/product_delete_scan.html", product_list_page_list=product_list_page_list.items, next_url=next_url, prev_url=prev_url)

@app.route("/product/delete/scan/del", methods=["GET"])
@login_required
def product_delete_scan_del_page():
    id = request.args.get("id")
    
    product = models.product.Product.query.filter_by(qr_code=id).first()
    if product is None:
        flash("Product not found!", "danger")
        return redirect(url_for("product_delete_scan_page"))
    
    db.session.delete(product)
    db.session.commit()
    flash("Product Successfully deleted", "warning")
    return redirect(url_for("product_delete_scan_page"))

@app.route("/product/check", methods=["GET"])
@login_required
def product_check_page():
    id = request.args.get("id")
    if id is not None:
        check_product_list_p = session.get("check_product_list", [])
        product = models.product.Product.query.filter_by(qr_code=id).first()
        if product is not None:
            if id not in check_product_list_p:
                check_product_list_p.insert(0, id)
            else:
                flash("This product already exists!", "danger")
        else:
            flash("Product not found!", "danger")
    else:
        check_product_list_p = session.get("check_product_list", [])
    
    product_list = models.product.Product.query.filter(models.product.Product.qr_code.in_(check_product_list_p)).all()
    product_list_page = models.product.Product.query.filter(models.product.Product.qr_code.in_(check_product_list_p))

    if len(product_list) != 0:
        for i in range(len(product_list)):
            if None in product_list:
                product_list.remove(None)
    
    check_product_list_p = ",".join(check_product_list_p)
    product_total_count = len(product_list)
    product_total_gramm = sum(product.gramm for product in product_list)
    product_total_price = sum(product.price for product in product_list)
    product_total_price = round(product_total_price, 2)
    product_total_gramm = round(product_total_gramm, 2)
    salary_list = models.salary.Salary.query.all()

    offset = request.args.get("offset")
    if offset is None:
        offset = 1
    else:
        offset = int(offset)
    
    product_list_page_list = db.paginate(product_list_page, page=offset, per_page=25, error_out=False)
    
    next_url = url_for('product_check_page', offset=product_list_page_list.next_num) \
        if product_list_page_list.has_next else None
    prev_url = url_for('product_check_page', offset=product_list_page_list.prev_num) \
        if product_list_page_list.has_prev else None
    return render_template("product/product_check.html", product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, salary_list=salary_list, product_total_count=product_total_count, product_list_page_list=product_list_page_list.items, next_url=next_url, prev_url=prev_url)
