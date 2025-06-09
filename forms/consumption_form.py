from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, validators

class CreateConsumptionForm(FlaskForm):
    type = StringField("Type", [validators.DataRequired(), validators.Length(min=4, max=100)])
    comment = StringField("Comment", [validators.DataRequired(), validators.Length(min=4, max=300)])
    amount = FloatField("Amount", [validators.DataRequired()])
    submit = SubmitField("Add")

class UpdateConsumptionForm(FlaskForm):
    type = StringField("Type", [validators.DataRequired(), validators.Length(min=4, max=100)])
    comment = StringField("Comment", [validators.DataRequired(), validators.Length(min=4, max=300)])
    amount = FloatField("Amount", [validators.DataRequired()])
    submit = SubmitField("Update")
