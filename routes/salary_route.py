from app import app
import models.salary
from models import db
from flask_login import login_required
from forms.salary_form import CreateSalaryForm, UpdateSalaryForm
from flask import render_template, redirect, url_for, flash, request

@app.route("/salary/list", methods=["GET"])
@login_required
def salary_list_page():
    salary_list = models.salary.Salary.query.order_by(models.salary.Salary.created_at.desc()).all()
    return render_template("salary/salary_list.html", salary_list=salary_list)

@app.route("/salary/create", methods=["GET", "POST"])
@login_required
def salary_create_page():
    form = CreateSalaryForm()
    if form.validate_on_submit():
        type = form.type.data
        amount = form.amount.data

        found_salary = models.salary.Salary.query.filter_by(type=type).first()
        if found_salary is not None:
            flash("This type already exists", "danger")
            return redirect(url_for("salary_create_page"))

        new_salary = models.salary.Salary(type=type, amount=amount)
        db.session.add(new_salary)
        db.session.commit()

        flash("Salary created successfully", "success")
        return redirect(url_for("salary_list_page"))
    else:
        return render_template("salary/salary_create.html", form=form)

@app.route("/salary/delete/<salary_id>", methods=["GET", "POST"])
@login_required
def salary_delete_page(salary_id):
    if request.method == "POST":
        deleted_salary = models.salary.Salary.query.filter_by(id=salary_id).first()
        db.session.delete(deleted_salary)
        db.session.commit()

        flash("Salary successfully deleted", "warning")
        return redirect(url_for("salary_list_page"))
    else:
        return render_template("salary/salary_delete.html", salary_id=salary_id)

@app.route("/salary/update/<salary_id>", methods=["GET", "POST"])
@login_required
def salary_update_page(salary_id):
    form = UpdateSalaryForm()
    if form.validate_on_submit():
        type = form.type.data
        amount = form.amount.data

        found_salary = models.salary.Salary.query.filter_by(type=type).first()
        if found_salary is not None and found_salary.id != int(salary_id):
            flash("This type already exists", "danger")
            return redirect(url_for("salary_update_page", salary_id=salary_id))

        updated_salary = models.salary.Salary.query.filter_by(id=salary_id).first()
        updated_salary.type = type
        updated_salary.amount = amount
        db.session.commit()

        flash("Salary updated successfully", "success")
        return redirect(url_for("salary_list_page"))
    else:
        salary = models.salary.Salary.query.filter_by(id=salary_id).first()
        form.type.data = salary.type
        form.amount.data = salary.amount
        return render_template("salary/salary_update.html", form=form)
