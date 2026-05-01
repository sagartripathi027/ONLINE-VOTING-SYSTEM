"""
Admin Routes (admin role only)
GET  /api/admin/dashboard    – stats overview
GET  /api/admin/users        – list all users
GET  /api/admin/users/<id>   – user detail
PUT  /api/admin/users/<id>   – update user (role, active status)
DELETE /api/admin/users/<id> – soft-delete (deactivate)
"""
from flask import Blueprint, request, jsonify
from app import db
from models.user import User
from models.election import Election
from models.vote import Vote
from middleware.rbac import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    total_users     = User.query.count()
    total_voters    = User.query.filter_by(role='voter').count()
    total_elections = Election.query.count()
    active_elections= sum(1 for e in Election.query.all() if e.status == 'active')
    total_votes     = Vote.query.count()

    # Recent elections
    recent = Election.query.order_by(Election.created_at.desc()).limit(5).all()

    return jsonify({
        'stats': {
            'total_users':      total_users,
            'total_voters':     total_voters,
            'total_elections':  total_elections,
            'active_elections': active_elections,
            'total_votes':      total_votes,
        },
        'recent_elections': [e.to_dict() for e in recent],
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role     = request.args.get('role')

    query = User.query
    if role:
        query = query.filter_by(role=role)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'users':    [u.to_dict() for u in pagination.items],
        'total':    pagination.total,
        'pages':    pagination.pages,
        'page':     page,
        'per_page': per_page,
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    data = user.to_dict()
    data['votes_cast'] = user.votes.count()
    return jsonify({'user': data}), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    if 'role' in data:
        if data['role'] not in ('admin', 'voter'):
            return jsonify({'error': "Role must be 'admin' or 'voter'"}), 422
        user.role = data['role']

    if 'is_active' in data:
        user.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({'message': 'User updated', 'user': user.to_dict()}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({'error': 'Cannot deactivate admin accounts'}), 403
    user.is_active = False
    db.session.commit()
    return jsonify({'message': f'User {user.email} deactivated'}), 200