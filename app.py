import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.models import db
from routes.auth import auth_bp
from routes.tasks import tasks_bp
from routes.views import views_bp
from scheduler import init_scheduler
from config.config import DevConfig, StagingConfig, ProdConfig

def create_app():
    app = Flask(__name__)

    env = os.getenv('ENVIRONMENT', 'Dev')
    if env == 'Dev':
        app.config.from_object(DevConfig)
    elif env == 'Stag':
        app.config.from_object(StagingConfig)
    elif env == 'Prod':
        app.config.from_object(ProdConfig)
    else:
        raise ValueError(f"Invalid ENVIRONMENT: {env}")

    limiter = Limiter(
        get_remote_address,
        default_limits=["5 per minute"],
        storage_uri="memory://",
        strategy="fixed-window",
        on_breach=lambda: (jsonify({"message": "Too many requests"}), 429)
    )
    limiter.init_app(app)

    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    mail = Mail(app)
    app.limiter = limiter

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401

    init_scheduler(app, mail)

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(views_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
