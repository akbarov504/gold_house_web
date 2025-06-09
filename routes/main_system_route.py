from app import app
from models import db
import models.main_system
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from forms.main_system_form import CreateMainSystemForm, UpdateMainSystemForm
import models.room_t

@app.route("/main_system/list", methods=["GET"])
@login_required
def main_system_list_page():
    main_system_list = models.main_system.MainSystem.query.order_by(models.main_system.MainSystem.created_at.desc()).all()
    room_list = models.room_t.RoomT.query.order_by(models.room_t.RoomT.created_at.desc()).all()
    return render_template("main_system/main_system_list.html", main_system_list=main_system_list, room_list=room_list)

@app.route("/main_system/create", methods=["GET", "POST"])
@login_required
def main_system_create_page():
    form = CreateMainSystemForm()
    if form.validate_on_submit():
        lom = form.lom.data
        comment = form.comment.data

        new_main_system = models.main_system.MainSystem(lom=lom, comment=comment)
        db.session.add(new_main_system)
        db.session.commit()

        flash("Main system created successfully", "success")
        return redirect(url_for("main_system_list_page"))
    else:
        return render_template("main_system/main_system_create.html", form=form)

@app.route("/main_system/delete/<main_system_id>", methods=["GET", "POST"])
@login_required
def main_system_delete_page(main_system_id):
    if request.method == "POST":
        deleted_main_system = models.main_system.MainSystem.query.filter_by(id=main_system_id).first()
        room_list = models.room_t.RoomT.query.filter_by(main_system_id=deleted_main_system.id).all()
        for room in room_list:
            db.session.delete(room)

        db.session.commit()
        db.session.delete(deleted_main_system)
        db.session.commit()

        flash("Main system successfully deleted", "warning")
        return redirect(url_for("main_system_list_page"))
    else:
        return render_template("main_system/main_system_delete.html", main_system_id=main_system_id)

@app.route("/main_system/update/<main_system_id>", methods=["GET", "POST"])
@login_required
def main_system_update_page(main_system_id):
    form = UpdateMainSystemForm()
    if form.validate_on_submit():
        lom = form.lom.data
        comment = form.comment.data

        updated_main_system = models.main_system.MainSystem.query.filter_by(id=main_system_id).first()
        updated_main_system.lom = lom
        updated_main_system.comment = comment
        db.session.commit()

        flash("Main system updated successfully", "success")
        return redirect(url_for("main_system_list_page"))
    else:
        main_system = models.main_system.MainSystem.query.filter_by(id=main_system_id).first()
        form.lom.data = main_system.lom
        form.comment.data = main_system.comment
        return render_template("main_system/main_system_update.html", form=form, main_system_id=main_system_id)

@app.route("/main_system/get/<main_system_id>", methods=["GET"])
@login_required
def main_system_get_page(main_system_id):
    main_system = models.main_system.MainSystem.query.filter_by(id=main_system_id).first()
    if main_system:
        total_room = 0
        room_list = models.room_t.RoomT.query.filter_by(main_system_id=main_system_id).order_by(models.room_t.RoomT.created_at.desc()).all()
        for room in room_list:
            total_room += room.lom
        return render_template("main_system/main_system_get.html", main_system=main_system, room_list=room_list, total_room=total_room)
    else:
        flash("Main system not found", "danger")
        return redirect(url_for("main_system_list_page"))
