from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length

class PredictForm(FlaskForm):
    text = TextAreaField("Enter a text to detect its language:", validators=[DataRequired()])
    submit = SubmitField("Detect Language")

class EditProfileForm(FlaskForm):
    email = StringField("New Email", validators=[Optional(), Email()])
    password = PasswordField("New Password", validators=[Optional(), Length(min=6)])
    submit = SubmitField("Update Profile")
