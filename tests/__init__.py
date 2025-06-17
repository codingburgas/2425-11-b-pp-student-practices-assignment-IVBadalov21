"""
Test package for Language Detector application.

This package contains unit tests for the Flask application,
including tests for models, authentication, and the custom
Perceptron algorithm.
"""

import os
import sys
import tempfile
import unittest
from flask import Flask

# Add the parent directory to the path so we can import our application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_test_app():
    """Create a Flask app configured for testing."""
    from app import create_app
    from app.extensions import db
    
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True,
        'LOGIN_DISABLED': False
    })
    
    with app.app_context():
        db.create_all()
    
    return app, db_fd, db_path

def destroy_test_app(db_fd, db_path):
    """Clean up test database."""
    os.close(db_fd)
    os.unlink(db_path)

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app, self.db_fd, self.db_path = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Import models after app context is established
        import app.models
        self.db = self.app.extensions.db
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()
        destroy_test_app(self.db_fd, self.db_path)
    
    def create_user(self, username='testuser', email='test@example.com', 
                   password='testpass123', is_confirmed=True, is_admin=False):
        """Helper method to create a test user."""
        from app.models import User
        
        user = User(
            username=username,
            email=email,
            is_confirmed=is_confirmed,
            is_admin=is_admin
        )
        user.set_password(password)
        
        self.db.session.add(user)
        self.db.session.commit()
        return user
    
    def login_user(self, username='testuser', password='testpass123'):
        """Helper method to log in a user."""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def logout_user(self):
        """Helper method to log out the current user."""
        return self.client.get('/auth/logout', follow_redirects=True)
    
    def create_survey(self, user, text_sample='Hello world', language='en', 
                     confidence=1.0, is_approved=True):
        """Helper method to create a test survey."""
        from app.models import Survey
        
        survey = Survey(
            user_id=user.id,
            text_sample=text_sample,
            language=language,
            confidence=confidence,
            is_approved=is_approved
        )
        
        self.db.session.add(survey)
        self.db.session.commit()
        return survey
    
    def create_prediction(self, user, input_text='Test text', 
                         predicted_language='en', is_public=False):
        """Helper method to create a test prediction."""
        from app.models import Prediction
        
        prediction = Prediction(
            user_id=user.id,
            input_text=input_text,
            predicted_language=predicted_language,
            processing_time=0.1,
            is_public=is_public
        )
        prediction.set_confidence_scores({
            'en': 0.8,
            'es': 0.1,
            'fr': 0.05,
            'bg': 0.03,
            'de': 0.02
        })
        
        self.db.session.add(prediction)
        self.db.session.commit()
        return prediction

def run_tests():
    """Run all tests in the tests package."""
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == '__main__':
    run_tests()
