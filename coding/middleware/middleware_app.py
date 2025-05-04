from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
from middleware_data_classes import create_database
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
import secrets
from datetime import timedelta
from flask_cors import CORS
from extensions import redis_client
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.invitation_routes import invitation_bp
from routes.task_routes import task_bp
from routes.group_routes import group_bp
from services.auth_service import AuthService
from services.user_service import UserService

load_dotenv()
create_database()

app = Flask(__name__)

CORS(app, 
    resources={r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }},
    supports_credentials=True
)

if os.getenv("FLASK_ENV") == "development":
    dev_key = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    app.config["JWT_SECRET_KEY"] = dev_key
else:
    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(invitation_bp, url_prefix='/api/invites')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(group_bp, url_prefix='/api/groups')

auth_service = AuthService(redis_client)
user_service = UserService()
app.extensions['auth_service'] = auth_service
app.extensions['user_service'] = user_service

@app.before_request
def before_request():
    g.auth_service = app.extensions['auth_service']
    g.user_service = app.extensions['user_service']

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return redis_client.exists(f"revoked:{jti}")

@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@jwt.revoked_token_loader
def handle_revoked_token(jwt_header, jwt_payload):
    return jsonify({"error": "Token has been revoked"}), 401

@jwt.invalid_token_loader
def handle_invalid_token(error):
    return jsonify({"error": "Invalid token"}), 401

@app.route('/')
def index():
    return 'CULater API is running!'

if __name__ == '__main__':
    port = int(os.getenv("SERVER_PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)