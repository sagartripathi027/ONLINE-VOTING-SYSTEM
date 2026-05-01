"""
Vote Model — one vote per user per election (enforced at DB level)
"""
from datetime import datetime, timezone
from app import db


class Vote(db.Model):
    __tablename__ = 'votes'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'election_id', name='uq_user_election'),
    )

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'),      nullable=False)
    election_id  = db.Column(db.Integer, db.ForeignKey('elections.id'),  nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    voted_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # IP for audit trail (not exposed publicly)
    ip_address   = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        return {
            'id':           self.id,
            'election_id':  self.election_id,
            'candidate_id': self.candidate_id,
            'voted_at':     self.voted_at.isoformat(),
        }

    def __repr__(self):
        return f'<Vote user={self.user_id} election={self.election_id}>'