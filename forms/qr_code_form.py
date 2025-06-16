from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, FloatField, validators, SubmitField

class CreateQRCodeForm(FlaskForm):
    title = SelectField("Title", [validators.DataRequired()])
    gramm = FloatField("Gramm", [validators.DataRequired()])
    proba = FloatField("Proba", [validators.DataRequired()], default=585)
    type = SelectField("Type", [validators.DataRequired()])
    number = IntegerField("Number", [validators.DataRequired()], default=1)
    size = FloatField("Size", default=0)
    submit = SubmitField("Add")
