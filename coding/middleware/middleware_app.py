from flask import Flask, jsonify, request
from dotenv import load_dotenv
from middleware_data_classes import create_database
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import os
import secrets
from datetime import timedelta
import sys

# loads properties.env
load_dotenv()

# create database
create_database()

app = Flask(__name__)

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

# mock user database
users = {"test@example.com":{"password":"password123", "global_roles":["user"]},
         "admin@example.com":{"password":"admin123", "global_roles":["super_admin","user"]}}

# login endpoint
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return {"error": "Missing email/password"}, 400

    user = users.get(email)
    if not user or user["password"] != password:
        return {"error": "Bad credentials"}, 401

    # token generation
    access_token = create_access_token(identity=email, additional_claims={"global_roles": user["global_roles"]})
    # TODO: Database team to add is_super_admin column (to identify system admins who are kinda like super users)
    refresh_token = create_refresh_token(identity=email)

    return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"email": email, "global_roles": user["global_roles"]}
            }

# refresh endpoint
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims = get_jwt()
    new_token = create_access_token(identity=identity, additional_claims={"global_roles": claims.get("global_roles", [])})
    return {"access_token": new_token}

# protected endpoints
#       basic protected route
@app.route('/protected')
@jwt_required()
def protected():
    user = get_jwt_identity()
    return jsonify(logged_in_as=user)

#       system admin-only route
@app.route('/admin-only')
@jwt_required()
def admin_only():
    claims = get_jwt()
    if "super_admin" not in claims.get("global_roles", []):
        return {"error": "System admins only!"}, 403
    return {"secret_data": "Top secret admin info!"}

@app.route('/')
def dummy_endpoint():
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    app.run(debug=True)
