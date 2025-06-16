from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, validators

class CreateClientDebtForm(FlaskForm):
    client = SelectField("Client", choices=[])
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Add")

class CreateClientDebtWithIDForm(FlaskForm):
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Add")

class UpdateClientDebtForm(FlaskForm):
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Update")
