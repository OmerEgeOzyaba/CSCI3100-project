import jwt
import redis
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from functools import wraps
from middleware.middleware_data_classes import User
from sqlalchemy.orm import Session
from database import Database
import os
from flask_jwt_extended import (
        create_access_token,
        create_refresh_token,
        get_jwt_identity,
        get_jwt,
        jwt_required
        )
import uuid

class AuthService:
    def __init__(self, redis_conn):
        self.redis = redis_conn
    def login(self, email, password): # Return a tuple of access/refresh tokens, return none if login unsuccessful
        db = Database().get_session()

        user = db.query(User).filter(User.email == email).first()
        if not user or not check_password_hash(user.get_password(), password):
            return None, "Invalid credentials"

        # Generate JWTs
        jti = str(uuid.uuid4()) # Generates unique id for refresh token
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email, additional_claims={"jti":jti})

        return access_token, refresh_token

    def logout(self, jti):
        token_expiration = timedelta(days=current_app.config["JWT_REFRESH_TOKEN_EXPIRES"])
        self.redis.setex(f"refresh_token_jti:{jti}", token_expiration, "revoked")
    def authentiate_user(self): # REVISE ARGUMENTS, maybe this can be for the group permissions and stuff
        pass
    def refresh_access_token(self, refresh_token):
        refresh_is_valid, decoded_refresh_t = self.validate_refresh_token(refresh_token)
        if refresh_is_valid:
            identity = decoded_refresh_t.get("identity")
            if not identity:
                return None, "Invalid refresh token"
            new_access_token = create_access_token(identity=identity)
            return new_access_token, None

    def validate_access_token(self, token): # REVISE ARGUMENTS, this is to validate the
        jwt_key = os.getenv("JWT_SECRET_KEY")
        try:
            decoded_token = jwt.decode(token, jwt_key, algorithms=["HS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:
            return "error: token expired"
        except jwt.InvalidTokenError:
            return "invalid token"
    def validate_refresh_token(self, token):
        jwt_key = os.getenv("JWT_SECRET_KEY")
        try: 
            decoded_token = jwt.decode(token, jwt_key, algorithms=["HS256"])
            jti = decoded_token.get("jti")
            if not jti:
                return False, "Refresh token missing JTI"

            if self.redis.get(f"refresh_token_jti:{jti}"):
                return False, "Refresh token revoked"

            return True, decoded_token
        except jwt.ExpiredSignatureError:
            return False, "Refresh token expired"
        except jwt.InvalidTokenError:
            return False, "Invalid refresh token"

    def hash_password(self): # REVISE ARGUMENTS
        pass

