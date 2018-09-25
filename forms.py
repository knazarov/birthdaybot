import flask
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, IntegerField
from wtforms import DateTimeField

from wtforms.validators import DataRequired, Optional, Email
from wtforms.widgets import TextArea
from wtforms.fields.html5 import EmailField
from flask_security import forms as security_forms


class DepositForm(FlaskForm):
    amount = IntegerField('Amount',
                          validators=[DataRequired()])
    submit = SubmitField('Deposit')
