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
# Signup endpoint
#@auth_bp.route('/signup', methods=['POST'])
#def signup():
    #if not request.is_json:
        #return jsonify({"error": "Request must be JSON"}), 400

    #email = request.json.get("email")
    #password = request.json.get("password")
    #license_key = request.json.get("licenseKey")

    #if not email or not password or not license_key:
        #return jsonify({"error": "Missing required fields"}), 400

    # Validate email format
    #if not '@' in email or not '.' in email:
        #return jsonify({"error": "Invalid email format"}), 400

    # Validate password length
    #if len(password) < 8:
        #return jsonify({"error": "Password must be at least 8 characters"}), 400

    #db = Database().get_session()
    #try:
        # Check if user already exists
        #existing_user = db.query(User).filter(User.email == email).first()
        #if existing_user:
            #return jsonify({"error": "Email already registered"}), 409

        # Create new user with current timestamp
        #new_user = User(
            #email=email,
            #password=generate_password_hash(password),
            #license_key=license_key,
            #created_at=datetime.utcnow()
        #)
        
        #db.add(new_user)
        #db.commit()
        
        #return jsonify({
            #"msg": "User registered successfully",
            #"user": {"email": email}
        #}), 201

    #except Exception as e:
        #db.rollback()
        #current_app.logger.error(f"Signup error: {str(e)}")
        #return jsonify({"error": "Registration failed"}), 500
    #finally:
        #db.close()

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

