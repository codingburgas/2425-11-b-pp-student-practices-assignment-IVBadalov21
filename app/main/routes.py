from flask import render_template, Blueprint, request
from app.main.forms import PredictLanguageForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    form = PredictLanguageForm()
    prediction = None

    if form.validate_on_submit():
        text = form.text.data
        # Тук по-късно ще използваме модела:
        prediction = f"Предсказан език: (примерно: English) за '{text[:30]}...'"

    return render_template('index.html', form=form, prediction=prediction)
