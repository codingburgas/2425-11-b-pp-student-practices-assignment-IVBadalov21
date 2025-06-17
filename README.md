# Language Detector - Project #12

A Flask web application that uses a custom Perceptron algorithm to detect languages in text samples. Supports 5 languages: English, Spanish, French, Bulgarian, and German.

## Quick Start

### Option 1: Simple SQLite Setup (Recommended for testing)

1. **Extract the project** to a folder on your computer

2. **Install Python dependencies**:
```bash
pip install flask flask-sqlalchemy flask-login flask-wtf flask-mail flask-migrate flask-bootstrap wtforms psycopg2-binary gunicorn werkzeug itsdangerous email-validator numpy requests
```

3. **Set environment variable** (Windows):
```cmd
set SESSION_SECRET=language-detector-secret-key
set DATABASE_URL=sqlite:///language_detector.db
```

Or (Mac/Linux):
```bash
export SESSION_SECRET=language-detector-secret-key
export DATABASE_URL=sqlite:///language_detector.db
```

4. **Run the application**:
```bash
python run_local.py
```

5. **Open your browser** and go to: `http://localhost:5000`

### Option 2: PostgreSQL Setup (Production)

1. **Install PostgreSQL** and create a database named `language_detector`

2. **Set environment variables**:
```bash
export DATABASE_URL=postgresql://username:password@localhost/language_detector
export SESSION_SECRET=your-secret-key-here
```

3. **Run the application**:
```bash
python run_server.py
```

## Features

- **Language Detection**: Detect text in English, Spanish, French, Bulgarian, German
- **User Authentication**: Register and login system
- **Survey Collection**: Help train the model by submitting text samples 
- **Admin Dashboard**: Manage users and view model performance
- **API Endpoints**: Programmatic access to language detection

## Usage

1. Register a new account or login
2. Use the "Predict Language" page to test text samples
3. Submit training data via the "Survey" page
4. View your prediction history in "Results"

## Files Overview

- `wsgi.py` - Main Flask application
- `run_server.py` - Application runner
- `perceptron.py` - Custom Perceptron algorithm
- `language_features.py` - Feature extraction for text analysis
- `models.py` - Database models
- `auth/` - Authentication routes
- `main/` - Main application routes
- `admin/` - Admin panel routes
- `templates/` - HTML templates
- `static/` - CSS and JavaScript files

## Troubleshooting

If you get database errors, make sure:
1. PostgreSQL is running (if using PostgreSQL)
2. Database exists and credentials are correct
3. Environment variables are set properly

For SQLite (easier option), the database file will be created automatically.

## Database Schema

Here's a visual representation of the application's database schema, generated using Mermaid.io:

```mermaid
erDiagram
    users {
        int id PK
        string username
        string email
        string password_hash
        string first_name
        string last_name
        boolean is_admin
        boolean is_confirmed
        datetime confirmed_on
        datetime registered_on
        datetime last_seen
    }

    surveys {
        int id PK
        int user_id FK
        text text_sample
        string language
        float confidence
        datetime created_at
        boolean is_approved
    }

    predictions {
        int id PK
        int user_id FK
        text input_text
        string predicted_language
        text confidence_scores
        float accuracy_score
        float processing_time
        datetime created_at
        boolean is_public
        string actual_language
    }

    model_training {
        int id PK
        datetime training_date
        int samples_count
        float accuracy
        float error_rate
        float loss
        int epochs
        float learning_rate
        int feature_count
        float training_time
        text notes
    }

    users ||--o{ surveys : "has"
    users ||--o{ predictions : "makes"
```