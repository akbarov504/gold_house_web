from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, validators

class CreateRoomForm(FlaskForm):
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Add")

class UpdateRoomForm(FlaskForm):
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Update")
