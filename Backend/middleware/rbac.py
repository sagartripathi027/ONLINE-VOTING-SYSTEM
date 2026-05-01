"""
RBAC Middleware — role-based access decorators
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.user import User


def roles_required(*roles):
    """
    Decorator: require JWT + one of the specified roles.
    Usage:
        @roles_required('admin')
        @roles_required('admin', 'voter')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user = User.query.get(identity)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            if not user.is_active:
                return jsonify({'error': 'Account suspended'}), 403

            if user.role not in roles:
                return jsonify({
                    'error': f"Access denied. Required role(s): {', '.join(roles)}"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Shorthand: admin only."""
    return roles_required('admin')(fn)


def voter_required(fn):
    """Shorthand: any authenticated active user."""
    return roles_required('admin', 'voter')(fn)