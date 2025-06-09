import models.user
from app import app
from models import db
from flask_login import login_required
from forms.user_form import CreateWorkerForm
from flask import render_template, redirect, url_for, flash, request

@app.route("/worker/list", methods=["GET"])
@login_required
def worker_list_page():
    worker_list = models.user.User.query.filter_by(role="WORKER").order_by(models.user.User.created_at.desc()).all()
    return render_template("worker/worker_list.html", worker_list=worker_list)

@app.route("/worker/create", methods=["GET", "POST"])
@login_required
def worker_create_page():
    form = CreateWorkerForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        username = form.username.data
        phone_number = form.phone_number.data
        password = form.password.data

        found_worker = models.user.User.query.filter_by(username=username).first()
        if found_worker is not None:
            flash("This username already exists", "danger")
            return redirect(url_for("worker_create_page"))

        new_worker = models.user.User(full_name=full_name, username=username, phone_number=phone_number, password=password, role="WORKER")
        db.session.add(new_worker)
        db.session.commit()

        flash("Worker created successfully", "success")
        return redirect(url_for("worker_list_page"))
    else:
        return render_template("worker/worker_create.html", form=form)

@app.route("/worker/delete/<worker_id>", methods=["GET", "POST"])
@login_required
def worker_delete_page(worker_id):
    if request.method == "POST":
        deleted_worker = models.user.User.query.filter_by(id=worker_id).first()
        db.session.delete(deleted_worker)
        db.session.commit()

        flash("Worker successfully deleted", "warning")
        return redirect(url_for("worker_list_page"))
    else:
        return render_template("worker/worker_delete.html", worker_id=worker_id)
