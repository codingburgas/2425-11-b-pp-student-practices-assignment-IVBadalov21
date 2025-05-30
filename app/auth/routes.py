from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import RegistrationForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Тук по-късно ще запазим потребителя в базата и ще изпратим имейл
        flash('Регистрацията мина успешно! Очаквай имейл за потвърждение.', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)
