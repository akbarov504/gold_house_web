from app import app
from models import db
from datetime import datetime
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from forms.invoice_form import CreateInvoiceForm, UpdateInvoiceForm, CreateInvoiceProductForm

import models.user
import models.invoice
import models.product
import models.invoice_product

@app.route("/invoice/list", methods=["GET"])
@login_required
def invoice_list_page():
    invoice_list = models.invoice.Invoice.query.order_by(models.invoice.Invoice.created_at.desc()).all()
    user_list = models.user.User.query.filter_by(role="DEALER").all()
    return render_template("invoice/invoice_list.html", invoice_list=invoice_list, user_list=user_list)

@app.route("/invoice/get/<invoice_id>", methods=["GET"])
@login_required
def invoice_get_page(invoice_id):
    invoice_get = models.invoice.Invoice.query.filter_by(id=invoice_id).first()
    if invoice_get:
        user_get = models.user.User.query.filter_by(id=invoice_get.user_id, role="DEALER").first()
        invoice_product_list = models.invoice_product.InvoiceProduct.query.filter_by(invoice_id=invoice_get.id).all()
        product_list = models.product.Product.query.all()
        product_total_gramm = 0
        product_total_price = 0
        product_sold_count = 0
        for invoice_product in invoice_product_list:
            product = models.product.Product.query.filter_by(id=invoice_product.product_id).first()
            if product:
                product_total_gramm += product.gramm
                product_total_price += product.price
                if product.status == "SOLD":
                    product_sold_count += 1
        return render_template("/invoice/invoice_get.html", invoice=invoice_get, user=user_get, invoice_product_list=invoice_product_list, product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price, product_sold_count=product_sold_count)
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
            pro = int(pro)
            found_product = models.product.Product.query.filter_by(id=pro, status="NEW").first()
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
    form = CreateInvoiceProductForm()
    if form.validate_on_submit():
        val = form.hidden_field.data
        if val is None or val == "":
            flash("Product is not selected!", "danger")
            return redirect(url_for("invoice_product_create_page"))
        else:
            product_list = []
            val = val.split(",")
            for i in val:
                i = int(i)
                if i != -1:
                    found_product = models.product.Product.query.filter_by(id=i, status="NEW").first()
                    if found_product is None:
                        flash("Product not found!", "danger")
                        return redirect(url_for("invoice_product_create_page"))
                    else:
                        product_list.append(str(i))

            if len(product_list) == 0:
                flash("Product is not selected!", "danger")
                return redirect(url_for("invoice_product_create_page"))
            
            product_list = ",".join(product_list)
            flash("Products succesfully added!", "success")
            return redirect(url_for("invoice_create_page", product_list=product_list))
    else:
        query = request.args.get("search", None)
        if query:
            type = query[:1].upper()
            number = query[1:]
            if number and number.isdigit():
                product_list = models.product.Product.query.filter_by(status="NEW", type=type, number=number).order_by(models.product.Product.created_at.desc()).all()
            else:
                product_list = models.product.Product.query.filter_by(status="NEW", type=type).order_by(models.product.Product.created_at.desc()).all()
        else:
            product_list = models.product.Product.query.filter_by(status="NEW").order_by(models.product.Product.created_at.desc()).all()
        return render_template("invoice/invoice_product_create.html", form=form, product_list=product_list)

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
        product_total_gramm = 0
        product_total_price = 0
        for invoice_product in invoice_product_list:
            product = models.product.Product.query.filter_by(id=invoice_product.product_id).first()
            if product:
                product_total_gramm += product.gramm
                product_total_price += product.price
            else:
                continue
        return render_template("invoice/invoice_print.html", invoice=invoice_print, user=user_print, invoice_product_list=invoice_product_list, product_list=product_list, product_total_gramm=product_total_gramm, product_total_price=product_total_price)
    else:
        flash("Invoice not found", "danger")
        return redirect(url_for("invoice_list_page"))
