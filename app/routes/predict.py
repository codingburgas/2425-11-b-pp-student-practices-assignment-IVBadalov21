from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, Prediction
from ..forms.forms import PredictionForm
import joblib
import os

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def language_predict():
    form = PredictionForm()
    if form.validate_on_submit():
        prediction = Prediction(
            text=form.text.data,
            is_public=form.make_public.data,
            user_id=current_user.id
        )

        # Here you would add your language detection logic
        # For now, let's just set a dummy value
        prediction.predicted_language = "English"
        prediction.confidence = 0.95

        db.session.add(prediction)
        db.session.commit()

        flash(f'Text language detected as {prediction.predicted_language}!', 'success')
        return redirect(url_for('predict.language_predict'))

    return render_template('predict/predict.html', form=form)