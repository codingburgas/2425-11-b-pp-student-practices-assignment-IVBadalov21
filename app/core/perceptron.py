import numpy as np
import time
import logging
from typing import List, Dict, Tuple, Any
from app.core.language_features import LanguageFeatureExtractor

class MultiClassPerceptron:
    """
    Custom Multi-class Perceptron implementation for language detection
    Uses one-vs-all approach for multi-class classification
    """
    
    def __init__(self, languages: List[str], learning_rate: float = 0.01, 
                 max_epochs: int = 1000, tolerance: float = 1e-6):
        """
        Initialize the Multi-class Perceptron
        
        Args:
            languages: List of language codes ['en', 'es', 'fr', 'bg', 'de']
            learning_rate: Learning rate for weight updates
            max_epochs: Maximum number of training epochs
            tolerance: Convergence tolerance
        """
        self.languages = languages
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.tolerance = tolerance
        self.feature_extractor = LanguageFeatureExtractor()
        
        # Initialize weights for each language (one-vs-all)
        self.weights = {}
        self.biases = {}
        self.feature_dim = None
        
        # Training metrics
        self.training_history = {
            'accuracy': [],
            'loss': [],
            'error_rate': []
        }
        
        self.is_trained = False
        
    def _initialize_weights(self, feature_dim: int):
        """Initialize weights and biases for all languages"""
        self.feature_dim = feature_dim
        
        for lang in self.languages:
            # Initialize weights with small random values
            self.weights[lang] = np.random.normal(0, 0.01, feature_dim)
            self.biases[lang] = 0.0
            
    def _sigmoid(self, z: float) -> float:
        """Sigmoid activation function with overflow protection"""
        z = np.clip(z, -500, 500)  # Prevent overflow
        return 1.0 / (1.0 + np.exp(-z))
    
    def _predict_single_class(self, features: np.ndarray, language: str) -> float:
        """Predict probability for a single language"""
        z = np.dot(features, self.weights[language]) + self.biases[language]
        return self._sigmoid(z)
    
    def predict_proba(self, text: str) -> Dict[str, float]:
        """
        Predict probabilities for all languages
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with language probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        features = self.feature_extractor.extract_features(text)
        
        probabilities = {}
        for lang in self.languages:
            probabilities[lang] = self._predict_single_class(features, lang)
        
        # Normalize probabilities to sum to 1
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            probabilities = {lang: prob/total_prob for lang, prob in probabilities.items()}
        
        return probabilities
    
    def predict(self, text: str) -> dict:
        """
        Predict the most likely language and return a dictionary with language and scores.
        Args:
            text: Input text to classify
        Returns:
            Dictionary with 'language' and 'scores' keys
        """
        probabilities = self.predict_proba(text)
        predicted_language = max(probabilities, key=probabilities.get)
        return {
            'language': predicted_language,
            'scores': probabilities
        }
    
    def _calculate_loss(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate cross-entropy loss"""
        total_loss = 0.0
        
        for i, features in enumerate(X):
            for lang in self.languages:
                target = 1.0 if y[i] == lang else 0.0
                pred = self._predict_single_class(features, lang)
                
                # Avoid log(0)
                pred = np.clip(pred, 1e-15, 1 - 1e-15)
                total_loss += -(target * np.log(pred) + (1 - target) * np.log(1 - pred))
                
        return total_loss / len(X)
    
    def _calculate_accuracy(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate prediction accuracy"""
        correct = 0
        
        for i, features in enumerate(X):
            # Get probabilities for all languages
            lang_probs = {}
            for lang in self.languages:
                lang_probs[lang] = self._predict_single_class(features, lang)
            
            # Predict the language with highest probability
            predicted = max(lang_probs, key=lang_probs.get)
            if predicted == y[i]:
                correct += 1
                
        return correct / len(X)
    
    def train(self, texts: List[str], labels: List[str]) -> Dict[str, Any]:
        """
        Train the perceptron using the provided data
        
        Args:
            texts: List of text samples
            labels: List of corresponding language labels
            
        Returns:
            Training metrics dictionary
        """
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must be equal")
        
        # Ensure all labels are valid
        invalid_labels = set(labels) - set(self.languages)
        if invalid_labels:
            raise ValueError(f"Invalid language labels: {invalid_labels}")
        
        logging.info(f"Starting training with {len(texts)} samples")
        start_time = time.time()
        
        # Extract features for all texts
        X = []
        for text in texts:
            features = self.feature_extractor.extract_features(text)
            X.append(features)
        
        X = np.array(X)
        y = np.array(labels)
        
        # Initialize weights
        if self.feature_dim is None:
            self._initialize_weights(X.shape[1])
        
        # Training loop
        prev_loss = float('inf')
        
        for epoch in range(self.max_epochs):
            # Shuffle data
            indices = np.random.permutation(len(X))
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            # Train each language classifier
            for i, (features, true_label) in enumerate(zip(X_shuffled, y_shuffled)):
                for lang in self.languages:
                    # Binary target: 1 if current language, 0 otherwise
                    target = 1.0 if true_label == lang else 0.0
                    
                    # Make prediction
                    prediction = self._predict_single_class(features, lang)
                    
                    # Calculate error
                    error = target - prediction
                    
                    # Update weights and bias
                    self.weights[lang] += self.learning_rate * error * features
                    self.biases[lang] += self.learning_rate * error
            
            # Calculate metrics every 10 epochs
            if epoch % 10 == 0:
                current_loss = self._calculate_loss(X, y)
                accuracy = self._calculate_accuracy(X, y)
                error_rate = 1.0 - accuracy
                
                self.training_history['loss'].append(current_loss)
                self.training_history['accuracy'].append(accuracy)
                self.training_history['error_rate'].append(error_rate)
                
                logging.debug(f"Epoch {epoch}: Loss={current_loss:.4f}, Accuracy={accuracy:.4f}")
                
                # Check for convergence
                if abs(prev_loss - current_loss) < self.tolerance:
                    logging.info(f"Converged at epoch {epoch}")
                    break
                    
                prev_loss = current_loss
        
        # Final metrics
        final_loss = self._calculate_loss(X, y)
        final_accuracy = self._calculate_accuracy(X, y)
        final_error_rate = 1.0 - final_accuracy
        training_time = time.time() - start_time
        
        self.is_trained = True
        
        training_metrics = {
            'accuracy': final_accuracy,
            'loss': final_loss,
            'error_rate': final_error_rate,
            'epochs_completed': epoch + 1,
            'training_time': training_time,
            'samples_count': len(texts),
            'feature_count': self.feature_dim,
            'learning_rate': self.learning_rate
        }
        
        logging.info(f"Training completed: Accuracy={final_accuracy:.4f}, Loss={final_loss:.4f}")
        return training_metrics
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Get feature importance for each language"""
        if not self.is_trained:
            raise ValueError("Model must be trained before getting feature importance")
            
        importance = {}
        feature_names = self.feature_extractor.get_feature_names()
        
        for lang in self.languages:
            # Use absolute weights as importance measure
            lang_importance = {}
            for i, feature_name in enumerate(feature_names):
                lang_importance[feature_name] = abs(self.weights[lang][i])
            
            # Sort by importance
            lang_importance = dict(sorted(lang_importance.items(), 
                                        key=lambda x: x[1], reverse=True))
            importance[lang] = lang_importance
            
        return importance
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary of the trained model"""
        if not self.is_trained:
            return {"status": "Not trained"}
            
        return {
            "status": "Trained",
            "languages": self.languages,
            "feature_dimension": self.feature_dim,
            "learning_rate": self.learning_rate,
            "training_history": self.training_history,
            "feature_extractor_info": self.feature_extractor.get_info()
        }
