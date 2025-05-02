from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import (
        get_jwt_identity,
        get_jwt,
        jwt_required,
        verify_jwt_in_request
        )
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

# login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400

    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return {"error": "Missing email/password"}, 400

    
    auth_service = g.auth_service
    auth_token, error_msg= auth_service.login(email, password)
    if error_msg:
        return {"error": "Bad credentials"}, 401

    return jsonify({
            "auth_token": auth_token,
            "expires_in": int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()),
            "user": {"email": email}
            }), 200

# logout endpoint
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    auth_service = g.auth_service
    jti = get_jwt()["jti"] 
    logout_status = auth_service.logout(jti)
    if not logout_status: 
        return jsonify({"error": "Logout failed"}), 500
    return jsonify({"msg": "Logout successful"}), 200

# validate token endpoint [NOT SUPER NEEDED HONESTLY]
@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    return jsonify({
        "valid": True,
        "user": get_jwt_identity()
        }), 200

