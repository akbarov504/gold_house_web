from app import app
from models import db
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from forms.room_form import CreateRoomForm, UpdateRoomForm
import models.room_t

@app.route("/room/create/<main_system_id>", methods=["GET", "POST"])
@login_required
def room_create_page(main_system_id):
    form = CreateRoomForm()
    if form.validate_on_submit():
        lom = form.lom.data
        comment = form.comment.data

        new_room = models.room_t.RoomT(lom=lom, comment=comment, main_system_id=main_system_id)
        db.session.add(new_room)
        db.session.commit()

        flash("Room created successfully", "success")
        return redirect(url_for("main_system_list_page"))
    else:
        return render_template("room/room_create.html", form=form)

@app.route("/room/delete/<room_id>", methods=["GET", "POST"])
@login_required
def room_delete_page(room_id):
    if request.method == "POST":
        deleted_room = models.room_t.RoomT.query.filter_by(id=room_id).first()
        db.session.delete(deleted_room)
        db.session.commit()

        flash("Room successfully deleted", "warning")
        return redirect(url_for("main_system_list_page"))
    else:
        return render_template("room/room_delete.html", room_id=room_id)

@app.route("/room/update/<room_id>", methods=["GET", "POST"])
@login_required
def room_update_page(room_id):
    form = UpdateRoomForm()
    if form.validate_on_submit():
        lom = form.lom.data
        comment = form.comment.data

        updated_room = models.room_t.RoomT.query.filter_by(id=room_id).first()
        updated_room.lom = lom
        updated_room.comment = comment
        db.session.commit()

        flash("Room updated successfully", "success")
        return redirect(url_for("main_system_list_page"))
    else:
        room = models.room_t.RoomT.query.filter_by(id=room_id).first()
        form.lom.data = room.lom
        form.comment.data = room.comment
        return render_template("room/room_update.html", form=form, room_id=room_id)

