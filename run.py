from flask import render_template
from app import create_app, db
from app.models import User, Prediction

app = create_app()

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Prediction': Prediction
    }

if __name__ == '__main__':
    app.run(debug=True)
