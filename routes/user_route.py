import calendar
import models.user
from app import app
import models.invoice
from models import db
import models.client_debt
from datetime import date
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from forms.user_form import CreateClientForm, UpdateClientForm, CreateDealerForm, UpdateDealerForm

@app.route("/client/list", methods=["GET"])
@login_required
def client_list_page():
    client_list = models.user.User.query.filter_by(role="CLIENT").order_by(models.user.User.created_at.desc()).all()
    return render_template("user/client_list.html", client_list=client_list)

@app.route("/client/create", methods=["GET", "POST"])
@login_required
def client_create_page():
    form = CreateClientForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        phone_number = form.phone_number.data

        found_client = models.user.User.query.filter_by(phone_number=phone_number).first()
        if found_client is not None:
            flash("This phone number already exists", "danger")
            return redirect(url_for("client_create_page"))

        new_client = models.user.User(full_name=full_name, username=phone_number, phone_number=phone_number, password=phone_number, role="CLIENT")
        db.session.add(new_client)
        db.session.commit()

        flash("Client created successfully", "success")
        return redirect(url_for("client_list_page"))
    else:
        return render_template("user/client_create.html", form=form)

@app.route("/client/delete/<client_id>", methods=["GET", "POST"])
@login_required
def client_delete_page(client_id):
    if request.method == "POST":
        deleted_client = models.user.User.query.filter_by(id=client_id).first()
        client_debt_list = models.client_debt.ClientDebt.query.filter_by(user_id=deleted_client.id).all()
        for client_debt in client_debt_list:
            db.session.delete(client_debt)
        db.session.commit()
        db.session.delete(deleted_client)
        db.session.commit()

        flash("Client successfully deleted", "warning")
        return redirect(url_for("client_list_page"))
    else:
        return render_template("user/client_delete.html", client_id=client_id)

@app.route("/client/update/<client_id>", methods=["GET", "POST"])
@login_required
def client_update_page(client_id):
    form = UpdateClientForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        phone_number = form.phone_number.data

        found_client = models.user.User.query.filter_by(phone_number=phone_number).first()
        if found_client is not None and found_client.id != int(client_id):
            flash("This phone number already exists", "danger")
            return redirect(url_for("client_update_page", client_id=client_id))

        updated_client = models.user.User.query.filter_by(id=client_id).first()
        updated_client.full_name = full_name
        updated_client.phone_number = phone_number
        updated_client.username = phone_number
        updated_client.password = phone_number
        db.session.commit()

        flash("Client updated successfully", "success")
        return redirect(url_for("client_list_page"))
    else:
        client = models.user.User.query.filter_by(id=client_id).first()
        form.full_name.data = client.full_name
        form.phone_number.data = client.phone_number
        return render_template("user/client_update.html", form=form)

@app.route("/client/get/<client_id>", methods=["GET"])
@login_required
def client_get_page(client_id):
    client_get = models.user.User.query.filter_by(id=client_id, role="CLIENT").first()
    if client_get:
        client_total_debt = 0
        client_debt_list = models.client_debt.ClientDebt.query.filter_by(user_id=client_get.id).order_by(models.client_debt.ClientDebt.created_at.desc()).all()
        for client_debt in client_debt_list:
            client_total_debt += client_debt.lom
        return render_template("user/client_get.html", client=client_get, client_debt_list=client_debt_list, client_total_debt=client_total_debt)
    else:
        flash("Client not found", "danger")
        return redirect(url_for("client_list_page"))

@app.route("/dealer/list", methods=["GET"])
@login_required
def dealer_list_page():
    dealer_list = models.user.User.query.filter_by(role="DEALER").order_by(models.user.User.created_at.desc()).all()
    return render_template("user/dealer_list.html", dealer_list=dealer_list)

@app.route("/dealer/get/<dealer_id>", methods=["GET"])
@login_required
def dealer_get_page(dealer_id):
    dealer_get = models.user.User.query.filter_by(id=dealer_id, role="DEALER").first()
    if dealer_get:
        query_select = request.args.get("select_type", None)
        query_month = request.args.get("select_month", None)
        
        if query_select:
            if query_select == "ALL":
                invoice_list = models.invoice.Invoice.query.filter_by(user_id=dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_select == "NEW":
                invoice_list = models.invoice.Invoice.query.filter_by(user_id=dealer_get.id, status="NEW").order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_select == "COMPLETED":
                invoice_list = models.invoice.Invoice.query.filter_by(user_id=dealer_get.id, status="COMPLETED").order_by(models.invoice.Invoice.created_at.desc()).all()
        
        elif query_month:
            if query_month == "ALL":
                invoice_list = models.invoice.Invoice.query.filter_by(user_id=dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "JANUARY":
                start_date = date(date.today().year, 1, 1)
                end_date = date(date.today().year, 1, 31)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "FEBRUARY":
                start_date = date(date.today().year, 2, 1)
                end_date = date(date.today().year, 2, 28) if not calendar.isleap(date.today().year) else date(date.today().year, 2, 29)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "MARCH":
                start_date = date(date.today().year, 3, 1)
                end_date = date(date.today().year, 3, 31)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "APRIL":
                start_date = date(date.today().year, 4, 1)
                end_date = date(date.today().year, 4, 30)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "MAY":
                start_date = date(date.today().year, 5, 1)
                end_date = date(date.today().year, 5, 31)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "JUNE":
                start_date = date(date.today().year, 6, 1)
                end_date = date(date.today().year, 6, 30)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "JULY":
                start_date = date(date.today().year, 7, 1)
                end_date = date(date.today().year, 7, 31)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "AUGUST":
                start_date = date(date.today().year, 8, 1)
                end_date = date(date.today().year, 8, 31)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "SEPTEMBER":
                start_date = date(date.today().year, 9, 1)
                end_date = date(date.today().year, 9, 30)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "OCTOBER":
                start_date = date(date.today().year, 10, 1)
                end_date = date(date.today().year, 10, 31)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "NOVEMBER":
                start_date = date(date.today().year, 11, 1)
                end_date = date(date.today().year, 11, 30)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()
            elif query_month == "DECEMBER":
                start_date = date(date.today().year, 12, 1)
                end_date = date(date.today().year, 12, 31)
                invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date), models.invoice.Invoice.user_id == dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()

        else:
            invoice_list = models.invoice.Invoice.query.filter_by(user_id=dealer_get.id).order_by(models.invoice.Invoice.created_at.desc()).all()

        return render_template("user/dealer_get.html", dealer=dealer_get, invoice_list=invoice_list)
    else:
        flash("Dealer not found", "danger")
        return redirect(url_for("dealer_list_page"))

@app.route("/dealer/create", methods=["GET", "POST"])
@login_required
def dealer_create_page():
    form = CreateDealerForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        username = form.username.data
        phone_number = form.phone_number.data
        password = form.password.data

        found_dealer = models.user.User.query.filter_by(username=username).first()
        if found_dealer is not None:
            flash("This username already exists", "danger")
            return redirect(url_for("dealer_create_page"))

        found_dealer = models.user.User.query.filter_by(phone_number=phone_number).first()
        if found_dealer is not None:
            flash("This phone number already exists", "danger")
            return redirect(url_for("dealer_create_page"))

        new_dealer = models.user.User(full_name=full_name, username=username, phone_number=phone_number, password=password, role="DEALER")
        db.session.add(new_dealer)
        db.session.commit()

        flash("Dealer created successfully", "success")
        return redirect(url_for("dealer_list_page"))
    else:
        return render_template("user/dealer_create.html", form=form)

@app.route("/dealer/delete/<dealer_id>", methods=["GET", "POST"])
@login_required
def dealer_delete_page(dealer_id):
    if request.method == "POST":
        deleted_dealer = models.user.User.query.filter_by(id=dealer_id).first()
        
        try:
            db.session.delete(deleted_dealer)
            db.session.commit()
        except Exception as e:
            flash("This dealer cannot be deleted because before delete invoice", "danger")
            return redirect(url_for("dealer_list_page"))

        flash("Dealer successfully deleted", "warning")
        return redirect(url_for("dealer_list_page"))
    else:
        return render_template("user/dealer_delete.html", dealer_id=dealer_id)

@app.route("/dealer/update/<dealer_id>", methods=["GET", "POST"])
@login_required
def dealer_update_page(dealer_id):
    form = UpdateDealerForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        username = form.username.data
        phone_number = form.phone_number.data
        password = form.password.data

        found_dealer = models.user.User.query.filter_by(username=username).first()
        if found_dealer is not None and found_dealer.id != int(dealer_id):
            flash("This username already exists", "danger")
            return redirect(url_for("dealer_update_page", dealer_id=dealer_id))

        found_dealer = models.user.User.query.filter_by(phone_number=phone_number).first()
        if found_dealer is not None and found_dealer.id != int(dealer_id):
            flash("This phone number already exists", "danger")
            return redirect(url_for("dealer_update_page", dealer_id=dealer_id))

        updated_dealer = models.user.User.query.filter_by(id=dealer_id).first()
        updated_dealer.full_name = full_name
        updated_dealer.username = username
        updated_dealer.phone_number = phone_number
        updated_dealer.password = password
        db.session.commit()

        flash("Dealer updated successfully", "success")
        return redirect(url_for("dealer_list_page"))
    else:
        dealer = models.user.User.query.filter_by(id=dealer_id).first()
        form.full_name.data = dealer.full_name
        form.username.data = dealer.username
        form.phone_number.data = dealer.phone_number
        form.password.data = dealer.password
        return render_template("user/dealer_update.html", form=form)
