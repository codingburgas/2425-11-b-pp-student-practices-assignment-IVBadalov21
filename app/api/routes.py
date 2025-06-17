from flask import jsonify, request
from app.api import bp

@bp.route('/detect', methods=['POST'])
def detect_language():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text parameter'}), 400
    
    text = data['text']
    # Here you would integrate your language detection logic
    # For now, let's return a placeholder
    detected_language = "English" # Replace with actual detection
    
    return jsonify({'language': detected_language}) 