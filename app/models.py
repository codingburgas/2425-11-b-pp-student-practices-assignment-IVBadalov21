from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Import db from extensions to avoid circular imports
from app.extensions import db

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_admin = db.Column(db.Boolean, default=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    surveys = db.relationship('Survey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'

class Survey(db.Model):
    """Model for storing survey data for training"""
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text_sample = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), nullable=False)  # en, es, fr, bg, de
    confidence = db.Column(db.Float, default=1.0)  # User confidence in language label
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)  # Admin can approve/reject
    
    def __repr__(self):
        return f'<Survey {self.id}: {self.language}>'

class Prediction(db.Model):
    """Model for storing prediction results"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    predicted_language = db.Column(db.String(5), nullable=False)
    confidence_scores = db.Column(db.Text)  # JSON string of all language scores
    accuracy_score = db.Column(db.Float)
    processing_time = db.Column(db.Float)  # Time taken for prediction in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)  # User consent for sharing
    actual_language = db.Column(db.String(5))  # If user provides feedback
    
    def set_confidence_scores(self, scores_dict):
        """Store confidence scores as JSON"""
        self.confidence_scores = json.dumps(scores_dict)
    
    def get_confidence_scores(self):
        """Retrieve confidence scores as dictionary"""
        if self.confidence_scores:
            return json.loads(self.confidence_scores)
        return {}
    
    def __repr__(self):
        return f'<Prediction {self.id}: {self.predicted_language}>'

class ModelTraining(db.Model):
    """Model for tracking training sessions and metrics"""
    __tablename__ = 'model_training'
    
    id = db.Column(db.Integer, primary_key=True)
    training_date = db.Column(db.DateTime, default=datetime.utcnow)
    samples_count = db.Column(db.Integer)  # Number of training samples
    accuracy = db.Column(db.Float)
    error_rate = db.Column(db.Float)
    loss = db.Column(db.Float)
    epochs = db.Column(db.Integer)
    learning_rate = db.Column(db.Float)
    feature_count = db.Column(db.Integer)
    training_time = db.Column(db.Float)  # Training time in seconds
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ModelTraining {self.id}: {self.accuracy:.3f} accuracy>'
