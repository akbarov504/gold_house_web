from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, TelField

class LoginForm(FlaskForm):
    username = StringField("Login", [validators.DataRequired(), validators.Length(min=4, max=80)])
    password = PasswordField("Parol", [validators.DataRequired(), validators.Length(min=8, max=120)])
    submit = SubmitField("Kirish")

class CreateWorkerForm(FlaskForm):
    full_name = StringField("Full Name", [validators.DataRequired(), validators.Length(min=4, max=80)])
    username = StringField("Username", [validators.DataRequired(), validators.Length(min=4, max=80)])
    phone_number = TelField("Phone Number", [validators.DataRequired(), validators.Length(min=13, max=20)])
    password = PasswordField("Password", [validators.DataRequired(), validators.Length(min=8, max=120)])
    submit = SubmitField("Add")

class UpdateProfileForm(FlaskForm):
    full_name = StringField("Full Name", [validators.DataRequired(), validators.Length(min=4, max=80)])
    username = StringField("Username", [validators.DataRequired(), validators.Length(min=4, max=80)])
    phone_number = TelField("Phone Number", [validators.DataRequired(), validators.Length(min=13, max=20)])
    password = PasswordField("Password", [validators.DataRequired(), validators.Length(min=8, max=120)])
    submit = SubmitField("Update")

class CreateClientForm(FlaskForm):
    full_name = StringField("Full Name", [validators.DataRequired(), validators.Length(min=4, max=80)])
    phone_number = TelField("Phone Number", [validators.DataRequired(), validators.Length(min=13, max=20)])
    submit = SubmitField("Add")

class UpdateClientForm(FlaskForm):
    full_name = StringField("Full Name", [validators.DataRequired(), validators.Length(min=4, max=80)])
    phone_number = TelField("Phone Number", [validators.DataRequired(), validators.Length(min=13, max=20)])
    submit = SubmitField("Update")

class CreateDealerForm(FlaskForm):
    full_name = StringField("Full Name", [validators.DataRequired(), validators.Length(min=4, max=80)])
    username = StringField("Username", [validators.DataRequired(), validators.Length(min=4, max=80)])
    phone_number = TelField("Phone Number", [validators.DataRequired(), validators.Length(min=13, max=20)])
    password = PasswordField("Password", [validators.DataRequired(), validators.Length(min=8, max=120)])
    submit = SubmitField("Add")

class UpdateDealerForm(FlaskForm):
    full_name = StringField("Full Name", [validators.DataRequired(), validators.Length(min=4, max=80)])
    username = StringField("Username", [validators.DataRequired(), validators.Length(min=4, max=80)])
    phone_number = TelField("Phone Number", [validators.DataRequired(), validators.Length(min=13, max=20)])
    password = PasswordField("Password", [validators.DataRequired(), validators.Length(min=8, max=120)])
    submit = SubmitField("Update")
