"""
Flask Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.elections import elections_bp
    from routes.votes import votes_bp
    from routes.admin import admin_bp
    from routes.results import results_bp

    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(elections_bp, url_prefix='/api/elections')
    app.register_blueprint(votes_bp,     url_prefix='/api/votes')
    app.register_blueprint(admin_bp,     url_prefix='/api/admin')
    app.register_blueprint(results_bp,   url_prefix='/api/results')

    # JWT token blacklist check
    from models.user import TokenBlacklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token is not None

    # Create all tables
    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Create default admin if none exists."""
    from models.user import User
    if not User.query.filter_by(role='admin').first():
        admin = User(
            full_name='System Admin',
            email='admin@vote.local',
            role='admin'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created → admin@vote.local / Admin@123")