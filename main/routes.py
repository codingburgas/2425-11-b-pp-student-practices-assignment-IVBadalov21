from flask import render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import time
import logging

from main import bp
from app.models import User, Survey, Prediction, ModelTraining, db
from app.forms.forms import SurveyForm, PredictionForm
from app.core.perceptron import MultiClassPerceptron
from app.core.utils import get_or_create_model, save_model_training_metrics

@bp.route('/')
def index():
    """Home page"""
    # Get some statistics for the homepage
    stats = {
        'total_users': User.query.count(),
        'total_surveys': Survey.query.count(),
        'total_predictions': Prediction.query.count(),
        'supported_languages': len(current_app.config['LANGUAGES'])
    }
    
    # Get recent public predictions
    recent_predictions = Prediction.query.filter_by(is_public=True)\
                                        .order_by(Prediction.created_at.desc())\
                                        .limit(5).all()
    
    return render_template('index.html', title='Language Detector', 
                         stats=stats, recent_predictions=recent_predictions)

@bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    """Survey form for collecting training data"""
    form = SurveyForm()
    
    if form.validate_on_submit():
        survey_entry = Survey(
            user_id=current_user.id,
            text_sample=form.text_sample.data,
            language=form.language.data,
            confidence=form.confidence.data
        )
        
        db.session.add(survey_entry)
        db.session.commit()
        
        flash('Thank you for contributing to our language detection model!', 'success')
        return redirect(url_for('main.survey'))
    
    # Get user's previous surveys
    user_surveys = Survey.query.filter_by(user_id=current_user.id)\
                              .order_by(Survey.created_at.desc())\
                              .limit(10).all()
    
    return render_template('survey.html', title='Language Survey', 
                         form=form, user_surveys=user_surveys)

@bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Language prediction interface"""
    form = PredictionForm()
    prediction_result = None
    
    if form.validate_on_submit():
        start_time = time.time()
        
        try:
            # Get or create the trained model
            model = get_or_create_model()
            
            if not model.is_trained:
                flash('The model is not trained yet. Please contribute to surveys first.', 'warning')
                return redirect(url_for('main.survey'))
            
            # Make prediction
            input_text = form.input_text.data
            predicted_language = model.predict(input_text)
            confidence_scores = model.predict_proba(input_text)
            
            processing_time = time.time() - start_time
            
            # Save prediction to database
            prediction = Prediction(
                user_id=current_user.id,
                input_text=input_text,
                predicted_language=predicted_language,
                processing_time=processing_time,
                is_public=form.make_public.data
            )
            prediction.set_confidence_scores(confidence_scores)
            
            db.session.add(prediction)
            db.session.commit()
            
            # Prepare result for display
            prediction_result = {
                'predicted_language': predicted_language,
                'language_name': current_app.config['LANGUAGE_NAMES'][predicted_language],
                'confidence_scores': confidence_scores,
                'processing_time': processing_time,
                'prediction_id': prediction.id
            }
            
            flash('Prediction completed successfully!', 'success')
            
        except Exception as e:
            logging.error(f"Prediction error: {e}")
            flash('An error occurred during prediction. Please try again.', 'danger')
    
    return render_template('predict.html', title='Language Prediction', 
                         form=form, prediction_result=prediction_result)

@bp.route('/results')
@login_required
def results():
    """User's prediction results"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RESULTS_PER_PAGE']
    
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
                                 .order_by(Prediction.created_at.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('results.html', title='My Results', predictions=predictions)

@bp.route('/public_results')
def public_results():
    """Public prediction results"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RESULTS_PER_PAGE']
    
    predictions = Prediction.query.filter_by(is_public=True)\
                                 .order_by(Prediction.created_at.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('results.html', title='Public Results', 
                         predictions=predictions, public_view=True)

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
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
@login_required
def edit_profile():
    """Edit user profile"""
    from forms import EditProfileForm
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

@bp.route('/model_info')
def model_info():
    """Display model information and training metrics"""
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

@bp.route('/feedback/<int:prediction_id>', methods=['POST'])
@login_required
def prediction_feedback():
    """Provide feedback on prediction accuracy"""
    prediction = Prediction.query.get_or_404(prediction_id)
    
    if prediction.user_id != current_user.id:
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
    
    return redirect(url_for('main.results'))
