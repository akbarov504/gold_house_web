import models.user
from app import app
from models import db
import models.client_debt
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from forms.client_debt_form import CreateClientDebtForm, UpdateClientDebtForm, CreateClientDebtWithIDForm

@app.route("/client_debt/create", methods=["GET", "POST"])
@login_required
def client_debt_create_page():
    form = CreateClientDebtForm()
    client_list = models.user.User.query.filter_by(role="CLIENT").all()
    form.client.choices = [(client.id, client.full_name) for client in client_list]

    if form.validate_on_submit():
        client = form.client.data

        client_get = models.user.User.query.filter_by(id=client, role="CLIENT").first()
        if client_get is None:
            flash("Client not found", "danger")
            return redirect(url_for("client_debt_create_page"))

        lom = form.lom.data
        comment = form.comment.data

        new_client_debt = models.client_debt.ClientDebt(user_id=client_get.id, lom=lom, comment=comment)
        db.session.add(new_client_debt)
        db.session.commit()

        flash("Client debt created successfully", "success")
        return redirect(url_for("client_list_page"))
    else:
        return render_template("client_debt/client_debt_create.html", form=form)
    
@app.route("/client_debt/create/<client_id>", methods=["GET", "POST"])
@login_required
def client_debt_create_page_with_id(client_id):
    form = CreateClientDebtWithIDForm()
    if form.validate_on_submit():
        client_get = models.user.User.query.filter_by(id=client_id, role="CLIENT").first()
        if client_get is None:
            flash("Client not found", "danger")
            return redirect(url_for("client_debt_create_page"))

        lom = form.lom.data
        comment = form.comment.data

        new_client_debt = models.client_debt.ClientDebt(user_id=client_get.id, lom=lom, comment=comment)
        db.session.add(new_client_debt)
        db.session.commit()

        flash("Client debt created successfully", "success")
        return redirect(url_for("client_list_page"))
    else:
        return render_template("client_debt/client_debt_create_with_id.html", form=form, client_id=client_id)

@app.route("/client_debt/delete/<client_debt_id>", methods=["GET", "POST"])
@login_required
def client_debt_delete_page(client_debt_id):
    if request.method == "POST":
        deleted_client_debt = models.client_debt.ClientDebt.query.filter_by(id=client_debt_id).first()
        db.session.delete(deleted_client_debt)
        db.session.commit()

        flash("Client debt successfully deleted", "warning")
        return redirect(url_for("client_list_page"))
    else:
        return render_template("client_debt/client_debt_delete.html", client_debt_id=client_debt_id)

@app.route("/client_debt/update/<client_id>/<client_debt_id>", methods=["GET", "POST"])
@login_required
def client_debt_update_page(client_id, client_debt_id):
    form = UpdateClientDebtForm()
    if form.validate_on_submit():
        lom = form.lom.data
        comment = form.comment.data

        update_client_debt = models.client_debt.ClientDebt.query.filter_by(id=client_debt_id).first()
        update_client_debt.client = client_id
        update_client_debt.lom = lom
        update_client_debt.comment = comment
        db.session.commit()

        flash("Client debt updated successfully", "success")
        return redirect(url_for("client_list_page"))
    else:
        client_debt = models.client_debt.ClientDebt.query.filter_by(id=client_debt_id).first()
        form.lom.data = client_debt.lom
        form.comment.data = client_debt.comment
        return render_template("client_debt/client_debt_update.html", form=form, client_debt_id=client_debt_id, client_id=client_id)
