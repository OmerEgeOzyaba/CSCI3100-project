from flask import Blueprint, jsonify, request, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware_data_classes import Membership, Role, InvitationStatus, User, Group
from database import Database
from datetime import datetime
from sqlalchemy import and_

invitation_bp = Blueprint('invitations', __name__)

@invitation_bp.route('/', methods=['GET'])
@jwt_required()
def get_invitations():
    """Get all invitations for the current user"""
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()
        
        # Get all pending invitations for the user
        invitations = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.status == InvitationStatus.SENT
            )
        ).all()
        
        invitations_data = []
        for invitation in invitations:
            # Get the group and inviter details
            group = db.query(Group).filter(Group.id == invitation.group_id).first()
            
            invitations_data.append({
                "id": f"{invitation.user_id}_{invitation.group_id}",  # Composite key
                "group_id": invitation.group_id,
                "group_name": group.name if group else "Unknown Group",
                "inviter_email": invitation.inviter_email,
                "invite_date": invitation.invite_date.isoformat() if invitation.invite_date else None,
                "status": invitation.status.value
            })
        
        return jsonify({"invitations": invitations_data})
    except Exception as e:
        current_app.logger.error(f"Error fetching invitations: {str(e)}")
        return jsonify({"error": "Failed to fetch invitations"}), 500
    finally:
        db.close()

@invitation_bp.route('/send', methods=['POST'])
@jwt_required()
def send_invitation():
    """Send an invitation to a user to join a group"""
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    email = request.json.get('email')
    group_id = request.json.get('group_id')
    role = request.json.get('role', 'reader')  # Default to reader if not specified
    
    if not email or not group_id:
        return jsonify({"error": "Email and group_id are required"}), 400
    
    try:
        inviter_email = get_jwt_identity()
        db = Database().get_session()
        
        # Verify that the inviter is a member of the group with admin or contributor role
        inviter_membership = db.query(Membership).filter(
            and_(
                Membership.user_id == inviter_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()
        
        if not inviter_membership:
            return jsonify({"error": "You are not a member of this group"}), 403
        
        if inviter_membership.role not in [Role.ADMIN, Role.CONTRIBUTOR]:
            return jsonify({"error": "You don't have permission to invite users to this group"}), 403
        
        # Check if the user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if the user is already a member of the group
        existing_membership = db.query(Membership).filter(
            and_(
                Membership.user_id == email,
                Membership.group_id == group_id
            )
        ).first()
        
        if existing_membership:
            if existing_membership.status == InvitationStatus.ACCEPTED:
                return jsonify({"error": "User is already a member of this group"}), 400
            elif existing_membership.status == InvitationStatus.SENT:
                return jsonify({"error": "User already has a pending invitation to this group"}), 400
        
        # Create a new membership with SENT status and specified role
        membership = Membership(
            user_id=email,
            group_id=group_id,
            role=Role(role),  # Convert string to Role enum
            inviter_email=inviter_email,
            invite_date=datetime.utcnow(),
            status=InvitationStatus.SENT
        )
        
        db.add(membership)
        db.commit()
        
        return jsonify({
            "message": "Invitation sent successfully",
            "invitation": {
                "id": f"{email}_{group_id}",  # Composite key
                "email": email,
                "group_id": group_id,
                "role": role,
                "inviter_email": inviter_email,
                "invite_date": membership.invite_date.isoformat(),
                "status": membership.status.value
            }
        }), 201
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error sending invitation: {str(e)}")
        return jsonify({"error": f"Failed to send invitation: {str(e)}"}), 500
    finally:
        db.close()

@invitation_bp.route('/accept', methods=['POST'])
@jwt_required()
def accept_invitation():
    """Accept an invitation to join a group"""
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    group_id = request.json.get('group_id')
    
    if not group_id:
        return jsonify({"error": "Group ID is required"}), 400
    
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()
        
        # Find the invitation
        invitation = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.SENT
            )
        ).first()
        
        if not invitation:
            return jsonify({"error": "Invitation not found"}), 404
        
        # Update the invitation status to ACCEPTED
        invitation.status = InvitationStatus.ACCEPTED
        invitation.join_date = datetime.utcnow()
        db.commit()
        
        return jsonify({
            "message": "Invitation accepted successfully",
            "membership": {
                "user_id": invitation.user_id,
                "group_id": invitation.group_id,
                "role": invitation.role.value,
                "status": invitation.status.value,
                "join_date": invitation.join_date.isoformat()
            }
        })
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error accepting invitation: {str(e)}")
        return jsonify({"error": "Failed to accept invitation"}), 500
    finally:
        db.close()

@invitation_bp.route('/decline', methods=['POST'])
@jwt_required()
def decline_invitation():
    """Decline an invitation to join a group"""
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    group_id = request.json.get('group_id')
    
    if not group_id:
        return jsonify({"error": "Group ID is required"}), 400
    
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()
        
        # Find the invitation
        invitation = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.SENT
            )
        ).first()
        
        if not invitation:
            return jsonify({"error": "Invitation not found"}), 404
        
        # Delete the invitation
        db.delete(invitation)
        db.commit()
        
        return jsonify({
            "message": "Invitation declined successfully"
        })
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error declining invitation: {str(e)}")
        return jsonify({"error": "Failed to decline invitation"}), 500
    finally:
        db.close()