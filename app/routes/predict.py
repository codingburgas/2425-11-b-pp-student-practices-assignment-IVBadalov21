from flask import Blueprint, render_template, request, flash
from ..forms.forms import PredictForm
import joblib

predict_bp = Blueprint("predict", __name__)

model = joblib.load("language_model.pkl")
fe = joblib.load("feature_extractor.pkl")
le = joblib.load("label_encoder.pkl")

@predict_bp.route("/predict", methods=["GET", "POST"])
def predict():
    form = PredictForm()
    prediction = None

    if form.validate_on_submit():
        text = form.text.data
        X = fe.transform([text])
        pred_class = model.predict(X[0])
        prediction = le.inverse_transform([pred_class])[0]
        flash(f"Detected language: {prediction}", "success")

    return render_template("predict.html", form=form, prediction=prediction)
