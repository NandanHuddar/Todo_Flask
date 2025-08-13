from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.models import db
from routes.auth import auth_bp
from routes.tasks import tasks_bp
from routes.views import views_bp
from scheduler import init_scheduler

def create_app():
    app = Flask(__name__)
    limiter = Limiter(
        get_remote_address,
        default_limits=["5 per minute"],
        storage_uri="memory://",
        strategy="fixed-window",
        on_breach=lambda: (jsonify({"message": "Too many requests"}), 429)
    )
    limiter.init_app(app)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'postgresql+psycopg2://todo_user:secret123@localhost:5432/todo_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

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
    app.run(debug=True, host='0.0.0.0')
