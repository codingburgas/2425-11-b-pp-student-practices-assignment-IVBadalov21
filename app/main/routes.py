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

@bp.route('/predict', methods=['GET', 'POST'])
def predict():
    """Language prediction interface"""
    from app.forms.forms import PredictionForm
    from flask_login import current_user, login_required
    from flask import flash, redirect, url_for, current_app
    from app.models import Prediction
    from app.extensions import db
    from app.core.utils import get_or_create_model
    import time
    import logging

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

            # Save prediction to database if user is logged in
            if current_user.is_authenticated:
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

                prediction_id = prediction.id
            else:
                prediction_id = None

            # Prepare result for display
            prediction_result = {
                'predicted_language': predicted_language,
                'language_name': current_app.config['LANGUAGE_NAMES'][predicted_language],
                'confidence_scores': confidence_scores,
                'processing_time': processing_time,
                'prediction_id': prediction_id
            }

            flash('Prediction completed successfully!', 'success')

        except Exception as e:
            logging.error(f"Prediction error: {e}")
            flash('An error occurred during prediction. Please try again.', 'danger')

    return render_template('predict.html', title='Language Prediction', 
                         form=form, prediction_result=prediction_result)

@bp.route('/survey', methods=['GET', 'POST'])
def survey():
    """Language survey interface for collecting training data"""
    from app.forms.forms import SurveyForm
    from flask_login import current_user
    from flask import flash, redirect, url_for
    from app.models import Survey
    from app.extensions import db

    form = SurveyForm()
    user_surveys = []

    # Get user's recent surveys if logged in
    if current_user.is_authenticated:
        user_surveys = Survey.query.filter_by(user_id=current_user.id)\
                                  .order_by(Survey.created_at.desc())\
                                  .limit(10).all()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please log in to submit survey data.', 'warning')
            return redirect(url_for('auth.login'))

        # Create new survey entry
        survey = Survey(
            user_id=current_user.id,
            text_sample=form.text_sample.data,
            language=form.language.data,
            confidence=form.confidence.data
        )

        db.session.add(survey)
        db.session.commit()

        flash('Thank you for your contribution! Your survey has been submitted.', 'success')
        return redirect(url_for('main.survey'))

    return render_template('survey.html', title='Language Survey', 
                         form=form, user_surveys=user_surveys)

@bp.route('/results')
def results():
    """User's prediction results"""
    from flask_login import current_user, login_required
    from flask import request, current_app, redirect, url_for, flash
    from app.models import Prediction
    
    if not current_user.is_authenticated:
        flash('Please log in to view your results.', 'warning')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = getattr(current_app.config, 'RESULTS_PER_PAGE', 10)
    
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
                                 .order_by(Prediction.created_at.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
    
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
    # Placeholder for handling prediction feedback
    return "Prediction feedback submitted!"

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