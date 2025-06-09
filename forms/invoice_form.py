from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField, validators, SubmitField

class CreateInvoiceForm(FlaskForm):
    dealer = SelectField("Dealer", [validators.DataRequired()], choices=[])
    submit = SubmitField("Add")

class UpdateInvoiceForm(FlaskForm):
    dealer = SelectField("Dealer", [validators.DataRequired()], choices=[])
    submit = SubmitField("Update")

class CreateInvoiceProductForm(FlaskForm):
    hidden_field = HiddenField("Hidden Field")
    submit = SubmitField("Save")
