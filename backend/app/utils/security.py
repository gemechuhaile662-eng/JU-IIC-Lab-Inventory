# =========================================================
# app/utils/security.py
# Session-based authentication helpers
# =========================================================

from functools import wraps
from flask import session, jsonify, g

from app.models import User


def current_user():
    """Return the currently logged-in User, or None."""
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


def login_required(f):
    """Decorator: require a logged-in user."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user.status != 'active':
            return jsonify({'error': 'authentication required'}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Decorator: require a specific role (in addition to login)."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user or user.status != 'active':
                return jsonify({'error': 'authentication required'}), 401
            if user.role not in allowed_roles:
                return jsonify({'error': 'forbidden', 'your_role': user.role}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator