#!/usr/bin/env python3
"""
Local development runner for Language Detector - Project #12
This file avoids all circular import issues.
"""
import os
import sys
from dotenv import load_dotenv
import app

# Load environment variables from .env file
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables if not already set
if 'SESSION_SECRET' not in os.environ:
    os.environ['SESSION_SECRET'] = 'language-detector-secret-key-2025'
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///language_detector.db'

# Configure Flask before any imports
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Email configuration will be loaded from .env file
# Make sure to create a .env file with the following variables:
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=true
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
# MAIL_DEFAULT_SENDER=your-email@gmail.com

def main():
    """Main function to run the Language Detector application."""
    print("Language Detector - Project #12")
    print("Custom Perceptron for 5-Language Detection")
    print("Languages: English, Spanish, French, Bulgarian, German")
    print("-" * 50)
    
    try:
        # Create the Flask application
        flask_app = app.create_app()
        
        # Configure the app for all hosts
        flask_app.config['SERVER_NAME'] = None  # Allow all hostnames
        
        print("Starting Flask development server...")
        print("Open your browser to: http://localhost:5000")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        # Run the Flask app
        flask_app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nPlease install required packages:")
        print("pip install flask flask-sqlalchemy flask-login flask-wtf flask-mail flask-migrate flask-bootstrap wtforms werkzeug itsdangerous email-validator numpy python-dotenv")
        sys.exit(1)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()