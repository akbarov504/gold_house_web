from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, validators

class CreateClientDebtForm(FlaskForm):
    client = SelectField("Client", [validators.DataRequired()], choices=[])
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Add")

class UpdateClientDebtForm(FlaskForm):
    client = SelectField("Client", [validators.DataRequired()], choices=[])
    lom = FloatField("Lom", [validators.DataRequired()])
    comment = StringField("Comment")
    submit = SubmitField("Update")
