from flask import Blueprint, render_template, send_from_directory

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/login')
def login_page():
    return render_template('login.html')

@views_bp.route('/register')
def register_page():
    return render_template('register.html')

@views_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@views_bp.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)
