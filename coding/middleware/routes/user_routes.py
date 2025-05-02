from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import (
        get_jwt_identity,
        get_jwt,
        jwt_required,
        verify_jwt_in_request
        )
from services.user_service import UserService

user_bp = Blueprint('users', __name__)

# Dummy data
users = [
    {"username": "john_doe", "email": "john@example.com", "name": "John Doe"},
    {"username": "jane_smith", "email": "jane@example.com", "name": "Jane Smith"},
    {"username": "sam_wong", "email": "sam@example.com", "name": "Sam Wong"}
]

# Handle OPTIONS request for signup
@user_bp.route('/signup', methods=['OPTIONS'])
def handle_signup_options():
    return '', 200

####################################################
# TODO: THESE WORK WITH DUMMY DATA, WILL PROLLY REMOVE

@user_bp.route('/', methods=['GET'])
def get_users():
    return jsonify({"users": users})

@user_bp.route('/<string:username>', methods=['GET'])
def get_user(username):
    user = next((user for user in users if user["username"] == username), None)
    if user:
        return jsonify({"user": user})
    return jsonify({"error": "User not found"}), 404
####################################################

@user_bp.route('/signup', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400

    email = request.json.get("email")
    password = request.json.get("password")
    license_key = request.json.get("licenseKey")
    
    if not email or not password or not license_key:
        return {"error": "Missing email/password/software license"}, 400

    user_service = g.user_service
    new_user, error = user_service.create_user(email, password, license_key)

    if not new_user:
        if "User registration failed" in error:
            current_app.logger.error(f"{error}")
            return jsonify({"error": error}), 500
        return jsonify({"error": error}), 400

    email = new_user.email
    created_at = new_user.created_at
    return jsonify({"user": email,
                    "created_at": created_at}), 201

