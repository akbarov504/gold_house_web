from app import app
from models import db
import models.consumption
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from forms.consumption_form import CreateConsumptionForm, UpdateConsumptionForm

@app.route("/consumption/list", methods=["GET"])
@login_required
def consumption_list_page():
    consumption_list = models.consumption.Consumption.query.order_by(models.consumption.Consumption.created_at.desc()).all()
    return render_template("consumption/consumption_list.html", consumption_list=consumption_list)

@app.route("/consumption/create", methods=["GET", "POST"])
@login_required
def consumption_create_page():
    form = CreateConsumptionForm()
    if form.validate_on_submit():
        type = form.type.data
        comment = form.comment.data
        amount = form.amount.data

        new_consumption = models.consumption.Consumption(type=type, comment=comment, amount=amount)
        db.session.add(new_consumption)
        db.session.commit()

        flash("Consumption created successfully", "success")
        return redirect(url_for("consumption_list_page"))
    else:
        return render_template("consumption/consumption_create.html", form=form)

@app.route("/consumption/delete/<consumption_id>", methods=["GET", "POST"])
@login_required
def consumption_delete_page(consumption_id):
    if request.method == "POST":
        deleted_consumption = models.consumption.Consumption.query.filter_by(id=consumption_id).first()
        db.session.delete(deleted_consumption)
        db.session.commit()

        flash("Consumption successfully deleted", "warning")
        return redirect(url_for("consumption_list_page"))
    else:
        return render_template("consumption/consumption_delete.html", consumption_id=consumption_id)

@app.route("/consumption/update/<consumption_id>", methods=["GET", "POST"])
@login_required
def consumption_update_page(consumption_id):
    form = UpdateConsumptionForm()
    if form.validate_on_submit():
        type = form.type.data
        comment = form.comment.data
        amount = form.amount.data

        updated_consumption = models.consumption.Consumption.query.filter_by(id=consumption_id).first()
        updated_consumption.type = type
        updated_consumption.comment = comment
        updated_consumption.amount = amount
        db.session.commit()

        flash("Consumption updated successfully", "success")
        return redirect(url_for("consumption_list_page"))
    else:
        consumption = models.consumption.Consumption.query.filter_by(id=consumption_id).first()
        form.type.data = consumption.type
        form.comment.data = consumption.comment
        form.amount.data = consumption.amount
        return render_template("consumption/consumption_update.html", form=form)
