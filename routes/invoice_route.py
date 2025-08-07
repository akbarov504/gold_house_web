from app import app
from models import db
from datetime import datetime
from flask_login import login_required
from forms.invoice_form import CreateInvoiceForm, UpdateInvoiceForm
from flask import render_template, redirect, url_for, flash, request, session

import models.salary
import models.user
import models.invoice
import models.product
import models.invoice_product

@app.route("/invoice/list", methods=["GET"])
@login_required
def invoice_list_page():
    session.update({"product_list": []})
    invoice_list = models.invoice.Invoice.query.order_by(models.invoice.Invoice.created_at.desc()).all()
    salary_list = models.salary.Salary.query.all()
    product_list = models.product.Product.query.filter_by(status="INVOICE").all()
    user_list = models.user.User.query.filter_by(role="DEALER").all()
    product_total_gramm = sum(product.gramm for product in product_list)
    product_total_price = sum(product.price for product in product_list)
    product_total_price = round(product_total_price, 2)
    product_total_gramm = round(product_total_gramm, 2)
    return render_template("invoice/invoice_list.html", invoice_list=invoice_list, user_list=user_list, salary_list=salary_list, product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price)

@app.route("/invoice/get/<invoice_id>", methods=["GET"])
@login_required
def invoice_get_page(invoice_id):
    id = request.args.get("id")
    if id is not None:
        invoice = models.invoice.Invoice.query.filter_by(id=invoice_id).first()
        invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(invoice_id=invoice.id).all()
        product = models.product.Product.query.filter_by(status="INVOICE", qr_code=id).first()

        invoice_product_list_l = [invoice_product.product_id for invoice_product in invoice_product_list]
        if product is None or product.id not in invoice_product_list_l:
            flash("Product not found", "danger")
            return redirect(url_for("invoice_get_page", invoice_id=invoice_id))
        
        product.status = "BACK"
        db.session.commit()
        
        total_amount = 0
        for invoice_product in invoice_product_list:
            product = models.product.Product.query.filter_by(id=invoice_product.product_id).first()
            total_amount += product.price
        invoice.total_price = total_amount
        db.session.commit()

    invoice_get = models.invoice.Invoice.query.filter_by(id=invoice_id).first()
    if invoice_get:
        user_get = models.user.User.query.filter_by(id=invoice_get.user_id, role="DEALER").first()
        invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(invoice_id=invoice_get.id).all()
        invoice_product_product_id_list = [invoice_product.product_id for invoice_product in invoice_product_list]
        d_s_product_list = models.product.Product.query.filter(models.product.Product.id.in_(invoice_product_product_id_list)).all()
        d_s_product_list_page = models.product.Product.query.filter(models.product.Product.id.in_(invoice_product_product_id_list))

        product_total_gramm = 0
        product_total_price = 0
        for d_s_product in d_s_product_list:
            product_total_gramm += d_s_product.gramm
            product_total_price += d_s_product.price
        salary_list = models.salary.Salary.query.all()

        offset = request.args.get("offset")
        if offset is None:
            offset = 1
        else:
            offset = int(offset)

        d_s_product_list_page_list = db.paginate(d_s_product_list_page, page=offset, per_page=25, error_out=False)
    
        next_url = url_for('invoice_get_page', invoice_id=invoice_get.id, offset=d_s_product_list_page_list.next_num) \
            if d_s_product_list_page_list.has_next else None
        prev_url = url_for('invoice_get_page', invoice_id=invoice_get.id, offset=d_s_product_list_page_list.prev_num) \
            if d_s_product_list_page_list.has_prev else None
        
        return render_template("/invoice/invoice_get.html", salary_list=salary_list, d_s_product_list=d_s_product_list, product_count=len(d_s_product_list), invoice=invoice_get, user=user_get, invoice_product_list=invoice_product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, d_s_product_list_page_list=d_s_product_list_page_list.items, next_url=next_url, prev_url=prev_url)
    else:
        flash("Invoice not found", "danger")
        return redirect(url_for("invoice_list_page"))

@app.route("/invoice/reset-back-product/<invoice_id>", methods=["GET"])
@login_required
def invoice_reset_back_product(invoice_id):
    invoice = models.invoice.Invoice.query.filter_by(status="NEW", id=invoice_id).first()
    if invoice:
        invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(invoice_id=invoice.id).all()
        for invoice_product in invoice_product_list:
            product = models.product.Product.query.filter_by(status="BACK", id=invoice_product.product_id).first()
            if product:
                product.status = "INVOICE"
        db.session.commit()
        flash("Product status change INVOICE!", "warning")
        return redirect(url_for("invoice_get_page", invoice_id=invoice_id))
    else:
        flash("Invoice not found", "danger")
        return redirect(url_for("invoice_list_page"))

@app.route("/invoice/complate/<invoice_id>", methods=["GET"])
@login_required
def invoice_complate_page(invoice_id):
    invoice = models.invoice.Invoice.query.filter_by(id=invoice_id).first()
    if invoice:
        invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(invoice_id=invoice.id).all()
        for invoice_product in invoice_product_list:
            product_sold = models.product.Product.query.filter_by(id=invoice_product.product_id, status="INVOICE").first()
            if product_sold is not None:
                product_sold.status = "SOLD"

            product_back = models.product.Product.query.filter_by(id=invoice_product.product_id, status="BACK").first()
            if product_back is not None:
                product_back.status = "NEW"
                db.session.delete(invoice_product)

        invoice.status = "COMPLETED"
        db.session.commit()
        return redirect(url_for("invoice_get_page", invoice_id=invoice.id))
    else:
        flash("Invoice not found", "danger")
        return redirect(url_for("invoice_list_page"))

@app.route("/invoice/create/<product_list>", methods=["GET", "POST"])
@login_required
def invoice_create_page(product_list):
    form = CreateInvoiceForm()
    user_list = models.user.User.query.filter_by(role="DEALER").all()
    form.dealer.choices = [(user.id, user.full_name) for user in user_list]

    if form.validate_on_submit():
        session.update({"product_list": []})
        product_list = product_list.split(",")
        dealer = form.dealer.data

        found_dealer =  models.user.User.query.filter_by(id=dealer, role="DEALER").first()
        if found_dealer is None:
            flash("Dealer not found!", "danger")
            return redirect(url_for("invoice_create_page", product_list=product_list))
        
        total_amount = 0
        invoice_number = "INV_" + datetime.now().strftime("%Y%m%d_%H%M%S") + "_0" + str(found_dealer.id)
        new_invoice = models.invoice.Invoice(invoice_number=invoice_number, user_id=found_dealer.id, status="NEW", total_price=total_amount)
        db.session.add(new_invoice)
        db.session.commit()

        for pro in product_list:
            found_product = models.product.Product.query.filter_by(qr_code=pro, status="NEW").first()
            if found_product is None:
                flash("Product not found!", "danger")
                return redirect(url_for("invoice_product_create_page"))
            else:
                found_product.status = "INVOICE"
                total_amount += found_product.price

            new_invovice_product = models.invoice_product.InvoiceProduct(new_invoice.id, found_product.id)
            db.session.add(new_invovice_product)
            
        new_invoice.total_price = total_amount
        db.session.commit()
        
        flash("Invoice created successfully", "success")
        return redirect(url_for("invoice_list_page"))
    else:
        return render_template("invoice/invoice_create.html", form=form, product_list=product_list)

@app.route("/invoice/product/create", methods=["GET", "POST"])
@login_required
def invoice_product_create_page():
    id = request.args.get("id")
    if id is not None:
        product_list_with_id = session.get("product_list", [])
        product = models.product.Product.query.filter_by(status="NEW", qr_code=id).first()
        if product is not None:
            if id not in product_list_with_id:
                product_list_with_id.insert(0, id)
            else:
                flash("This product already exists!", "danger")
        else:
            flash("Product not found!", "danger")
    else:
        product_list_with_id = session.get("product_list", [])

    product_list = models.product.Product.query.filter(models.product.Product.qr_code.in_(product_list_with_id)).all()
    product_list_page = models.product.Product.query.filter(models.product.Product.qr_code.in_(product_list_with_id))

    if len(product_list) != 0:
        for i in range(len(product_list)):
            if None in product_list:
                product_list.remove(None)

    product_list_with_id = ",".join(product_list_with_id)
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
    
    next_url = url_for('invoice_product_create_page', offset=product_list_page_list.next_num) \
        if product_list_page_list.has_next else None
    prev_url = url_for('invoice_product_create_page', offset=product_list_page_list.prev_num) \
        if product_list_page_list.has_prev else None

    product_list_page_list.items.reverse()
    return render_template("invoice/invoice_product_create.html", product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, salary_list=salary_list, product_total_count=product_total_count, product_list_with_id=product_list_with_id, product_list_page_list=product_list_page_list.items, next_url=next_url, prev_url=prev_url)

@app.route("/invoice/delete/<invoice_id>", methods=["GET", "POST"])
@login_required
def invoice_delete_page(invoice_id):
    if request.method == "POST":
        deleted_invoice = models.invoice.Invoice.query.filter_by(id=invoice_id).first()

        if deleted_invoice.status != "NEW":
            invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(invoice_id=deleted_invoice.id).all()

            for invoice_product in invoice_product_list:
                product = models.product.Product.query.filter_by(id=invoice_product.product_id, status="INVOICE").first()

                if product is not None:
                    product.status = "NEW"
                    db.session.delete(invoice_product)
                    db.session.commit()
                else:
                    db.session.delete(invoice_product)
                    db.session.commit()

            db.session.delete(deleted_invoice)
            db.session.commit()

            flash("Invoice successfully deleted", "warning")
            return redirect(url_for("invoice_list_page"))
        else:
            flash("Invoice has not complated", "danger")
            return redirect(url_for("invoice_list_page"))
    else:
        return render_template("invoice/invoice_delete.html", invoice_id=invoice_id)

@app.route("/invoice/update/<invoice_id>", methods=["GET", "POST"])
@login_required
def invoice_update_page(invoice_id):
    form = UpdateInvoiceForm()
    user_list = models.user.User.query.filter_by(role="DEALER").all()
    form.dealer.choices = [(user.id, user.full_name) for user in user_list]

    if form.validate_on_submit():
        dealer = form.dealer.data
        updated_invoice = models.invoice.Invoice.query.filter_by(id=invoice_id).first()
        updated_invoice.user_id = dealer
        db.session.commit()

        flash("Invoice dealer updated successfully", "success")
        return redirect(url_for("invoice_list_page"))
    else:
        return render_template("invoice/invoice_update.html", form=form)

@app.route("/invoice/print/<invoice_id>", methods=["GET"])
@login_required
def invoice_print_page(invoice_id):
    invoice_print = models.invoice.Invoice.query.filter_by(id=invoice_id).first()
    if invoice_print:
        user_print = models.user.User.query.filter_by(id=invoice_print.user_id, role="DEALER").first()
        invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(invoice_id=invoice_print.id).all()
        product_list = models.product.Product.query.all()
        salary_list = models.salary.Salary.query.all()
        product_total_gramm = 0
        product_total_price = 0
        for invoice_product in invoice_product_list:
            product = models.product.Product.query.filter_by(id=invoice_product.product_id).first()
            if product:
                product_total_gramm += product.gramm
                product_total_price += product.price
            else:
                continue
        return render_template("invoice/invoice_print.html", invoice=invoice_print, user=user_print, invoice_product_list=invoice_product_list, product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, salary_list=salary_list)
    else:
        flash("Invoice not found", "danger")
        return redirect(url_for("invoice_list_page"))
