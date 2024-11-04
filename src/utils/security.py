from functools import wraps
from flask import request, current_app
from src.exceptions import APIError

def require_api_key(f):
    """Decorator to require API key for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key not in current_app.config['API_KEYS']:
            raise APIError('Invalid API key', 401)
        return f(*args, **kwargs)
    return decorated_function