from flask import Flask
from app.models import db
from app.auth import login_manager
from app.main.routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'секретен_ключ'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main_bp)
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    return app