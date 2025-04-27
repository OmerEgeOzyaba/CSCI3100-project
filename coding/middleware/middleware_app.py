from flask import Flask, jsonify, request
from dotenv import load_dotenv
from middleware_data_classes import create_database
from database import Database
from flask_jwt_extended import JWTManager
import os
import secrets
from datetime import timedelta
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import redis
from flask_cors import CORS

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.invitation_routes import invitation_bp
from routes.task_routes import task_bp
from routes.group_routes import group_bp

# loads properties.env
load_dotenv()

# create database
create_database()

app = Flask(__name__)

# More explicit CORS configuration
CORS(app, 
     resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
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




app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15) # expiration for short-lived JWTs
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7) # expiration for long-lived JWTs
jwt = JWTManager(app) # initialize JWT

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(invitation_bp, url_prefix='/api/invitations')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(group_bp, url_prefix='/api/groups')



# configure redis [FOR LOGOUT]
# TODO: might wanna change this to strict loading like JWT configuration (i.e. including configuration values in .env)
# TODO: commented everything Redis related out for now, decide on what to do based on team discussion
#redis_client = redis.Redis(
        #host = os.getenv("REDIS_HOST", "localhost"),
        #port = int(os.getenv("REDIS_PORT", 6379)),
        #db = int(os.getenv("REDIS_DB", 0)),
        #decode_responses = True
        #)

#try: 
    #redis_client.ping()
    #print("Redis connection successful")
#except redis.ConnectionError:
    #print("Redis connection failed - check if Redis server is running")
    #sys.exit(1)

# blacklist checker [FOR LOGOUT]
#@jwt.token_in_blocklist_loader
#def check_if_token_revoked(jwt_header, jwt_payload):
    #jti = jwt_payload["jti"]
    #return redis_client.exists(jti)

# dummy user database
# TODO: Instead of this, configure the real database
users = {"test@example.com":{"password": generate_password_hash("password123"), "global_roles":["user"]},
         "admin@example.com":{"password": generate_password_hash("admin123"), "global_roles":["super_admin","user"]}}

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

if __name__ == '__main__':
    # Get port from environment variable with default fallback to 5001
    port = int(os.getenv("SERVER_PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
