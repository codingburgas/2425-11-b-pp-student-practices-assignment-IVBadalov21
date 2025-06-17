from flask import Blueprint

bp = Blueprint('auth', __name__)

# Import routes at the end to avoid circular imports
from app.auth import routes 