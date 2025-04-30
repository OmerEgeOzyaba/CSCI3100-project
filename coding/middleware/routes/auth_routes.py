from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import (
        get_jwt_identity,
        get_jwt,
        jwt_required,
        verify_jwt_in_request
        )
from services.auth_service import AuthService
from middleware_data_classes import User
from database import Database
from werkzeug.security import generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Handle OPTIONS request for signup
@auth_bp.route('/signup', methods=['OPTIONS'])
def handle_signup_options():
    return '', 200

# Handle OPTIONS request for logout
@auth_bp.route('/logout', methods=['OPTIONS'])
def handle_logout_options():
    return '', 200

# Signup endpoint
@auth_bp.route('/signup', methods=['POST'])
def signup():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    email = request.json.get("email")
    password = request.json.get("password")
    license_key = request.json.get("licenseKey")

    if not email or not password or not license_key:
        return jsonify({"error": "Missing required fields"}), 400

    # Validate email format
    if not '@' in email or not '.' in email:
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password length
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    db = Database().get_session()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409

        # Create new user with current timestamp
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            license_key=license_key,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        
        return jsonify({
            "msg": "User registered successfully",
            "user": {"email": email}
        }), 201

    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500
    finally:
        db.close()

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
            "access_token": auth_token,
            "expires_in": int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()),
            "user": {"email": email},
            "token_type": "access"
            }), 200

# logout endpoint
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        auth_service = g.auth_service
        jwt_data = get_jwt()
        jti = jwt_data["jti"]
        token_type = jwt_data["type"]
        
        if token_type != "access":
            return jsonify({"error": "Invalid token type"}), 422
            
        logout_status = auth_service.logout(jti)
        if not logout_status:
            return jsonify({"error": "Logout failed"}), 500
        return jsonify({"msg": "Logout successful"}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"error": "Logout failed"}), 500

# validate token endpoint [NOT SUPER NEEDED HONESTLY]
@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    return jsonify({
        "valid": True,
        "user": get_jwt_identity()
        }), 200

