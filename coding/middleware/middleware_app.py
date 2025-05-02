from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
from middleware_data_classes import create_database
from database import Database
from flask_jwt_extended import JWTManager, jwt_required
import os
import secrets
from datetime import timedelta
import sys
import redis
from flask_cors import CORS

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.invitation_routes import invitation_bp
from routes.task_routes import task_bp
from routes.group_routes import group_bp

from extensions import redis_client
from services.auth_service import AuthService
from services.user_service import UserService

# loads properties.env
load_dotenv()

# create database
create_database()

app = Flask(__name__)

# Configure CORS with more permissive settings
CORS(app, 
    resources={r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }},
    supports_credentials=True,
    automatic_options=True
)

# configure JWT in Flask
# setting up JWT_SECRET_KEY with safety checks and warnings
if os.getenv("FLASK_ENV") == "development":
    dev_key = os.getenv("JWT_SECRET_KEY")
    if not dev_key:
        print("\nDEVELOPMENT WARNING: Using temporary JWT key (invalid on restart)")
        print("     To fix: python3 generate_secret_key.py")
        dev_key = secrets.token_hex(32)
    app.config["JWT_SECRET_KEY"] = dev_key
else:
    try:
        app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
    except KeyError:
        print("\nPRODUCTION ERROR: JWT_SECRET_KEY environment variable missing!")
        print("     Generate with: python3 generate_secret_key.py")
        raise




app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7) # expiration for auth tokens
jwt = JWTManager(app) # initialize JWT

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(invitation_bp, url_prefix='/api/invites')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(group_bp, url_prefix='/api/groups')



# configure redis [configured in extensions.py]
# create AuthService object for the whole program
auth_service = AuthService(redis_client)
user_service = UserService()
app.extensions = getattr(app, "extensions", {})
app.extensions['auth_service'] = auth_service
app.extensions['user_service'] = user_service
@app.before_request
def before_request():
    g.auth_service = auth_service
    g.user_service = user_service


# blacklist checker [might not need it]
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return redis_client.exists(f"revoked:{jti}")


#=========================================================================
# global error handlers [FOR UNEXPECTED ERRORS]
@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "Internal server error"}), 500

#=========================================================================
# redis error handling
#@jwt.revoked_token_loader
#def handle_revoked_token(jwt_header, jwt_payload):
    #return jsonify({"error": "Token has been revoked"}), 401

#@jwt.invalid_token_loader
#def handle_invalid_token(error):
    #return jsonify({"error": "Invalid token"}), 401

#========================================================================= 

@app.route('/')
def index():
    return 'CULater API is running!'

#=========================================================================

# User endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    """Retrieve a list of users."""
    dummy_users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ]
    return jsonify(dummy_users), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieve a specific user by ID."""
    dummy_users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ]
    
    # Find the user with the matching ID
    user = next((usr for usr in dummy_users if usr["id"] == user_id), None)
    
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user), 200

# Invitation endpoints
@app.route('/api/invitations', methods=['GET'])
def get_invitations():
    """Retrieve a list of invitations."""
    dummy_invitations = [
        {"id": 1, "email": "invitee1@example.com", "status": "pending"},
        {"id": 2, "email": "invitee2@example.com", "status": "accepted"}
    ]
    return jsonify(dummy_invitations), 200

@app.route('/api/invitations/<int:invitation_id>', methods=['GET'])
def get_invitation(invitation_id):
    """Retrieve a specific invitation by ID."""
    dummy_invitations = [
        {"id": 1, "email": "invitee1@example.com", "status": "pending"},
        {"id": 2, "email": "invitee2@example.com", "status": "accepted"}
    ]
    
    # Find the invitation with the matching ID
    invitation = next((inv for inv in dummy_invitations if inv["id"] == invitation_id), None)
    
    if invitation is None:
        return jsonify({"error": "Invitation not found"}), 404
    
    return jsonify(invitation), 200

@app.route('/')
def health_check():
    return jsonify(
            status="running",
            service="auth",
            environment=os.getenv("FLASK_ENV", "development")
            )

# Debug
@app.after_request
def after_request(response):
    print(f"Response headers: {response.headers}")
    return response

#=========================================================================
# Task filtering by group
def get_tasks_by_group(user_email, group_id):
    """
    Retrieve tasks for a specific user and group.

    :param user_email: The email of the user.
    :param group_id: The ID of the group.
    :return: A list of tasks belonging to the user and group.
    """
    try:
        db = Database().get_session()

        # Verify the user is a member of the group with ACCEPTED status
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == user_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()

        if not membership:
            return []

        # Retrieve tasks for the user and group
        tasks = db.query(Task).filter(
            and_(
                Task.group_id == group_id,
                Task.assigned_to.contains(user_email)  # Assuming `assigned_to` is a list of emails
            )
        ).all()

        return tasks
    except Exception as e:
        current_app.logger.error(f"Error fetching tasks by group: {str(e)}")
        return []
    finally:
        db.close()

@app.route('/api/tasks/group/<int:group_id>', methods=['GET'])
@jwt_required()
def test_get_tasks_by_group(group_id):
    """
    Test endpoint for get_tasks_by_group function.
    """
    try:
        user_email = get_jwt_identity()  # Get the current user's email from the JWT
        tasks = get_tasks_by_group(user_email, group_id)
        return jsonify({"tasks": [task_to_dict(task) for task in tasks]}), 200
    except Exception as e:
        current_app.logger.error(f"Error in test_get_tasks_by_group: {str(e)}")
        return jsonify({"error": "Failed to fetch tasks"}), 500

if __name__ == '__main__':
    # Get port from environment variable with default fallback to 5001
    port = int(os.getenv("SERVER_PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

