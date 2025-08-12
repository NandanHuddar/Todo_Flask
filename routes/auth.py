from flask import Blueprint, request, jsonify, current_app, render_template, url_for, flash, redirect
from flask_jwt_extended import create_access_token
from models.models import db, User
from flask_mail import Message
from utils.security import hash_password, verify_password
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import time

TOKEN_EXPIRY_SECONDS = 3600

auth_bp = Blueprint('auth', __name__)

def get_serializer():
    secret = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    return URLSafeTimedSerializer(secret, salt='email-confirm-salt')

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid payload'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 409

    hashed_password = hash_password(password)

    payload = {
        'email': email,
        'password': hashed_password,
        'iat': int(time.time())
    }

    s = get_serializer()
    token = s.dumps(payload)

    verification_url = url_for('auth.verify_email', token=token, _external=True)

    try:
        msg = Message(
            subject='Email Verification - Click to Verify',
            recipients=[email],
            html=render_template('email_template.html',
                                 verification_url=verification_url,
                                 email=email),
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        current_app.extensions['mail'].send(msg)

        return jsonify({'message': 'Registration successful. Please verify your email.', 'email': email}), 200

    except Exception as e:
        return jsonify({'message': f'Failed to send verification email: {str(e)}'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid payload'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not verify_password(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    if not user.email_verified:
        return jsonify({'message': 'Please verify your email before logging in.'}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'Login successful', 'access_token': access_token}), 200

@auth_bp.route('/api/verify_email/<token>', methods=['GET'])
def verify_email(token):

    s = get_serializer()
    try:
        data = s.loads(token, max_age=TOKEN_EXPIRY_SECONDS)
    except SignatureExpired:
        return render_template('verification_status.html', status='error', message='Verification link has expired.')
    except BadSignature:
        return render_template('verification_status.html', status='error', message='Invalid verification token.')

    email = data.get('email')
    hashed_password = data.get('password')

    if not email or not hashed_password:
        return render_template('verification_status.html', status='error', message='Invalid token payload.')

    existing = User.query.filter_by(email=email).first()
    if existing:
        if existing.email_verified:
            return render_template('verification_status.html', status='success', message=f'Email {email} already verified.')
        else:
            existing.email_verified = True
            db.session.commit()
            return render_template('verification_status.html', status='success', message=f'Email {email} verified successfully')

    try:
        new_user = User(email=email, password=hashed_password, email_verified=True)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return render_template('verification_status.html', status='error', message=f'Failed to create user: {str(e)}')

    return render_template('verification_status.html', status='success', message=f'Email {email} verified successfully')
