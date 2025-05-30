from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class PredictLanguageForm(FlaskForm):
    text = TextAreaField('Въведи текст:', validators=[DataRequired()])
    submit = SubmitField('Предскажи език')
