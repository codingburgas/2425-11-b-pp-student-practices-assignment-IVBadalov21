"""
Unit tests for the custom Perceptron algorithm implementation.

Tests the MultiClassPerceptron and LanguageFeatureExtractor classes
to ensure correct functionality for language detection.
"""

import unittest
import numpy as np
from tests import BaseTestCase
from app.core.perceptron import MultiClassPerceptron
from app.core.language_features import LanguageFeatureExtractor


class TestLanguageFeatureExtractor(BaseTestCase):
    """Test cases for the LanguageFeatureExtractor class."""
    
    def setUp(self):
        super().setUp()
        self.extractor = LanguageFeatureExtractor()
    
    def test_feature_extractor_initialization(self):
        """Test that the feature extractor initializes correctly."""
        self.assertIsInstance(self.extractor.feature_names, list)
        self.assertGreater(len(self.extractor.feature_names), 0)
        self.assertIn('en', self.extractor.language_chars)
        self.assertIn('bg', self.extractor.language_chars)
    
    def test_extract_features_english(self):
        """Test feature extraction for English text."""
        text = "Hello, how are you today?"
        features = self.extractor.extract_features(text)
        
        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(len(features), len(self.extractor.feature_names))
        self.assertTrue(np.isfinite(features).all())
    
    def test_extract_features_bulgarian(self):
        """Test feature extraction for Bulgarian (Cyrillic) text."""
        text = "Здравей, как си днес?"
        features = self.extractor.extract_features(text)
        
        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(len(features), len(self.extractor.feature_names))
        self.assertTrue(np.isfinite(features).all())
        
        # Check that Cyrillic ratio is detected
        cyrillic_ratio_idx = self.extractor.feature_names.index('cyrillic_ratio')
        self.assertGreater(features[cyrillic_ratio_idx], 0)
    
    def test_extract_features_empty_text(self):
        """Test feature extraction for empty text."""
        features = self.extractor.extract_features("")
        
        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(len(features), len(self.extractor.feature_names))
        self.assertTrue(np.all(features == 0))
    
    def test_extract_features_unicode_support(self):
        """Test that Unicode characters are handled correctly."""
        texts = [
            "Café français",  # French with accents
            "Niño español",   # Spanish with ñ
            "Größe deutsch",  # German with umlaut
            "Здраве българско"  # Bulgarian Cyrillic
        ]
        
        for text in texts:
            features = self.extractor.extract_features(text)
            self.assertIsInstance(features, np.ndarray)
            self.assertTrue(np.isfinite(features).all())
    
    def test_get_feature_names(self):
        """Test that feature names are returned correctly."""
        feature_names = self.extractor.get_feature_names()
        
        self.assertIsInstance(feature_names, list)
        self.assertGreater(len(feature_names), 0)
        self.assertEqual(len(feature_names), len(self.extractor.feature_names))
    
    def test_get_info(self):
        """Test that extractor info is returned correctly."""
        info = self.extractor.get_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('feature_count', info)
        self.assertIn('supported_languages', info)
        self.assertIn('unicode_support', info)
        self.assertIn('cyrillic_support', info)
        self.assertTrue(info['unicode_support'])
        self.assertTrue(info['cyrillic_support'])


class TestMultiClassPerceptron(BaseTestCase):
    """Test cases for the MultiClassPerceptron class."""
    
    def setUp(self):
        super().setUp()
        self.languages = ['en', 'es', 'fr']
        self.perceptron = MultiClassPerceptron(
            languages=self.languages,
            learning_rate=0.1,
            max_epochs=10,
            tolerance=1e-3
        )
    
    def test_perceptron_initialization(self):
        """Test that the perceptron initializes correctly."""
        self.assertEqual(self.perceptron.languages, self.languages)
        self.assertEqual(self.perceptron.learning_rate, 0.1)
        self.assertEqual(self.perceptron.max_epochs, 10)
        self.assertFalse(self.perceptron.is_trained)
        self.assertIsInstance(self.perceptron.feature_extractor, LanguageFeatureExtractor)
    
    def test_sigmoid_function(self):
        """Test the sigmoid activation function."""
        # Test normal values
        self.assertAlmostEqual(self.perceptron._sigmoid(0), 0.5, places=5)
        self.assertGreater(self.perceptron._sigmoid(10), 0.5)
        self.assertLess(self.perceptron._sigmoid(-10), 0.5)
        
        # Test overflow protection
        self.assertTrue(0 <= self.perceptron._sigmoid(1000) <= 1)
        self.assertTrue(0 <= self.perceptron._sigmoid(-1000) <= 1)
    
    def test_train_with_minimal_data(self):
        """Test training with minimal valid dataset."""
        texts = [
            "Hello, how are you?",  # English
            "Hola, ¿cómo estás?",   # Spanish
            "Bonjour, comment allez-vous?",  # French
            "Good morning everyone",  # English
            "Buenos días a todos",    # Spanish
            "Bonjour tout le monde"   # French
        ]
        labels = ['en', 'es', 'fr', 'en', 'es', 'fr']
        
        metrics = self.perceptron.train(texts, labels)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('accuracy', metrics)
        self.assertIn('loss', metrics)
        self.assertIn('error_rate', metrics)
        self.assertTrue(self.perceptron.is_trained)
        self.assertGreater(metrics['accuracy'], 0)
    
    def test_train_invalid_data(self):
        """Test training with invalid data raises appropriate errors."""
        # Mismatched lengths
        with self.assertRaises(ValueError):
            self.perceptron.train(['text1', 'text2'], ['en'])
        
        # Invalid language labels
        with self.assertRaises(ValueError):
            self.perceptron.train(['text1'], ['invalid_lang'])
    
    def test_predict_before_training(self):
        """Test that prediction before training raises an error."""
        with self.assertRaises(ValueError):
            self.perceptron.predict("Hello world")
        
        with self.assertRaises(ValueError):
            self.perceptron.predict_proba("Hello world")
    
    def test_predict_after_training(self):
        """Test prediction functionality after training."""
        # Train with minimal data
        texts = [
            "Hello world", "Good morning", "How are you?",  # English
            "Hola mundo", "Buenos días", "¿Cómo estás?",   # Spanish
            "Bonjour monde", "Bonjour", "Comment allez-vous?"  # French
        ]
        labels = ['en', 'en', 'en', 'es', 'es', 'es', 'fr', 'fr', 'fr']
        
        self.perceptron.train(texts, labels)
        
        # Test prediction
        prediction = self.perceptron.predict("Hello, good morning!")
        self.assertIn(prediction, self.languages)
        
        # Test probability prediction
        probabilities = self.perceptron.predict_proba("Hello, good morning!")
        self.assertIsInstance(probabilities, dict)
        self.assertEqual(set(probabilities.keys()), set(self.languages))
        
        # Probabilities should sum to approximately 1
        total_prob = sum(probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=3)
        
        # All probabilities should be between 0 and 1
        for prob in probabilities.values():
            self.assertGreaterEqual(prob, 0)
            self.assertLessEqual(prob, 1)
    
    def test_get_model_summary(self):
        """Test model summary functionality."""
        # Before training
        summary = self.perceptron.get_model_summary()
        self.assertEqual(summary['status'], 'Not trained')
        
        # After training
        texts = ['Hello', 'Hola', 'Bonjour'] * 3
        labels = ['en', 'es', 'fr'] * 3
        self.perceptron.train(texts, labels)
        
        summary = self.perceptron.get_model_summary()
        self.assertEqual(summary['status'], 'Trained')
        self.assertIn('languages', summary)
        self.assertIn('feature_dimension', summary)
        self.assertIn('learning_rate', summary)
    
    def test_feature_importance(self):
        """Test feature importance calculation."""
        # Train the model first
        texts = ['Hello world', 'Hola mundo', 'Bonjour monde'] * 5
        labels = ['en', 'es', 'fr'] * 5
        self.perceptron.train(texts, labels)
        
        importance = self.perceptron.get_feature_importance()
        
        self.assertIsInstance(importance, dict)
        self.assertEqual(set(importance.keys()), set(self.languages))
        
        for lang_importance in importance.values():
            self.assertIsInstance(lang_importance, dict)
            self.assertGreater(len(lang_importance), 0)
            
            # Check that importance values are non-negative
            for imp_value in lang_importance.values():
                self.assertGreaterEqual(imp_value, 0)
    
    def test_convergence(self):
        """Test that the algorithm can converge with sufficient data."""
        # Create more training data for better convergence
        english_texts = [
            "Hello how are you today",
            "Good morning everyone",
            "Thank you very much",
            "See you later",
            "Have a nice day"
        ]
        spanish_texts = [
            "Hola como estas hoy",
            "Buenos días a todos",
            "Muchas gracias",
            "Hasta luego",
            "Que tengas un buen día"
        ]
        french_texts = [
            "Bonjour comment allez vous",
            "Bonjour tout le monde",
            "Merci beaucoup",
            "À bientôt",
            "Bonne journée"
        ]
        
        texts = english_texts + spanish_texts + french_texts
        labels = ['en'] * len(english_texts) + ['es'] * len(spanish_texts) + ['fr'] * len(french_texts)
        
        # Use more epochs for this test
        self.perceptron.max_epochs = 100
        metrics = self.perceptron.train(texts, labels)
        
        # Should achieve reasonable accuracy
        self.assertGreater(metrics['accuracy'], 0.5)
        self.assertLess(metrics['error_rate'], 0.5)
    
    def test_training_history(self):
        """Test that training history is recorded correctly."""
        texts = ['Hello', 'Hola', 'Bonjour'] * 4
        labels = ['en', 'es', 'fr'] * 4
        
        self.perceptron.train(texts, labels)
        
        history = self.perceptron.training_history
        self.assertIn('accuracy', history)
        self.assertIn('loss', history)
        self.assertIn('error_rate', history)
        
        # Should have some recorded values
        self.assertGreater(len(history['accuracy']), 0)
        self.assertGreater(len(history['loss']), 0)
        self.assertGreater(len(history['error_rate']), 0)


class TestPerceptronIntegration(BaseTestCase):
    """Integration tests for the complete perceptron system."""
    
    def test_multilingual_detection(self):
        """Test detection across all supported languages."""
        languages = ['en', 'es', 'fr', 'bg', 'de']
        perceptron = MultiClassPerceptron(languages=languages, max_epochs=50)
        
        # Prepare multilingual training data
        training_data = {
            'en': ["Hello how are you", "Good morning", "Thank you"],
            'es': ["Hola como estas", "Buenos días", "Gracias"],
            'fr': ["Bonjour comment allez", "Bonjour", "Merci"],
            'bg': ["Здравей как си", "Добро утро", "Благодаря"],
            'de': ["Hallo wie geht es", "Guten Morgen", "Danke"]
        }
        
        texts = []
        labels = []
        for lang, lang_texts in training_data.items():
            texts.extend(lang_texts)
            labels.extend([lang] * len(lang_texts))
        
        # Train the model
        metrics = perceptron.train(texts, labels)
        self.assertTrue(perceptron.is_trained)
        
        # Test predictions for each language
        test_texts = {
            'en': "Hello world",
            'es': "Hola mundo",
            'fr': "Bonjour monde",
            'bg': "Здравей свят",
            'de': "Hallo Welt"
        }
        
        for expected_lang, test_text in test_texts.items():
            prediction = perceptron.predict(test_text)
            # Note: With limited training data, perfect accuracy isn't expected
            # but the prediction should be one of the valid languages
            self.assertIn(prediction, languages)
            
            probabilities = perceptron.predict_proba(test_text)
            self.assertEqual(len(probabilities), len(languages))
    
    def test_cyrillic_script_support(self):
        """Test specific support for Bulgarian Cyrillic script."""
        languages = ['en', 'bg']
        perceptron = MultiClassPerceptron(languages=languages, max_epochs=30)
        
        # Bulgarian and English training texts
        texts = [
            "Hello how are you today",
            "Good morning everyone",
            "Thank you very much",
            "Здравей как си днес",
            "Добро утро на всички",
            "Благодаря ти много"
        ]
        labels = ['en', 'en', 'en', 'bg', 'bg', 'bg']
        
        metrics = perceptron.train(texts, labels)
        
        # Test Bulgarian text detection
        bulgarian_text = "Как си днес"
        prediction = perceptron.predict(bulgarian_text)
        probabilities = perceptron.predict_proba(bulgarian_text)
        
        # Should recognize as one of the trained languages
        self.assertIn(prediction, ['en', 'bg'])
        self.assertEqual(len(probabilities), 2)
        
        # Feature extractor should detect Cyrillic characters
        features = perceptron.feature_extractor.extract_features(bulgarian_text)
        cyrillic_ratio_idx = perceptron.feature_extractor.feature_names.index('cyrillic_ratio')
        self.assertGreater(features[cyrillic_ratio_idx], 0)


if __name__ == '__main__':
    unittest.main()
