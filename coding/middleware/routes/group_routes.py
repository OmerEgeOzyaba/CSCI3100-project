from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.group_service import GroupService

group_bp = Blueprint('groups', __name__)
group_service = GroupService()

def group_to_dict(group, include_members=False):
    result = {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at.isoformat() if hasattr(group.created_at, 'isoformat') else group.created_at
    }
    if include_members and group.memberships:
        result["members"] = [{"email": m.user_id, "role": m.role.value, "status": m.status.value} for m in group.memberships]
    return result
    return result

@group_bp.route('/', methods=['GET'])
@jwt_required()
def get_groups():
    try:
        user_email = get_jwt_identity()
        groups = group_service.get_groups(user_email)
        return jsonify({"groups": [group_to_dict(g) for g in groups]})
    except Exception as e:
        current_app.logger.error(f"Error fetching groups: {str(e)}")
        return jsonify({"error": "Failed to fetch groups"}), 500

@group_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    try:
        user_email = get_jwt_identity()
        group = group_service.get_group(user_email, group_id)
        if not group:
            return jsonify({"error": "Group not found or access denied"}), 404
        return jsonify({"group": group_to_dict(group, include_members=True)})
    except Exception as e:
        current_app.logger.error(f"Error fetching group: {str(e)}")
        return jsonify({"error": "Failed to fetch group"}), 500

@group_bp.route('/', methods=['POST'])
@jwt_required()
def create_group():
    if not request.json or 'name' not in request.json:
        return jsonify({"error": "Missing name"}), 400
    try:
        user_email = get_jwt_identity()
        group = group_service.create_group(
            user_email,
            request.json['name'],
            request.json.get('description', '')
        )
        return jsonify({"group": group_to_dict(group, include_members=True)}), 201
    except Exception as e:
        current_app.logger.error(f"Error creating group: {str(e)}")
        return jsonify({"error": "Failed to create group"}), 500

@group_bp.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    try:
        user_email = get_jwt_identity()
        group_data = group_service.update_group(
            user_email,
            group_id,
            name=request.json.get('name'),
            description=request.json.get('description')
        )
        return jsonify({"group": group_data})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating group: {str(e)}")
        return jsonify({"error": "Failed to update group"}), 500

@group_bp.route('/<int:group_id>/leave', methods=['POST'])
@jwt_required()
def leave_group(group_id):
    try:
        user_email = get_jwt_identity()
        group_service.leave_group(user_email, group_id)
        return jsonify({"message": "Successfully left the group"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error leaving group: {str(e)}")
        return jsonify({"error": "Failed to leave group"}), 500