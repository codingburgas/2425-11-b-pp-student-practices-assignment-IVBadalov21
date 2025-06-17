import os
import logging
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import extensions from separate module to avoid circular imports
from app.extensions import db, login_manager, mail, migrate, bootstrap, csrf

def create_app():
    """Application factory pattern"""
    # Determine the root directory of the application
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

    # Initialize Flask app, explicitly setting template_folder and static_folder
    flask_instance = Flask(
        __name__,
        template_folder=os.path.join(project_root, 'templates'),
        static_folder=os.path.join(project_root, 'static')
    )
    
    # Configuration
    flask_instance.config.from_object('app.config.Config')
    flask_instance.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    flask_instance.wsgi_app = ProxyFix(flask_instance.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions with flask_instance
    db.init_app(flask_instance)
    login_manager.init_app(flask_instance)
    mail.init_app(flask_instance)
    migrate.init_app(flask_instance, db)
    bootstrap.init_app(flask_instance)
    csrf.init_app(flask_instance)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth import bp as auth_bp
    flask_instance.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    flask_instance.register_blueprint(main_bp)
    
    from app.admin import bp as admin_bp
    flask_instance.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.api import bp as api_bp
    flask_instance.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    @flask_instance.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @flask_instance.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Create database tables
    with flask_instance.app_context():
        # Import models to ensure tables are created
        import app.models
        db.create_all()
    
    print(f"DEBUG: Inside create_app, returning type: {type(flask_instance)}")
    return flask_instance

# App instance will be created in main.py
