from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.membership_service import MembershipService

invitation_bp = Blueprint('invitations', __name__)
membership_service = MembershipService()

@invitation_bp.route('/', methods=['GET'])
@jwt_required()
def get_invitations():
    try:
        user_email = get_jwt_identity()
        invitations = membership_service.get_invitations(user_email)
        invitations_data = [{
            "id": f"{inv.user_id}_{inv.group_id}",
            "group_id": inv.group_id,
            "group_name": inv.group.name if inv.group else "Unknown",
            "inviter_email": inv.inviter_email,
            "invite_date": inv.invite_date.isoformat() if inv.invite_date else None,
            "status": inv.status.value
        } for inv in invitations]
        return jsonify({"invitations": invitations_data})
    except Exception as e:
        current_app.logger.error(f"Error fetching invitations: {str(e)}")
        return jsonify({"error": "Failed to fetch invitations"}), 500

@invitation_bp.route('/send', methods=['POST'])
@jwt_required()
def send_invitation():
    try:
        inviter_email = get_jwt_identity()
        invite = membership_service.send_invitation(
            inviter_email,
            request.json['email'],
            request.json['group_id']
        )
        return jsonify({
            "message": "Invitation sent successfully",
            "invitation": invite  # Changed from invite_data to invite
        }), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error sending invitation: {str(e)}")
        return jsonify({"error": "Failed to send invitation"}), 500

@invitation_bp.route('/accept', methods=['POST'])
@jwt_required()
def accept_invitation():
    if not request.json or 'group_id' not in request.json:
        return jsonify({"error": "Missing group_id"}), 400
    try:
        user_email = get_jwt_identity()
        membership = membership_service.accept_invitation(user_email, request.json['group_id'])
        return jsonify({
            "message": "Invitation accepted successfully",
            "membership": {
                "user_id": membership.user_id,
                "group_id": membership.group_id,
                "role": membership.role.value,
                "status": membership.status.value,
                "join_date": membership.join_date.isoformat()
            }
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error accepting invitation: {str(e)}")
        return jsonify({"error": "Failed to accept invitation"}), 500

@invitation_bp.route('/decline', methods=['POST'])
@jwt_required()
def decline_invitation():
    if not request.json or 'group_id' not in request.json:
        return jsonify({"error": "Missing group_id"}), 400
    try:
        user_email = get_jwt_identity()
        membership_service.decline_invitation(user_email, request.json['group_id'])
        return jsonify({"message": "Invitation declined successfully"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error declining invitation: {str(e)}")
        return jsonify({"error": "Failed to decline invitation"}), 500