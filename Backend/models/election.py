"""
Election & Candidate Models
"""
from datetime import datetime, timezone
from app import db


class Election(db.Model):
    __tablename__ = 'elections'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    start_time  = db.Column(db.DateTime, nullable=False)
    end_time    = db.Column(db.DateTime, nullable=False)
    is_active   = db.Column(db.Boolean, default=True)
    created_by  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy='dynamic',
                                 cascade='all, delete-orphan')
    votes      = db.relationship('Vote',      backref='election', lazy='dynamic',
                                 cascade='all, delete-orphan')

    @property
    def status(self):
        now = datetime.now(timezone.utc)
        # make start/end timezone-aware if stored as naive
        start = self.start_time.replace(tzinfo=timezone.utc) if self.start_time.tzinfo is None else self.start_time
        end   = self.end_time.replace(tzinfo=timezone.utc)   if self.end_time.tzinfo   is None else self.end_time
        if now < start:
            return 'upcoming'
        elif now > end:
            return 'ended'
        return 'active'

    @property
    def total_votes(self):
        return self.votes.count()

    def to_dict(self, include_candidates=False):
        data = {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'start_time':  self.start_time.isoformat(),
            'end_time':    self.end_time.isoformat(),
            'is_active':   self.is_active,
            'status':      self.status,
            'total_votes': self.total_votes,
            'created_at':  self.created_at.isoformat(),
        }
        if include_candidates:
            data['candidates'] = [c.to_dict() for c in self.candidates]
        return data

    def __repr__(self):
        return f'<Election {self.title}>'


class Candidate(db.Model):
    __tablename__ = 'candidates'

    id          = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    name        = db.Column(db.String(120), nullable=False)
    party       = db.Column(db.String(120), default='Independent')
    bio         = db.Column(db.Text, default='')
    photo_url   = db.Column(db.String(500), default='')
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    votes = db.relationship('Vote', backref='candidate', lazy='dynamic')

    @property
    def vote_count(self):
        return self.votes.count()

    def to_dict(self):
        return {
            'id':          self.id,
            'election_id': self.election_id,
            'name':        self.name,
            'party':       self.party,
            'bio':         self.bio,
            'photo_url':   self.photo_url,
            'vote_count':  self.vote_count,
        }

    def __repr__(self):
        return f'<Candidate {self.name}>'