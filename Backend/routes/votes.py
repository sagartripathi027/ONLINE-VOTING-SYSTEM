"""
Votes Routes
POST /api/votes/cast   – cast a vote (voter)
GET  /api/votes/my     – voter's own vote history
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app import db, socketio
from models.vote import Vote
from models.election import Election, Candidate
from middleware.rbac import voter_required

votes_bp = Blueprint('votes', __name__)


@votes_bp.route('/cast', methods=['POST'])
@voter_required
def cast_vote():
    data = request.get_json(silent=True) or {}
    election_id  = data.get('election_id')
    candidate_id = data.get('candidate_id')

    if not election_id or not candidate_id:
        return jsonify({'error': 'election_id and candidate_id are required'}), 422

    # Validate election exists and is active
    election = Election.query.get(election_id)
    if not election or not election.is_active:
        return jsonify({'error': 'Election not found or inactive'}), 404

    if election.status != 'active':
        return jsonify({'error': f"Election is {election.status}. Voting is not allowed."}), 409

    # Validate candidate belongs to this election
    candidate = Candidate.query.filter_by(id=candidate_id, election_id=election_id).first()
    if not candidate:
        return jsonify({'error': 'Candidate not found in this election'}), 404

    user_id = get_jwt_identity()

    # Try inserting vote (DB constraint handles duplicate)
    vote = Vote(
        user_id=user_id,
        election_id=election_id,
        candidate_id=candidate_id,
        ip_address=request.remote_addr
    )
    db.session.add(vote)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'You have already voted in this election'}), 409

    # ── Real-time broadcast via SocketIO ──────────────────────────────────────
    results = _build_results(election)
    socketio.emit('vote_update', {
        'election_id': election_id,
        'results':     results,
        'total_votes': election.total_votes,
    }, room=f'election_{election_id}')

    return jsonify({
        'message':   'Vote cast successfully',
        'vote':      vote.to_dict(),
        'candidate': candidate.name,
    }), 201


@votes_bp.route('/my', methods=['GET'])
@voter_required
def my_votes():
    user_id = get_jwt_identity()
    votes = Vote.query.filter_by(user_id=user_id).all()
    return jsonify({'votes': [v.to_dict() for v in votes]}), 200


def _build_results(election):
    """Return list of {candidate, votes, percentage} sorted by votes desc."""
    candidates = election.candidates.all()
    total = election.total_votes
    results = []
    for c in candidates:
        count = c.vote_count
        results.append({
            'candidate_id': c.id,
            'name':         c.name,
            'party':        c.party,
            'votes':        count,
            'percentage':   round((count / total * 100), 2) if total else 0,
        })
    return sorted(results, key=lambda x: x['votes'], reverse=True)