import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if 'SESSION_SECRET' not in os.environ:
    os.environ['SESSION_SECRET'] = 'language-detector-secret-key-2025'
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///language_detector.db'

os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

def main():
    print("Language Detector - Project #12")
    print("Custom Perceptron for 5-Language Detection")
    print("Languages: English, Spanish, French, Bulgarian, German")
    print("-" * 50)
    
    try:
        from app import create_app
        flask_app = create_app()
        
        print("Starting Flask development server...")
        print("Open your browser to: http://localhost:5000")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        flask_app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nPlease ensure all required packages are installed.")
        print("Check that the app module is properly structured.")
        print("\nRequired packages:")
        print("flask flask-login flask-wtf flask-mail flask-migrate flask-bootstrap wtforms werkzeug itsdangerous email-validator numpy python-dotenv")
        sys.exit(1)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()