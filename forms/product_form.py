from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, validators, SubmitField

class CreateProductForm(FlaskForm):
    title = StringField("Title", [validators.DataRequired(), validators.Length(min=4, max=255)])
    gramm = FloatField("Gramm", [validators.DataRequired()])
    proba = FloatField("Proba", [validators.DataRequired()])
    type = StringField("Type", [validators.DataRequired(), validators.Length(max=50)])
    number = IntegerField("Number", [validators.DataRequired()])
    size = FloatField("Size")
    submit = SubmitField("Add")

class UpdateProductForm(FlaskForm):
    title = StringField("Title", [validators.DataRequired(), validators.Length(min=4, max=255)])
    gramm = FloatField("Gramm", [validators.DataRequired()])
    proba = FloatField("Proba", [validators.DataRequired()])
    type = StringField("Type", [validators.DataRequired(), validators.Length(max=50)])
    number = IntegerField("Number", [validators.DataRequired()])
    size = FloatField("Size")
    submit = SubmitField("Update")
