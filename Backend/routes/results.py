"""
Results Routes
GET /api/results/<election_id>          – live results
GET /api/results/<election_id>/summary  – winner, turnout, stats
"""
from flask import Blueprint, jsonify
from models.election import Election, Candidate
from middleware.rbac import voter_required

results_bp = Blueprint('results', __name__)


def _get_results(election):
    total = election.total_votes
    candidates = election.candidates.order_by(Candidate.id).all()
    data = []
    for c in candidates:
        count = c.vote_count
        data.append({
            'candidate_id': c.id,
            'name':         c.name,
            'party':        c.party,
            'photo_url':    c.photo_url,
            'votes':        count,
            'percentage':   round(count / total * 100, 2) if total else 0.0,
        })
    return sorted(data, key=lambda x: x['votes'], reverse=True)


@results_bp.route('/<int:election_id>', methods=['GET'])
@voter_required
def live_results(election_id):
    election = Election.query.get_or_404(election_id)
    results = _get_results(election)
    return jsonify({
        'election_id':  election_id,
        'title':        election.title,
        'status':       election.status,
        'total_votes':  election.total_votes,
        'results':      results,
    }), 200


@results_bp.route('/<int:election_id>/summary', methods=['GET'])
@voter_required
def result_summary(election_id):
    election = Election.query.get_or_404(election_id)
    results = _get_results(election)
    total = election.total_votes

    winner = results[0] if results else None
    is_tie = (
        len(results) >= 2 and
        results[0]['votes'] == results[1]['votes'] and
        results[0]['votes'] > 0
    )

    return jsonify({
        'election_id':  election_id,
        'title':        election.title,
        'status':       election.status,
        'total_votes':  total,
        'winner':       winner if not is_tie else None,
        'is_tie':       is_tie,
        'results':      results,
    }), 200