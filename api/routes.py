from flask import jsonify, request, current_app
from flask_login import login_required, current_user
import time
import logging

from api import bp
from app.models import Prediction, db
from app.extensions import db
from app.core.utils import get_or_create_model

@bp.route('/predict', methods=['POST'])
@login_required
def api_predict():
    """API endpoint for language prediction"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text input is required'}), 400
        
        input_text = data['text'].strip()
        if not input_text:
            return jsonify({'error': 'Text input cannot be empty'}), 400
        
        start_time = time.time()
        
        # Get model
        model = get_or_create_model()
        
        if not model.is_trained:
            return jsonify({'error': 'Model is not trained'}), 503
        
        # Make prediction
        predicted_language = model.predict(input_text)
        confidence_scores = model.predict_proba(input_text)
        processing_time = time.time() - start_time
        
        # Save prediction if requested
        save_prediction = data.get('save', True)
        prediction_id = None
        
        if save_prediction:
            prediction = Prediction(
                user_id=current_user.id,
                input_text=input_text,
                predicted_language=predicted_language,
                processing_time=processing_time,
                is_public=data.get('public', False)
            )
            prediction.set_confidence_scores(confidence_scores)
            
            db.session.add(prediction)
            db.session.commit()
            prediction_id = prediction.id
        
        response = {
            'predicted_language': predicted_language,
            'language_name': current_app.config['LANGUAGE_NAMES'][predicted_language],
            'confidence_scores': confidence_scores,
            'processing_time': processing_time,
            'prediction_id': prediction_id
        }
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"API prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/languages', methods=['GET'])
def api_languages():
    """API endpoint to get supported languages"""
    return jsonify({
        'languages': current_app.config['LANGUAGE_NAMES']
    })

@bp.route('/model/info', methods=['GET'])
def api_model_info():
    """API endpoint to get model information"""
    try:
        model = get_or_create_model()
        model_summary = model.get_model_summary()
        
        return jsonify(model_summary)
    
    except Exception as e:
        logging.error(f"API model info error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/stats', methods=['GET'])
def api_stats():
    """API endpoint to get system statistics"""
    from app.models import User, Survey, Prediction
    
    stats = {
        'total_users': User.query.count(),
        'total_surveys': Survey.query.count(),
        'total_predictions': Prediction.query.count(),
        'supported_languages': len(current_app.config['LANGUAGES'])
    }
    
    return jsonify(stats)
