from flask import Flask, jsonify, request
from dotenv import load_dotenv
from middleware_data_classes import create_database
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import os
import secrets
from datetime import timedelta
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import redis
from flask_cors import CORS

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
     resources={r"/api/*": {"origins": "http://localhost:5173"}},
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

# login endpoint

@app.route('/')
def index():
    return 'CULater API is running!'

@app.route('/api/auth/login', methods=['POST'])
def login():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400

    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return {"error": "Missing email/password"}, 400

    user = users.get(email)
    if not user or not check_password_hash(user["password"], password):
        return {"error": "Bad credentials"}, 401

    # token generation
    access_token = create_access_token(identity=email, additional_claims={"global_roles": user["global_roles"]})
    # TODO: Database team to add is_super_admin column (to identify system admins who are kinda like super users)
    # TODO: Used global_roles to make sure it isnt confused by group-specific roles in the future, if this won't 
    #       be an issue, replace all occurances of "global_roles" by "roles" as specified in documentation, otherwise
    #       update documentation, also change "super_admin" to "admin" depending on team decision
    refresh_token = create_refresh_token(identity=email)

    return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"email": email, "global_roles": user["global_roles"]}
            }), 200

# logout endpoint
# TODO: For delevopment purposes, no need to use Redis, commented out parts that use Redis.
#       decide on what to do based on team discussion.
@app.route('/api/auth/logout', methods=['DELETE'])
@jwt_required()
def logout():
    # jti = get_jwt()["jti"]
    # redis_client.set(jti, "revoked", ex=app.config["JWT_REFRESH_TOKEN_EXPIRES"]) # TODO: change here if team decided to exclude refreshing
    return jsonify({"msg": "Logout successful"}), 200

# validate token endpoint
@app.route('/api/auth/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    return jsonify({
        "valid": True,
        "user": get_jwt_identity(),
        "global_roles": get_jwt().get("global_roles", [])
        }), 200

#=========================================================================
# refresh endpoint [NOT SPECIFIED IN DOCUMENTATION BUT GOOD SECURITY PRACTICE]
# TODO: Either remove this endpoint and only generate long-lasting access tokens
#       or add this endpoint to the documentation
@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        claims = get_jwt()
        new_token = create_access_token(identity=identity, additional_claims={"global_roles": claims.get("global_roles", [])})
        return jsonify({"access_token": new_token}), 200
    except Exception as e:
        return jsonify({"error": "Token refresh failed"}), 500

#=========================================================================

#=========================================================================
# protected endpoints [FOR DEVELOPING/TESTING, NOT IN PRODUCTION]
#=========================================================================
#       basic protected route
@app.route('/api/auth/protected')
@jwt_required()
def protected():
    user = get_jwt_identity()
    return jsonify(logged_in_as=user)

#       system admin-only route
@app.route('/api/auth/admin-only')
@jwt_required()
def admin_only():
    claims = get_jwt()
    if "super_admin" not in claims.get("global_roles", []):
        return {"error": "System admins only!"}, 403
    return {"secret_data": "Top secret admin info!"}

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