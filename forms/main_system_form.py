from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, validators

class CreateMainSystemForm(FlaskForm):
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Add")

class UpdateMainSystemForm(FlaskForm):
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Update")
