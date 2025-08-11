from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, Task
from datetime import datetime
import jwt  
tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'message': 'Missing or invalid token'}), 401
    
    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = payload.get('sub')
        if not user_id:
            return jsonify({'message': 'Invalid token payload'}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        due_date_str = task.due_date.isoformat() if task.due_date else None
        result.append({
            'id': task.id,
            'title': task.title,
            'details': task.details,
            'due_date': due_date_str,
            'completed': task.completed
        })

    return jsonify(result), 200

@tasks_bp.route('/api/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    due_date = None
    if data.get('due_date'):
        due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    
    new_task = Task(
        title=data['title'],
        details=data.get('details', ''),
        due_date=due_date,
        user_id=user_id
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({
        'id': new_task.id,
        'title': new_task.title,
        'details': new_task.details,
        'due_date': new_task.due_date.isoformat() if new_task.due_date else None,
        'completed': new_task.completed
    }), 201

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'details' in data:
        task.details = data['details']
    if 'due_date' in data and data['due_date']:
        task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    elif 'due_date' in data and not data['due_date']:
        task.due_date = None
    if 'completed' in data:
        task.completed = data['completed']
    
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'details': task.details,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'completed': task.completed
    }), 200

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200
