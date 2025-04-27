from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
        create_access_token,
        create_refresh_token,
        get_jwt_identity,
        get_jwt,
        jwt_required
        )
from werkzeug.security import check_password_hash

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

@auth_bp.route('/signup', methods=['POST'])
def signup():
    # TODO
    return jsonify({"msg": "Signup successful"}), 201

# logout endpoint
# TODO: For delevopment purposes, no need to use Redis, commented out parts that use Redis.
#       decide on what to do based on team discussion.

@auth_bp.route('/logout', methods=['POST'])
# TODO comment for testing
# @jwt_required()
def logout():
    # jti = get_jwt()["jti"]
    # redis_client.set(jti, "revoked", ex=app.config["JWT_REFRESH_TOKEN_EXPIRES"]) # TODO: change here if team decided to exclude refreshing
    return jsonify({"msg": "Logout successful"}), 200

# validate token endpoint
@auth_bp.route('/validate-token', methods=['GET'])
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

@auth_bp.route('/refresh', methods=['POST'])
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
@auth_bp.route('/protected')
@jwt_required()
def protected():
    user = get_jwt_identity()
    return jsonify(logged_in_as=user)

#       system admin-only route
@auth_bp.route('/admin-only')
@jwt_required()
def admin_only():
    claims = get_jwt()
    if "super_admin" not in claims.get("global_roles", []):
        return {"error": "System admins only!"}, 403
    return {"secret_data": "Top secret admin info!"}


