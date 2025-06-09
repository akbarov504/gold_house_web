from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, validators

class CreateSalaryForm(FlaskForm):
    type = StringField("Type", [validators.DataRequired(), validators.Length(max=10)])
    amount = FloatField("Amount", [validators.DataRequired()])
    submit = SubmitField("Add")

class UpdateSalaryForm(FlaskForm):
    type = StringField("Type", [validators.DataRequired(), validators.Length(max=10)])
    amount = FloatField("Amount", [validators.DataRequired()])
    submit = SubmitField("Update")
