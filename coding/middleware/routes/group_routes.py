from flask import Blueprint, jsonify, request, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware_data_classes import Group, Membership, User, Role, InvitationStatus
from database import Database
from datetime import datetime
from sqlalchemy import and_

group_bp = Blueprint('groups', __name__)

# Convert Group SQLAlchemy object to JSON serializable dict
def group_to_dict(group, include_members=False):
    result = {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at.isoformat() if group.created_at else None
    }
    
    if include_members and group.memberships:
        result["members"] = [{
            "email": membership.user_id,
            "role": membership.role.value,
            "status": membership.status.value
        } for membership in group.memberships]
    
    return result

@group_bp.route('/', methods=['GET'])
@jwt_required()
def get_groups():
    """Get all groups for the current user"""
    try:
        current_user_email = get_jwt_identity()
        current_app.logger.info(f"Fetching groups for user: {current_user_email}")
        db = Database().get_session()

        # Get all memberships for the user
        user_memberships = db.query(Membership).filter(
            Membership.user_id == current_user_email
        ).all()
        
        current_app.logger.info(f"Found {len(user_memberships)} memberships for user {current_user_email}")

        # Get all groups where user has ACCEPTED membership
        groups_list = []
        for membership in user_memberships:
            if membership.status == InvitationStatus.ACCEPTED:
                group = db.query(Group).filter(Group.id == membership.group_id).first()
                if group:
                    group_dict = {
                        "id": group.id,
                        "name": group.name,
                        "description": group.description,
                        "created_at": group.created_at.isoformat() if group.created_at else None
                    }
                    groups_list.append(group_dict)
        
        current_app.logger.info(f"Returning {len(groups_list)} groups with ACCEPTED status")
        return jsonify({"groups": groups_list})
    except Exception as e:
        current_app.logger.error(f"Error fetching groups: {str(e)}")
        return jsonify({"error": "Failed to fetch groups"}), 500
    finally:
        db.close()

@group_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    """Get a specific group with its members"""
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()

        # Get the group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return jsonify({"error": "Group not found"}), 404

        # Verify the user has access to this group
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()

        if not membership:
            return jsonify({"error": "Access denied"}), 403

        # Get the group's memberships
        memberships = db.query(Membership).filter(
            Membership.group_id == group_id
        ).all()

        # Format the response
        group_data = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_at": group.created_at.isoformat() if group.created_at else None,
            "members": [{
                "email": m.user_id,
                "role": m.role.value,
                "status": m.status.value
            } for m in memberships]
        }

        return jsonify({"group": group_data})
    except Exception as e:
        current_app.logger.error(f"Error fetching group: {str(e)}")
        return jsonify({"error": "Failed to fetch group"}), 500
    finally:
        db.close()

@group_bp.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    """Update a group's name and description"""
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()
        
        # Get the group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return jsonify({"error": "Group not found"}), 404
        
        # Verify the user has access to this group and is an admin
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.ACCEPTED,
                Membership.role == Role.ADMIN
            )
        ).first()
        
        if not membership:
            return jsonify({"error": "You don't have permission to update this group"}), 403
        
        # Update the group
        if 'name' in request.json:
            group.name = request.json.get('name')
        
        if 'description' in request.json:
            group.description = request.json.get('description')
        
        db.commit()
        
        # Return the updated group
        return jsonify({
            "group": {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at.isoformat() if group.created_at else None
            }
        })
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error updating group: {str(e)}")
        return jsonify({"error": f"Failed to update group: {str(e)}"}), 500
    finally:
        db.close()

@group_bp.route('/', methods=['POST'])
@jwt_required()
def create_group():
    """Create a new group"""
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    required_fields = ['name']
    for field in required_fields:
        if field not in request.json:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        current_user_email = get_jwt_identity()
        current_app.logger.info(f"Creating group for user: {current_user_email}")
        db = Database().get_session()
        
        # Create the group
        new_group = Group(
            name=request.json.get('name'),
            description=request.json.get('description', ''),
            created_at=datetime.utcnow()
        )
        
        db.add(new_group)
        db.flush()  # Get the ID without committing
        current_app.logger.info(f"Created group with ID {new_group.id}")
        
        # Create membership for the current user as ADMIN with ACCEPTED status
        membership = Membership(
            user_id=current_user_email,
            group_id=new_group.id,
            role=Role.ADMIN,
            status=InvitationStatus.ACCEPTED,
            join_date=datetime.utcnow()
        )
        
        db.add(membership)
        db.commit()
        current_app.logger.info(f"Added user {current_user_email} as ADMIN to group {new_group.id}")
        
        # Return the created group
        group_data = {
            "id": new_group.id,
            "name": new_group.name,
            "description": new_group.description,
            "created_at": new_group.created_at.isoformat(),
            "members": [{
                "email": current_user_email,
                "role": "admin",
                "status": "accepted"
            }]
        }
        
        return jsonify({"group": group_data}), 201
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error creating group: {str(e)}")
        return jsonify({"error": f"Failed to create group: {str(e)}"}), 500
    finally:
        db.close()

@group_bp.route('/<int:group_id>/leave', methods=['POST'])
@jwt_required()
def leave_group(group_id):
    """Leave a group"""
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()
        
        # Find the membership
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()
        
        if not membership:
            return jsonify({"error": "You are not a member of this group"}), 404
        
        # Delete the membership
        db.delete(membership)
        db.commit()
        
        return jsonify({"message": "Successfully left the group"})
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error leaving group: {str(e)}")
        return jsonify({"error": "Failed to leave group"}), 500
    finally:
        db.close()

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