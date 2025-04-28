from flask import Blueprint, jsonify, request

user_bp = Blueprint('users', __name__)

# Dummy data
users = [
    {"username": "john_doe", "email": "john@example.com", "name": "John Doe"},
    {"username": "jane_smith", "email": "jane@example.com", "name": "Jane Smith"},
    {"username": "sam_wong", "email": "sam@example.com", "name": "Sam Wong"}
]

@user_bp.route('/', methods=['GET'])
def get_users():
    return jsonify({"users": users})

@user_bp.route('/<string:username>', methods=['GET'])
def get_user(username):
    user = next((user for user in users if user["username"] == username), None)
    if user:
        return jsonify({"user": user})
    return jsonify({"error": "User not found"}), 404

@user_bp.route('/', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    new_user = {
        "username": request.json.get('username'),
        "email": request.json.get('email'),
        "name": request.json.get('name')
    }
    users.append(new_user)
    return jsonify({"user": new_user}), 201