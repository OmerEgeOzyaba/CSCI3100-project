from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.task_service import TaskService
from datetime import datetime

task_bp = Blueprint('tasks', __name__)
task_service = TaskService()

def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": "completed" if task.status else "pending",
        "group_id": task.group_id
    }

@task_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        user_email = get_jwt_identity()
        tasks = task_service.get_tasks_for_user(user_email)
        return jsonify({"tasks": [task_to_dict(t) for t in tasks]})
    except Exception as e:
        current_app.logger.error(f"Error fetching tasks: {str(e)}")
        return jsonify({"error": "Failed to fetch tasks"}), 500

@task_bp.route('/group/<int:group_id>', methods=['GET'])
@jwt_required()
def get_tasks_by_group(group_id):
    try:
        user_email = get_jwt_identity()
        tasks = task_service.get_tasks_for_group(user_email, group_id)
        return jsonify({"tasks": [task_to_dict(t) for t in tasks]})
    except Exception as e:
        current_app.logger.error(f"Error fetching group tasks: {str(e)}")
        return jsonify({"error": "Failed to fetch group tasks"}), 500

@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    try:
        user_email = get_jwt_identity()
        task = task_service.get_task(user_email, task_id)
        if not task:
            return jsonify({"error": "Task not found or access denied"}), 404
        return jsonify({"task": task_to_dict(task)})
    except Exception as e:
        current_app.logger.error(f"Error fetching task: {str(e)}")
        return jsonify({"error": "Failed to fetch task"}), 500

@task_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    if not request.json or 'title' not in request.json or 'group_id' not in request.json:
        return jsonify({"error": "Missing title or group_id"}), 400
    try:
        user_email = get_jwt_identity()
        due_date = datetime.fromisoformat(request.json['due_date'].replace('Z', '+00:00')) if request.json.get('due_date') else None
        task = task_service.create_task(
            user_email,
            request.json['title'],
            request.json.get('description', ''),
            request.json['group_id'],
            due_date
        )
        return jsonify({"task": task_to_dict(task)}), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Failed to create task"}), 500

@task_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    try:
        user_email = get_jwt_identity()
        due_date = datetime.fromisoformat(request.json['due_date'].replace('Z', '+00:00')) if request.json.get('due_date') else None
        status = request.json['status'].lower() == 'completed' if 'status' in request.json else None
        task = task_service.update_task(
            user_email,
            task_id,
            title=request.json.get('title'),
            description=request.json.get('description'),
            due_date=due_date,
            status=status
        )
        return jsonify({"task": task_to_dict(task)})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating task: {str(e)}")
        return jsonify({"error": "Failed to update task"}), 500

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        user_email = get_jwt_identity()
        task_service.delete_task(user_email, task_id)
        return jsonify({"message": "Task deleted successfully"})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting task: {str(e)}")
        return jsonify({"error": "Failed to delete task"}), 500