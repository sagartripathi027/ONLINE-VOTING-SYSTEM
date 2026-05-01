"""
Auth Routes
POST /api/auth/signup
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
GET  /api/auth/profile
PUT  /api/auth/profile
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app import db
from models.user import User, TokenBlacklist
from middleware.rbac import voter_required

auth_bp = Blueprint('auth', __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_signup(data):
    errors = []
    if not data.get('full_name', '').strip():
        errors.append('Full name is required')
    email = data.get('email', '').strip().lower()
    if not email or '@' not in email:
        errors.append('Valid email is required')
    password = data.get('password', '')
    if len(password) < 8:
        errors.append('Password must be at least 8 characters')
    return errors, email


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    errors, email = _validate_signup(data)
    if errors:
        return jsonify({'errors': errors}), 422

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        full_name=data['full_name'].strip(),
        email=email,
        role='voter'            # public signup → voter only
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    access_token  = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Account created successfully',
        'user':    user.to_dict(),
        'access_token':  access_token,
        'refresh_token': refresh_token,
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data  = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 422

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account has been suspended'}), 403

    access_token  = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Login successful',
        'user':    user.to_dict(),
        'access_token':  access_token,
        'refresh_token': refresh_token,
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    token_type = get_jwt()['type']
    blacklisted = TokenBlacklist(jti=jti, token_type=token_type)
    db.session.add(blacklisted)
    db.session.commit()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    # Blacklist the old refresh token
    jti = get_jwt()['jti']
    blacklisted = TokenBlacklist(jti=jti, token_type='refresh')
    db.session.add(blacklisted)
    db.session.commit()

    new_access  = create_access_token(identity=identity)
    new_refresh = create_refresh_token(identity=identity)
    return jsonify({
        'access_token':  new_access,
        'refresh_token': new_refresh,
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@voter_required
def get_profile():
    user = User.query.get(get_jwt_identity())
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['PUT'])
@voter_required
def update_profile():
    user = User.query.get(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    if 'full_name' in data and data['full_name'].strip():
        user.full_name = data['full_name'].strip()

    if 'password' in data:
        if not data.get('current_password'):
            return jsonify({'error': 'Current password is required'}), 422
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        if len(data['password']) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 422
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200