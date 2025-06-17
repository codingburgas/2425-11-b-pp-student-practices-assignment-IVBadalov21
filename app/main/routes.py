from flask import render_template
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    # Placeholder for application statistics
    stats = {
        'total_users': 123,  # Example data
        'total_predictions': 4567, # Example data
        'total_surveys': 789, # Example data
        'model_accuracy': 0.92 # Example data
    }
    return render_template('index.html', title='Home', stats=stats)

@bp.route('/predict')
def predict():
    return render_template('predict.html', title='Predict Language')

@bp.route('/survey')
def survey():
    return render_template('survey.html', title='Language Survey')

@bp.route('/results')
def results():
    return render_template('results.html', title='Prediction Results')

@bp.route('/model_info')
def model_info():
    return render_template('model_info.html', title='Model Information')

@bp.route('/public_results')
def public_results():
    return render_template('results.html', title='Public Prediction Results')

@bp.route('/profile')
def profile():
    return render_template('user/profile.html', title='User Profile')

@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    return render_template('user/edit_profile.html', title='Edit Profile')

@bp.route('/prediction_feedback', methods=['POST'])
def prediction_feedback():
    # Placeholder for handling prediction feedback
    return "Prediction feedback submitted!"

@bp.route('/feedback/<int:prediction_id>', methods=['POST'])
def feedback(prediction_id):
    # Placeholder for handling specific prediction feedback
    return f"Feedback for prediction {prediction_id} submitted!" 