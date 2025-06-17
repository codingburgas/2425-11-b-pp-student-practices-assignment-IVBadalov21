"""
Unit tests for database models.

Tests the User, Survey, Prediction, and ModelTraining models
to ensure correct functionality and relationships.
"""

import unittest
import json
from datetime import datetime
from tests import BaseTestCase
from app.models import User, Survey, Prediction, ModelTraining
from app.extensions import db
from app import create_app


class TestUserModel(BaseTestCase):
    """Test cases for the User model."""
    
    def test_create_user(self):
        """Test creating a new user."""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('password123')
        
        self.db.session.add(user)
        self.db.session.commit()
        
        # Verify user was created
        saved_user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.email, 'test@example.com')
        self.assertEqual(saved_user.first_name, 'Test')
        self.assertEqual(saved_user.last_name, 'User')
        self.assertFalse(saved_user.is_admin)
        self.assertFalse(saved_user.is_confirmed)
    
    def test_user_password_methods(self):
        """Test password setting and checking."""
        user = User(username='test', email='test@example.com')
        
        # Set password
        user.set_password('mypassword')
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, 'mypassword')
        
        # Check password
        self.assertTrue(user.check_password('mypassword'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_user_full_name(self):
        """Test full name functionality."""
        # User with both names
        user = User(
            username='john_doe',
            email='john@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.get_full_name(), 'John Doe')
        
        # User with only first name
        user.last_name = None
        self.assertEqual(user.get_full_name(), 'john_doe')
        
        # User with no names
        user.first_name = None
        self.assertEqual(user.get_full_name(), 'john_doe')
    
    def test_user_relationships(self):
        """Test user relationships with surveys and predictions."""
        user = self.create_user()
        
        # Create surveys
        survey1 = Survey(
            user_id=user.id,
            text_sample='Hello world',
            language='en',
            confidence=1.0
        )
        survey2 = Survey(
            user_id=user.id,
            text_sample='Hola mundo',
            language='es',
            confidence=0.9
        )
        
        self.db.session.add_all([survey1, survey2])
        self.db.session.commit()
        
        # Test relationship
        self.assertEqual(user.surveys.count(), 2)
        self.assertIn(survey1, user.surveys.all())
        self.assertIn(survey2, user.surveys.all())
    
    def test_user_admin_functionality(self):
        """Test admin user functionality."""
        admin_user = self.create_user(username='admin', is_admin=True)
        regular_user = self.create_user(username='regular', is_admin=False)
        
        self.assertTrue(admin_user.is_admin)
        self.assertFalse(regular_user.is_admin)
    
    def test_user_confirmation_functionality(self):
        """Test email confirmation functionality."""
        user = self.create_user(is_confirmed=False)
        
        # Initially unconfirmed
        self.assertFalse(user.is_confirmed)
        self.assertIsNone(user.confirmed_on)
        
        # Confirm user
        user.is_confirmed = True
        user.confirmed_on = datetime.utcnow()
        self.db.session.commit()
        
        self.assertTrue(user.is_confirmed)
        self.assertIsNotNone(user.confirmed_on)


class TestSurveyModel(BaseTestCase):
    """Test cases for the Survey model."""
    
    def test_create_survey(self):
        """Test creating a new survey."""
        user = self.create_user()
        
        survey = Survey(
            user_id=user.id,
            text_sample='This is a test sample in English.',
            language='en',
            confidence=0.95
        )
        
        self.db.session.add(survey)
        self.db.session.commit()
        
        # Verify survey was created
        saved_survey = Survey.query.first()
        self.assertIsNotNone(saved_survey)
        self.assertEqual(saved_survey.user_id, user.id)
        self.assertEqual(saved_survey.text_sample, 'This is a test sample in English.')
        self.assertEqual(saved_survey.language, 'en')
        self.assertEqual(saved_survey.confidence, 0.95)
        self.assertTrue(saved_survey.is_approved)  # Default value
    
    def test_survey_user_relationship(self):
        """Test survey-user relationship."""
        user = self.create_user()
        survey = self.create_survey(user, text_sample='Test text', language='en')
        
        # Test relationship
        self.assertEqual(survey.user, user)
        self.assertEqual(survey.user.username, 'testuser')
    
    def test_survey_languages(self):
        """Test surveys with different languages."""
        user = self.create_user()
        
        languages = ['en', 'es', 'fr', 'bg', 'de']
        samples = [
            'Hello world',
            'Hola mundo',
            'Bonjour monde',
            'Здравей свят',
            'Hallo Welt'
        ]
        
        for lang, sample in zip(languages, samples):
            survey = self.create_survey(user, text_sample=sample, language=lang)
            self.assertEqual(survey.language, lang)
            self.assertEqual(survey.text_sample, sample)
    
    def test_survey_approval_status(self):
        """Test survey approval status."""
        user = self.create_user()
        
        # Approved survey (default)
        approved_survey = self.create_survey(user, is_approved=True)
        self.assertTrue(approved_survey.is_approved)
        
        # Pending survey
        pending_survey = self.create_survey(user, is_approved=False)
        self.assertFalse(pending_survey.is_approved)
    
    def test_survey_confidence_levels(self):
        """Test different confidence levels."""
        user = self.create_user()
        
        confidence_levels = [0.5, 0.7, 0.9, 1.0]
        
        for confidence in confidence_levels:
            survey = self.create_survey(user, confidence=confidence)
            self.assertEqual(survey.confidence, confidence)
    
    def test_survey_string_representation(self):
        """Test survey string representation."""
        user = self.create_user()
        survey = self.create_survey(user, language='en')
        
        expected = f'<Survey {survey.id}: en>'
        self.assertEqual(str(survey), expected)


class TestPredictionModel(BaseTestCase):
    """Test cases for the Prediction model."""
    
    def test_create_prediction(self):
        """Test creating a new prediction."""
        user = self.create_user()
        
        prediction = Prediction(
            user_id=user.id,
            input_text='Hello, how are you?',
            predicted_language='en',
            processing_time=0.15,
            is_public=True
        )
        
        # Set confidence scores
        scores = {'en': 0.8, 'es': 0.1, 'fr': 0.05, 'bg': 0.03, 'de': 0.02}
        prediction.set_confidence_scores(scores)
        
        self.db.session.add(prediction)
        self.db.session.commit()
        
        # Verify prediction was created
        saved_prediction = Prediction.query.first()
        self.assertIsNotNone(saved_prediction)
        self.assertEqual(saved_prediction.user_id, user.id)
        self.assertEqual(saved_prediction.input_text, 'Hello, how are you?')
        self.assertEqual(saved_prediction.predicted_language, 'en')
        self.assertEqual(saved_prediction.processing_time, 0.15)
        self.assertTrue(saved_prediction.is_public)
    
    def test_prediction_confidence_scores(self):
        """Test confidence scores functionality."""
        user = self.create_user()
        prediction = self.create_prediction(user)
        
        # Test confidence scores
        scores = {'en': 0.7, 'es': 0.15, 'fr': 0.1, 'bg': 0.03, 'de': 0.02}
        prediction.set_confidence_scores(scores)
        self.db.session.commit()
        
        # Retrieve and verify
        self.assertEqual(prediction.get_confidence_scores(), scores)
    
    def test_prediction_user_relationship(self):
        """Test prediction-user relationship."""
        user = self.create_user()
        prediction = self.create_prediction(user, input_text='Test text')
        
        # Test relationship
        self.assertEqual(prediction.user, user)
        self.assertEqual(prediction.user.username, 'testuser')
    
    def test_prediction_feedback(self):
        """Test prediction feedback functionality."""
        user = self.create_user()
        prediction = self.create_prediction(user, predicted_language='en')
        
        # Initially no actual language or accuracy score
        self.assertIsNone(prediction.actual_language)
        self.assertIsNone(prediction.accuracy_score)
        
        # Provide feedback - correct
        prediction.actual_language = 'en'
        prediction.accuracy_score = 1.0 if prediction.predicted_language == 'en' else 0.0
        self.db.session.commit()
        
        self.assertEqual(prediction.actual_language, 'en')
        self.assertEqual(prediction.accuracy_score, 1.0)
        
        # Provide feedback - incorrect
        prediction.actual_language = 'es'
        prediction.accuracy_score = 1.0 if prediction.predicted_language == 'es' else 0.0
        self.db.session.commit()
        
        self.assertEqual(prediction.actual_language, 'es')
        self.assertEqual(prediction.accuracy_score, 0.0)

    def test_prediction_public_status(self):
        """Test prediction public status."""
        user = self.create_user()
        
        # Public prediction
        public_prediction = self.create_prediction(user, is_public=True)
        self.assertTrue(public_prediction.is_public)
        
        # Private prediction
        private_prediction = self.create_prediction(user, is_public=False)
        self.assertFalse(private_prediction.is_public)

    def test_prediction_multiple_languages(self):
        """Test predictions with different languages."""
        user = self.create_user()
        
        languages = ['en', 'es', 'fr', 'bg', 'de']
        samples = [
            'Hello, how are you?',
            '¿Cómo estás?',
            'Comment allez-vous?',
            'Как си?',
            'Wie geht es Ihnen?'
        ]
        
        for lang, sample in zip(languages, samples):
            prediction = self.create_prediction(user, input_text=sample, predicted_language=lang)
            self.assertEqual(prediction.predicted_language, lang)
            self.assertEqual(prediction.input_text, sample)

    def test_prediction_string_representation(self):
        """Test prediction string representation."""
        user = self.create_user()
        prediction = self.create_prediction(user, predicted_language='en')
        
        expected = f'<Prediction {prediction.id}: en>'
        self.assertEqual(str(prediction), expected)


class TestModelTrainingModel(BaseTestCase):
    """Test cases for the ModelTraining model."""
    
    def test_create_model_training(self):
        """Test creating a new model training record."""
        training = ModelTraining(
            samples_count=1000,
            accuracy=0.92,
            error_rate=0.08,
            loss=0.15,
            epochs=50,
            learning_rate=0.01,
            feature_count=150,
            training_time=300.5,
            notes='Initial training run'
        )
        
        self.db.session.add(training)
        self.db.session.commit()
        
        # Verify training record was created
        saved_training = ModelTraining.query.first()
        self.assertIsNotNone(saved_training)
        self.assertEqual(saved_training.samples_count, 1000)
        self.assertEqual(saved_training.accuracy, 0.92)
        self.assertEqual(saved_training.loss, 0.15)
        self.assertEqual(saved_training.epochs, 50)
        self.assertEqual(saved_training.training_time, 300.5)
        self.assertEqual(saved_training.notes, 'Initial training run')
    
    def test_model_training_metrics(self):
        """Test various training metrics."""
        training = ModelTraining(
            samples_count=500,
            accuracy=0.85,
            error_rate=0.15,
            loss=0.25,
            epochs=20,
            learning_rate=0.005,
            feature_count=120,
            training_time=120.0,
            notes='Another training run'
        )
        self.db.session.add(training)
        self.db.session.commit()
        
        retrieved_training = ModelTraining.query.first()
        self.assertEqual(retrieved_training.samples_count, 500)
        self.assertEqual(retrieved_training.accuracy, 0.85)
        self.assertEqual(retrieved_training.error_rate, 0.15)
        self.assertEqual(retrieved_training.loss, 0.25)
        self.assertEqual(retrieved_training.epochs, 20)
        self.assertEqual(retrieved_training.learning_rate, 0.005)
        self.assertEqual(retrieved_training.feature_count, 120)
        self.assertEqual(retrieved_training.training_time, 120.0)

    def test_model_training_timestamps(self):
        """Test model training timestamps."""
        training = ModelTraining(samples_count=100, accuracy=0.9)
        self.db.session.add(training)
        self.db.session.commit()
        
        # Ensure training_date is set automatically
        self.assertIsNotNone(training.training_date)
        self.assertIsInstance(training.training_date, datetime)
        
        # Test ordering by training_date
        training2 = ModelTraining(samples_count=200, accuracy=0.95)
        self.db.session.add(training2)
        self.db.session.commit()
        
        latest_training = ModelTraining.query.order_by(ModelTraining.training_date.desc()).first()
        self.assertEqual(latest_training.accuracy, 0.95)

    def test_model_training_string_representation(self):
        """Test model training string representation."""
        training = ModelTraining(samples_count=1000, accuracy=0.925)
        self.db.session.add(training)
        self.db.session.commit()
        
        expected = f'<ModelTraining {training.id}: 0.925 accuracy>'
        self.assertEqual(str(training), expected)


class TestModelRelationships(BaseTestCase):
    """Test cases for model relationships."""

    def test_user_deletion_cascade(self):
        """Test cascade delete for user, surveys, and predictions."""
        user = self.create_user()
        survey1 = self.create_survey(user)
        prediction1 = self.create_prediction(user)
        
        self.db.session.add_all([survey1, prediction1])
        self.db.session.commit()
        
        # Assert surveys and predictions exist
        self.assertEqual(Survey.query.count(), 1)
        self.assertEqual(Prediction.query.count(), 1)
        
        # Delete user
        self.db.session.delete(user)
        self.db.session.commit()
        
        # Assert surveys and predictions are deleted due to cascade
        self.assertEqual(User.query.count(), 0)
        self.assertEqual(Survey.query.count(), 0)
        self.assertEqual(Prediction.query.count(), 0)
    
    def test_unique_constraints(self):
        """Test unique constraints on User model."""
        self.create_user(username='uniqueuser', email='unique@example.com')
        
        # Test duplicate username
        with self.assertRaises(Exception): # Assuming SQLAlchemy raises some exception
            duplicate_user = User(username='uniqueuser', email='another@example.com')
            duplicate_user.set_password('pass')
            self.db.session.add(duplicate_user)
            self.db.session.commit()
            
        self.db.session.rollback()
        
        # Test duplicate email
        with self.assertRaises(Exception): # Assuming SQLAlchemy raises some exception
            duplicate_user = User(username='anotheruser', email='unique@example.com')
            duplicate_user.set_password('pass')
            self.db.session.add(duplicate_user)
            self.db.session.commit()
            
        self.db.session.rollback()

    def test_foreign_key_constraints(self):
        """Test foreign key constraint for Survey and Prediction models."""
        # Attempt to create a survey with non-existent user_id
        with self.assertRaises(Exception): # Assuming SQLAlchemy raises some exception
            survey = Survey(user_id=999, text_sample='test', language='en')
            self.db.session.add(survey)
            self.db.session.commit()
        self.db.session.rollback()
        
        # Attempt to create a prediction with non-existent user_id
        with self.assertRaises(Exception): # Assuming SQLAlchemy raises some exception
            prediction = Prediction(user_id=999, input_text='test', predicted_language='en')
            prediction.set_confidence_scores({})
            self.db.session.add(prediction)
            self.db.session.commit()
        self.db.session.rollback()
    
    def test_model_queries(self):
        """Test basic model queries."""
        user1 = self.create_user(username='user1', email='user1@example.com')
        user2 = self.create_user(username='user2', email='user2@example.com')
        
        survey1 = self.create_survey(user1, language='en')
        survey2 = self.create_survey(user1, language='es')
        survey3 = self.create_survey(user2, language='fr')
        
        # Test all users
        all_users = User.query.all()
        self.assertEqual(len(all_users), 2)
        
        # Test user surveys
        self.assertEqual(user1.surveys.count(), 2)
        self.assertEqual(user2.surveys.count(), 1)
        
        # Test total surveys
        self.assertEqual(Survey.query.count(), 3)


if __name__ == '__main__':
    unittest.main()
