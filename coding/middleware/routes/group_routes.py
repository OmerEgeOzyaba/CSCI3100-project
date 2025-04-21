from flask import Blueprint, jsonify, request

group_bp = Blueprint('groups', __name__)

# Dummy data
groups = [
    {"id": 1, "name": "Project Alpha", "description": "Software development team", "created_at": "2025-03-01T10:00:00Z", "members": [{"email": "test@gmail.com", "role": "admin"}, {"email": "test@gmail.com", "role": "contributor"}, {"email": "test@gmail.com", "role": "contributor"}], "owner_id": 1},
    {"id": 2, "name": "Marketing Team", "description": "Product marketing", "created_at": "2025-03-05T15:30:00Z", "members": [{"email": "test@gmail.com", "role": "admin"}, {"email": "test@gmail.com", "role": "contributor"}], "owner_id": 3}
]

@group_bp.route('/', methods=['GET'])
def get_groups():
    return jsonify({"groups": groups})

@group_bp.route('/<int:group_id>', methods=['GET'])
def get_group(group_id):
    group = next((g for g in groups if g["id"] == group_id), None)
    if group:
        return jsonify({"group": group})
    return jsonify({"error": "Group not found"}), 404

@group_bp.route('/', methods=['POST'])
def create_group():
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    new_group = {
        "id": len(groups) + 1,
        "name": request.json.get('name'),
        "description": request.json.get('description'),
        "created_at": "2025-04-15T08:00:00Z",  # Fixed date for dummy data
        "members": [request.json.get('owner_id')],
        "owner_id": request.json.get('owner_id')
    }
    groups.append(new_group)
    return jsonify({"group": new_group}), 201

@group_bp.route('/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    # TODO
    return jsonify({}), 200

@group_bp.route('/<int:group_id>/leave', methods=['POST'])
def leave_group(group_id):
    # TODO
    return jsonify({}), 200

@group_bp.route('/<int:group_id>/members', methods=['POST'])
def add_member(group_id):
    group = next((g for g in groups if g["id"] == group_id), None)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    if not request.json or 'user_id' not in request.json:
        return jsonify({"error": "User ID required"}), 400
        
    user_id = request.json.get('user_id')
    if user_id in group['members']:
        return jsonify({"error": "User already in group"}), 400
        
    group['members'].append(user_id)
    return jsonify({"group": group})