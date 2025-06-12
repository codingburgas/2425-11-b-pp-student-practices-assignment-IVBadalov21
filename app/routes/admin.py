from flask import Blueprint, render_template, redirect, url_for, flash
from app.models import User
from app import db
from app.decorators import admin_required
from flask_login import login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("Cannot delete another admin.")
        return redirect(url_for('admin.list_users'))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.")
    return redirect(url_for('admin.list_users'))

