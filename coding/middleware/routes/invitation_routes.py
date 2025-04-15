from flask import Blueprint, jsonify, request

invitation_bp = Blueprint('invitations', __name__)

# Dummy data
invitations = [
    {"id": 1, "sender_id": 1, "recipient_id": 2, "group_id": 1, "status": "pending", "created_at": "2025-04-10T12:00:00Z"},
    {"id": 2, "sender_id": 3, "recipient_id": 1, "group_id": 2, "status": "accepted", "created_at": "2025-04-11T10:30:00Z"},
    {"id": 3, "sender_id": 2, "recipient_id": 3, "group_id": 1, "status": "declined", "created_at": "2025-04-09T15:45:00Z"}
]

@invitation_bp.route('/', methods=['GET'])
def get_invitations():
    return jsonify({"invitations": invitations})

@invitation_bp.route('/<int:invitation_id>', methods=['GET'])
def get_invitation(invitation_id):
    invitation = next((i for i in invitations if i["id"] == invitation_id), None)
    if invitation:
        return jsonify({"invitation": invitation})
    return jsonify({"error": "Invitation not found"}), 404

@invitation_bp.route('/', methods=['POST'])
def create_invitation():
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    new_invitation = {
        "id": len(invitations) + 1,
        "sender_id": request.json.get('sender_id'),
        "recipient_id": request.json.get('recipient_id'),
        "group_id": request.json.get('group_id'),
        "status": "pending",
        "created_at": "2025-04-15T08:00:00Z"  # Fixed date for dummy data
    }
    invitations.append(new_invitation)
    return jsonify({"invitation": new_invitation}), 201

@invitation_bp.route('/<int:invitation_id>/respond', methods=['POST'])
def respond_to_invitation(invitation_id):
    invitation = next((i for i in invitations if i["id"] == invitation_id), None)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404
    
    if not request.json or 'status' not in request.json:
        return jsonify({"error": "Status field required"}), 400
        
    status = request.json.get('status')
    if status not in ['accepted', 'declined']:
        return jsonify({"error": "Status must be 'accepted' or 'declined'"}), 400
        
    invitation['status'] = status
    return jsonify({"invitation": invitation})