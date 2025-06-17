import logging
from typing import Optional, Dict, Any
from app.models import Survey, ModelTraining
from app.extensions import db
from app.core.perceptron import MultiClassPerceptron
from flask import current_app

# Global model instance
_model_instance = None

def get_or_create_model() -> MultiClassPerceptron:
    """Get or create the global model instance"""
    global _model_instance
    
    if _model_instance is None:
        _model_instance = MultiClassPerceptron(
            languages=current_app.config['LANGUAGES'],
            learning_rate=0.01,
            max_epochs=1000,
            tolerance=1e-6
        )
        
        # Try to train with existing data
        try:
            train_model_with_surveys(model=_model_instance)
        except Exception as e:
            logging.warning(f"Could not train model on startup: {e}")
    
    return _model_instance

def train_model_with_surveys(model: Optional[MultiClassPerceptron] = None) -> Optional[Dict[str, Any]]:
    """Train the model with approved survey data"""
    if model is None:
        model = get_or_create_model()
    
    # Get approved survey data
    surveys = Survey.query.filter_by(is_approved=True).all()
    
    if len(surveys) < 10:  # Minimum training samples
        logging.warning(f"Not enough training data: {len(surveys)} samples")
        return None
    
    # Prepare training data
    texts = [survey.text_sample for survey in surveys]
    labels = [survey.language for survey in surveys]
    
    # Check if we have samples for all languages
    unique_labels = set(labels)
    required_languages = set(current_app.config['LANGUAGES'])
    
    if not required_languages.issubset(unique_labels):
        missing_langs = required_languages - unique_labels
        logging.warning(f"Missing training data for languages: {missing_langs}")
        return None
    
    try:
        # Train the model
        metrics = model.train(texts, labels)
        
        # Save training metrics to database
        save_model_training_metrics(metrics)
        
        logging.info(f"Model training completed: {metrics}")
        return metrics
        
    except Exception as e:
        logging.error(f"Model training failed: {e}")
        raise

def save_model_training_metrics(metrics: Dict[str, Any]):
    """Save training metrics to database"""
    try:
        training_record = ModelTraining(
            samples_count=metrics.get('samples_count'),
            accuracy=metrics.get('accuracy'),
            error_rate=metrics.get('error_rate'),
            loss=metrics.get('loss'),
            epochs=metrics.get('epochs_completed'),
            learning_rate=metrics.get('learning_rate'),
            feature_count=metrics.get('feature_count'),
            training_time=metrics.get('training_time'),
            notes=f"Automatic training with {metrics.get('samples_count')} samples"
        )
        
        db.session.add(training_record)
        db.session.commit()
        
        logging.info("Training metrics saved to database")
        
    except Exception as e:
        logging.error(f"Failed to save training metrics: {e}")
        db.session.rollback()

def reset_model():
    """Reset the global model instance (useful for testing)"""
    global _model_instance
    _model_instance = None

def get_language_statistics() -> Dict[str, Any]:
    """Get statistics about languages in the system"""
    from app.models import Survey, Prediction
    
    # Survey statistics
    survey_stats = db.session.query(Survey.language, db.func.count(Survey.id))\
                            .filter_by(is_approved=True)\
                            .group_by(Survey.language).all()
    
    # Prediction statistics
    prediction_stats = db.session.query(Prediction.predicted_language, db.func.count(Prediction.id))\
                                .group_by(Prediction.predicted_language).all()
    
    # Accuracy statistics (where feedback is available)
    accuracy_stats = db.session.query(
        Prediction.predicted_language,
        db.func.avg(Prediction.accuracy_score)
    ).filter(Prediction.accuracy_score.isnot(None))\
     .group_by(Prediction.predicted_language).all()
    
    return {
        'survey_distribution': {lang: count for lang, count in survey_stats},
        'prediction_distribution': {lang: count for lang, count in prediction_stats},
        'accuracy_by_language': {lang: acc for lang, acc in accuracy_stats}
    }

def validate_text_input(text: str) -> tuple[bool, str]:
    """Validate text input for prediction"""
    if not text or not text.strip():
        return False, "Text cannot be empty"
    
    if len(text.strip()) < 5:
        return False, "Text must be at least 5 characters long"
    
    if len(text) > 5000:
        return False, "Text must be less than 5000 characters"
    
    return True, ""

def format_confidence_scores(scores: Dict[str, float]) -> Dict[str, str]:
    """Format confidence scores for display"""
    formatted = {}
    for lang, score in scores.items():
        lang_name = current_app.config['LANGUAGE_NAMES'].get(lang, lang)
        formatted[lang_name] = f"{score * 100:.1f}%"
    
    return formatted
