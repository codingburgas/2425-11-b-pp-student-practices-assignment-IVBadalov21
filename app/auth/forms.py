from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Потвърди парола', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')
