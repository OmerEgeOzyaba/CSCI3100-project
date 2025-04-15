from flask import Blueprint, jsonify, request

task_bp = Blueprint('tasks', __name__)

# Dummy data
tasks = [
    {"id": 1, "title": "Complete project proposal", "description": "Finish the proposal by Friday", "due_date": "2025-04-20T23:59:59Z", "status": "pending", "group_id": 1, "assigned_to": [1, 2]},
    {"id": 2, "title": "Research competitors", "description": "Analyze top 3 competitors", "due_date": "2025-04-18T18:00:00Z", "status": "completed", "group_id": 1, "assigned_to": [3]},
    {"id": 3, "title": "Schedule team meeting", "description": "Set up Zoom call for next week", "due_date": "2025-04-15T12:00:00Z", "status": "pending", "group_id": 2, "assigned_to": [1, 2, 3]}
]

@task_bp.route('/', methods=['GET'])
def get_tasks():
    return jsonify({"tasks": tasks})

@task_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task:
        return jsonify({"task": task})
    return jsonify({"error": "Task not found"}), 404

@task_bp.route('/', methods=['POST'])
def create_task():
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    new_task = {
        "id": len(tasks) + 1,
        "title": request.json.get('title'),
        "description": request.json.get('description'),
        "due_date": request.json.get('due_date'),
        "status": "pending",
        "group_id": request.json.get('group_id'),
        "assigned_to": request.json.get('assigned_to', [])
    }
    tasks.append(new_task)
    return jsonify({"task": new_task}), 201

@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
        
    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])
    task['due_date'] = request.json.get('due_date', task['due_date'])
    task['status'] = request.json.get('status', task['status'])
    task['assigned_to'] = request.json.get('assigned_to', task['assigned_to'])
    
    return jsonify({"task": task})