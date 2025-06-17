from flask import render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import logging

from admin import bp
from app.models import User, Survey, Prediction, ModelTraining, db
from app.forms.forms import EditUserForm
from app.core.utils import get_or_create_model, train_model_with_surveys

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get system statistics
    stats = {
        'total_users': User.query.count(),
        'confirmed_users': User.query.filter_by(is_confirmed=True).count(),
        'admin_users': User.query.filter_by(is_admin=True).count(),
        'total_surveys': Survey.query.count(),
        'approved_surveys': Survey.query.filter_by(is_approved=True).count(),
        'total_predictions': Prediction.query.count(),
        'public_predictions': Prediction.query.filter_by(is_public=True).count()
    }
    
    # Get recent activity
    recent_users = User.query.order_by(User.registered_on.desc()).limit(5).all()
    recent_surveys = Survey.query.order_by(Survey.created_at.desc()).limit(5).all()
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()
    
    # Get language distribution
    survey_langs = db.session.query(Survey.language, db.func.count(Survey.id))\
                            .group_by(Survey.language).all()
    language_distribution = {lang: count for lang, count in survey_langs}
    
    # Get model training history
    training_history = ModelTraining.query.order_by(ModelTraining.training_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                         stats=stats, recent_users=recent_users,
                         recent_surveys=recent_surveys, recent_predictions=recent_predictions,
                         language_distribution=language_distribution,
                         training_history=training_history)

@bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RESULTS_PER_PAGE']
    
    users = User.query.order_by(User.registered_on.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', title='Manage Users', users=users)

@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_admin = form.is_admin.data
        user.is_confirmed = form.is_confirmed.data
        
        if not user.is_confirmed and form.is_confirmed.data:
            user.confirmed_on = datetime.utcnow()
        
        db.session.commit()
        flash(f'User {user.username} has been updated.', 'success')
        return redirect(url_for('admin.users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.is_admin.data = user.is_admin
        form.is_confirmed.data = user.is_confirmed
    
    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/surveys')
@login_required
@admin_required
def surveys():
    """Manage surveys"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RESULTS_PER_PAGE']
    
    surveys = Survey.query.order_by(Survey.created_at.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/surveys.html', title='Manage Surveys', surveys=surveys)

@bp.route('/approve_survey/<int:survey_id>')
@login_required
@admin_required
def approve_survey(survey_id):
    """Approve survey entry"""
    survey = Survey.query.get_or_404(survey_id)
    survey.is_approved = True
    db.session.commit()
    
    flash('Survey approved.', 'success')
    return redirect(url_for('admin.surveys'))

@bp.route('/reject_survey/<int:survey_id>')
@login_required
@admin_required
def reject_survey(survey_id):
    """Reject survey entry"""
    survey = Survey.query.get_or_404(survey_id)
    survey.is_approved = False
    db.session.commit()
    
    flash('Survey rejected.', 'warning')
    return redirect(url_for('admin.surveys'))

@bp.route('/delete_survey/<int:survey_id>', methods=['POST'])
@login_required
@admin_required
def delete_survey(survey_id):
    """Delete survey entry"""
    survey = Survey.query.get_or_404(survey_id)
    db.session.delete(survey)
    db.session.commit()
    
    flash('Survey deleted.', 'success')
    return redirect(url_for('admin.surveys'))

@bp.route('/train_model', methods=['POST'])
@login_required
@admin_required
def train_model():
    """Trigger model training"""
    try:
        # Train model with approved surveys
        metrics = train_model_with_surveys()
        
        if metrics:
            flash(f'Model training completed! Accuracy: {metrics["accuracy"]:.3f}', 'success')
        else:
            flash('Not enough training data available.', 'warning')
    
    except Exception as e:
        logging.error(f"Model training error: {e}")
        flash('An error occurred during model training.', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/model_metrics')
@login_required
@admin_required
def model_metrics():
    """View detailed model metrics"""
    try:
        model = get_or_create_model()
        
        # Get training history
        training_history = ModelTraining.query.order_by(ModelTraining.training_date.desc()).all()
        
        # Get model summary
        model_summary = model.get_model_summary()
        
        # Get feature importance if model is trained
        feature_importance = None
        if model.is_trained:
            feature_importance = model.get_feature_importance()
        
        return render_template('admin/model_metrics.html', title='Model Metrics',
                             training_history=training_history,
                             model_summary=model_summary,
                             feature_importance=feature_importance)
    
    except Exception as e:
        logging.error(f"Error loading model metrics: {e}")
        flash('Error loading model metrics.', 'danger')
        return redirect(url_for('admin.dashboard'))
