from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_mail import Message
from datetime import datetime
import logging

from auth import bp
from app.forms.forms import LoginForm, RegistrationForm
from app.extensions import mail

def generate_confirmation_token(email):
    """Generate email confirmation token"""
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600):
    """Confirm email token"""
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
    except (SignatureExpired, BadTimeSignature):
        return False
    return email

def send_confirmation_email(user_email):
    """Send confirmation email to user"""
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    
    html = render_template('auth/confirm_email.html', confirm_url=confirm_url)
    subject = "Please confirm your email - Language Detector"
    
    msg = Message(
        subject,
        recipients=[user_email],
        html=html,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to send confirmation email: {e}")
        return False

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        from app.models import User, db
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_confirmed:
            flash('Please confirm your email address first.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Update last seen
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to next page or index
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        flash(f'Welcome back, {user.get_full_name()}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        from app.models import User, db
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Send confirmation email
        if send_confirmation_email(user.email):
            flash('A confirmation email has been sent to your email address.', 'info')
        else:
            flash('Registration successful, but confirmation email could not be sent. Please contact support.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/confirm/<token>')
def confirm_email(token):
    """Confirm email address"""
    if current_user.is_authenticated and current_user.is_confirmed:
        flash('Account already confirmed.', 'success')
        return redirect(url_for('main.index'))
    
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    from app.models import User, db
    user = User.query.filter_by(email=email).first_or_404()
    
    if user.is_confirmed:
        flash('Account already confirmed.', 'success')
    else:
        user.is_confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    
    return redirect(url_for('auth.login'))

@bp.route('/resend')
@login_required
def resend_confirmation():
    """Resend confirmation email"""
    if current_user.is_confirmed:
        flash('Your account is already confirmed.', 'info')
        return redirect(url_for('main.index'))
    
    if send_confirmation_email(current_user.email):
        flash('A new confirmation email has been sent.', 'success')
    else:
        flash('Error sending confirmation email. Please try again later.', 'danger')
    
    return redirect(url_for('main.index'))
