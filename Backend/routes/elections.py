"""
Elections Routes
GET    /api/elections/              – list all (public)
POST   /api/elections/              – create (admin)
GET    /api/elections/<id>          – detail with candidates (public)
PUT    /api/elections/<id>          – update (admin)
DELETE /api/elections/<id>          – delete (admin)
POST   /api/elections/<id>/candidates        – add candidate (admin)
DELETE /api/elections/<id>/candidates/<cid>  – remove candidate (admin)
"""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app import db
from models.election import Election, Candidate
from models.vote import Vote
from middleware.rbac import admin_required, voter_required
from flask_jwt_extended import get_jwt_identity

elections_bp = Blueprint('elections', __name__)


def _parse_dt(s):
    """Parse ISO datetime string → naive UTC datetime."""
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        return None


# ── Election CRUD ─────────────────────────────────────────────────────────────

@elections_bp.route('/', methods=['GET'])
def list_elections():
    status = request.args.get('status')   # upcoming | active | ended
    elections = Election.query.filter_by(is_active=True).order_by(Election.start_time.desc()).all()
    result = [e.to_dict() for e in elections]
    if status:
        result = [e for e in result if e['status'] == status]
    return jsonify({'elections': result, 'count': len(result)}), 200


@elections_bp.route('/<int:election_id>', methods=['GET'])
def get_election(election_id):
    election = Election.query.get_or_404(election_id)
    return jsonify({'election': election.to_dict(include_candidates=True)}), 200


@elections_bp.route('/', methods=['POST'])
@admin_required
def create_election():
    data = request.get_json(silent=True) or {}
    required = ['title', 'start_time', 'end_time']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 422

    start = _parse_dt(data['start_time'])
    end   = _parse_dt(data['end_time'])
    if not start or not end:
        return jsonify({'error': 'Invalid datetime format. Use ISO 8601.'}), 422
    if end <= start:
        return jsonify({'error': 'end_time must be after start_time'}), 422

    election = Election(
        title=data['title'],
        description=data.get('description', ''),
        start_time=start,
        end_time=end,
        created_by=get_jwt_identity()
    )
    db.session.add(election)
    db.session.flush()  # get ID before adding candidates

    # Optionally add candidates inline
    for c in data.get('candidates', []):
        if c.get('name'):
            db.session.add(Candidate(
                election_id=election.id,
                name=c['name'],
                party=c.get('party', 'Independent'),
                bio=c.get('bio', ''),
                photo_url=c.get('photo_url', ''),
            ))

    db.session.commit()
    return jsonify({'message': 'Election created', 'election': election.to_dict(include_candidates=True)}), 201


@elections_bp.route('/<int:election_id>', methods=['PUT'])
@admin_required
def update_election(election_id):
    election = Election.query.get_or_404(election_id)
    data = request.get_json(silent=True) or {}

    if 'title' in data:
        election.title = data['title']
    if 'description' in data:
        election.description = data['description']
    if 'start_time' in data:
        dt = _parse_dt(data['start_time'])
        if not dt:
            return jsonify({'error': 'Invalid start_time'}), 422
        election.start_time = dt
    if 'end_time' in data:
        dt = _parse_dt(data['end_time'])
        if not dt:
            return jsonify({'error': 'Invalid end_time'}), 422
        election.end_time = dt
    if 'is_active' in data:
        election.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({'message': 'Election updated', 'election': election.to_dict()}), 200


@elections_bp.route('/<int:election_id>', methods=['DELETE'])
@admin_required
def delete_election(election_id):
    election = Election.query.get_or_404(election_id)
    db.session.delete(election)
    db.session.commit()
    return jsonify({'message': 'Election deleted'}), 200


# ── Candidate Management ──────────────────────────────────────────────────────

@elections_bp.route('/<int:election_id>/candidates', methods=['POST'])
@admin_required
def add_candidate(election_id):
    election = Election.query.get_or_404(election_id)
    if election.status != 'upcoming':
        return jsonify({'error': 'Candidates can only be added before election starts'}), 409

    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'error': 'Candidate name is required'}), 422

    candidate = Candidate(
        election_id=election.id,
        name=data['name'],
        party=data.get('party', 'Independent'),
        bio=data.get('bio', ''),
        photo_url=data.get('photo_url', ''),
    )
    db.session.add(candidate)
    db.session.commit()
    return jsonify({'message': 'Candidate added', 'candidate': candidate.to_dict()}), 201


@elections_bp.route('/<int:election_id>/candidates/<int:candidate_id>', methods=['DELETE'])
@admin_required
def remove_candidate(election_id, candidate_id):
    candidate = Candidate.query.filter_by(id=candidate_id, election_id=election_id).first_or_404()
    db.session.delete(candidate)
    db.session.commit()
    return jsonify({'message': 'Candidate removed'}), 200


# ── Voter: check if already voted ─────────────────────────────────────────────

@elections_bp.route('/<int:election_id>/my-vote', methods=['GET'])
@voter_required
def my_vote(election_id):
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()
    vote = Vote.query.filter_by(user_id=user_id, election_id=election_id).first()
    if vote:
        return jsonify({'voted': True, 'vote': vote.to_dict()}), 200
    return jsonify({'voted': False}), 200