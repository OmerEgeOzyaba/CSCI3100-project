import jwt
import redis
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from flask import current_app
from functools import wraps
from middleware_data_classes import User
from sqlalchemy.orm import Session
from database import Database
import os
from flask_jwt_extended import (
        create_access_token,
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
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not check_password_hash(user.get_password(), password):
                return None, "Invalid credentials"

            # Generate JWTs
            jti = str(uuid.uuid4()) # Generates unique id for refresh token
            auth_token = create_access_token(identity=email, additional_claims={"jti":jti})

            return auth_token, None
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return None, "Login failed"
        finally:
            db.close()

    def logout(self, jti):
        try:
            token_expiration = timedelta(days=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds())
            self.redis.setex(f"revoked:{jti}", token_expiration, "")
            return True
        except Exception as e:
            current_app.logger.error(f"Logout error: {str(e)}")
            return False

