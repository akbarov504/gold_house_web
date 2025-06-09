import models.user
from app import app
from models import db
from forms.user_form import LoginForm, UpdateProfileForm
from flask import render_template, redirect, url_for, flash, abort, session
from flask_login import login_required, login_user, logout_user, current_user

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page():
    if current_user.role == "DEALER" or current_user.role == "CLIENT":
        abort(403, "Ruxsat yetarli emas")
    else:
        form = UpdateProfileForm()
        if form.validate_on_submit():
            user = models.user.User.query.filter_by(id=current_user.id).first()
            user.full_name = form.full_name.data
            user.username = form.username.data
            user.phone_number = form.phone_number.data
            user.password = form.password.data
            db.session.commit()
            logout_user()
            return redirect(url_for("home_page"))
        else:
            form.full_name.data = current_user.full_name
            form.username.data = current_user.username
            form.phone_number.data = current_user.phone_number
            form.password.data = current_user.password
            return render_template("auth/profile.html", form=form)

@app.route("/logout", methods=["GET"])
@login_required
def logout_page():
    logout_user()
    return redirect(url_for("home_page"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = models.user.User.query.filter_by(username=username, password=password).first()
        if user is None:
            flash("Login yoki Parol hato", category="danger")
            return redirect(url_for("login_page"))
        elif user.role == "DEALER" or user.role == "CLIENT":
            abort(403, "Ruxsat yetarli emas")
        else:
            login_user(user)
            session.permanent = True
            flash("Tizimga muvaffaqiyatli kirdingiz", category="success")
            return redirect(url_for("home_page"))
    else:
        return render_template("auth/login.html", form=form)
