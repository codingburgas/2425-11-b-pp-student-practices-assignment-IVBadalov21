from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required

from ..forms.forms import EditProfileForm
from ..models import User
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('auth.register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('predict.predict'))
        flash('Invalid credentials.')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.email.data:
            current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for('auth.profile'))
    return render_template('edit_profile.html', form=form)

@auth_bp.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('auth.profile'))

    from ..models import User
    users = User.query.all()
    return render_template('admin_users.html', users=users)
