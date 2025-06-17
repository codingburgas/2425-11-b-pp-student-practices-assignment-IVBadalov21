from flask import render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import time
import logging
import json

from app.main import bp
from app.models import User, Prediction, db
from app.forms.forms import PredictionForm
from app.core.perceptron import MultiClassPerceptron
from app.core.utils import get_or_create_model

@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html', title='Language Detector')

@bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Language prediction interface"""
    form = PredictionForm()
    
    if form.validate_on_submit():
        start_time = time.time()
        
        # Get the pre-trained model
        model = get_or_create_model()
        
        # Make prediction
        prediction_result = model.predict(form.input_text.data)
        processing_time = time.time() - start_time
        
        # Create prediction record
        prediction = Prediction(
            user_id=current_user.id if current_user.is_authenticated else None,
            input_text=form.input_text.data,
            predicted_language=prediction_result['language'],
            confidence_scores=json.dumps(prediction_result['scores']),
            processing_time=processing_time,
            is_public=form.make_public.data if hasattr(form, 'make_public') else False
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return render_template('predict.html', title='Language Detection',
                             form=form, prediction_result=prediction)
    
    return render_template('predict.html', title='Language Detection', form=form)

@bp.route('/results')
@login_required
def results():
    """User's prediction history"""
    page = request.args.get('page', 1, type=int)
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
                                .order_by(Prediction.created_at.desc())\
                                .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('results.html', title='My Results',
                         predictions=predictions, public_view=False)

@bp.route('/model_info')
def model_info():
    """Display model information and training metrics"""
    from app.core.utils import get_or_create_model
    from app.models import ModelTraining, Survey
    from app.extensions import db
    from flask import flash, redirect, url_for
    import logging

    try:
        model = get_or_create_model()
        model_summary = model.get_model_summary()
        
        # Get latest training metrics
        latest_training = ModelTraining.query.order_by(ModelTraining.training_date.desc()).first()
        
        # Get training history
        training_history = ModelTraining.query.order_by(ModelTraining.training_date.desc()).limit(10).all()
        
        # Get survey statistics
        survey_stats = db.session.query(Survey.language, db.func.count(Survey.id))\
                                .group_by(Survey.language).all()
        
        return render_template('model_info.html', title='Model Information',
                             model_summary=model_summary,
                             latest_training=latest_training,
                             training_history=training_history,
                             survey_stats=survey_stats)
    
    except Exception as e:
        logging.error(f"Error getting model info: {e}")
        flash('Error loading model information.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/public_results')
def public_results():
    """Public prediction results"""
    from flask import request, current_app
    from app.models import Prediction
    
    page = request.args.get('page', 1, type=int)
    per_page = getattr(current_app.config, 'RESULTS_PER_PAGE', 10)
    
    predictions = Prediction.query.filter_by(is_public=True)\
                                 .order_by(Prediction.created_at.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('results.html', title='Public Prediction Results', 
                         predictions=predictions, public_view=True)

@bp.route('/profile')
def profile():
    """User profile page"""
    from flask_login import current_user, login_required
    from flask import redirect, url_for, flash
    from app.models import Survey, Prediction
    from app.extensions import db
    
    if not current_user.is_authenticated:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get user statistics
    user_stats = {
        'surveys_contributed': Survey.query.filter_by(user_id=current_user.id).count(),
        'predictions_made': Prediction.query.filter_by(user_id=current_user.id).count(),
        'public_predictions': Prediction.query.filter_by(user_id=current_user.id, is_public=True).count(),
        'member_since': current_user.registered_on,
        'last_seen': current_user.last_seen
    }
    
    # Get language distribution of user's surveys
    survey_langs = db.session.query(Survey.language, db.func.count(Survey.id))\
                            .filter_by(user_id=current_user.id)\
                            .group_by(Survey.language).all()
    
    language_stats = {lang: count for lang, count in survey_langs}
    
    return render_template('user/profile.html', title='Profile', 
                         user_stats=user_stats, language_stats=language_stats)

@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile"""
    from flask_login import current_user, login_required
    from flask import request, flash, redirect, url_for
    from app.forms.forms import EditProfileForm
    from app.extensions import db
    
    if not current_user.is_authenticated:
        flash('Please log in to edit your profile.', 'warning')
        return redirect(url_for('auth.login'))
    
    form = EditProfileForm(original_email=current_user.email)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('main.profile'))
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    
    return render_template('user/edit_profile.html', title='Edit Profile', form=form)

@bp.route('/prediction_feedback', methods=['POST'])
def prediction_feedback():
    # Handle feedback logic here (if any)
    flash("Thank you for your feedback!", "success")
    return redirect(url_for('main.results'))

@bp.route('/feedback/<int:prediction_id>', methods=['POST'])
def feedback(prediction_id):
    """Provide feedback on prediction accuracy"""
    from flask_login import current_user, login_required
    from flask import request, flash, redirect, url_for, current_app
    from app.models import Prediction
    from app.extensions import db

    prediction = Prediction.query.get_or_404(prediction_id)

    if current_user.is_authenticated and prediction.user_id != current_user.id:
        flash('You can only provide feedback on your own predictions.', 'danger')
        return redirect(url_for('main.results'))

    actual_language = request.form.get('actual_language')
    if actual_language in current_app.config['LANGUAGES']:
        prediction.actual_language = actual_language

        # Calculate accuracy
        prediction.accuracy_score = 1.0 if prediction.predicted_language == actual_language else 0.0

        db.session.commit()
        flash('Thank you for your feedback!', 'success')
    else:
        flash('Invalid language selection.', 'danger')

    return redirect(url_for('main.predict'))