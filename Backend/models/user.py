"""
User Model — roles: admin | voter
"""
from datetime import datetime, timezone
import bcrypt
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    full_name  = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password   = db.Column(db.String(255), nullable=False)
    role       = db.Column(db.String(20),  nullable=False, default='voter')  # 'admin' | 'voter'
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')

    def set_password(self, plain_text: str):
        self.password = bcrypt.hashpw(
            plain_text.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, plain_text: str) -> bool:
        return bcrypt.checkpw(
            plain_text.encode('utf-8'),
            self.password.encode('utf-8')
        )

    def to_dict(self):
        return {
            'id':         self.id,
            'full_name':  self.full_name,
            'email':      self.email,
            'role':       self.role,
            'is_active':  self.is_active,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'


class TokenBlacklist(db.Model):
    """Stores revoked JWTs (logout / refresh invalidation)."""
    __tablename__ = 'token_blacklist'

    id         = db.Column(db.Integer, primary_key=True)
    jti        = db.Column(db.String(36), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)
    revoked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<BlacklistedToken {self.jti}>'