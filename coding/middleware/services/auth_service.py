import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional, Tuple

import jwt
import redis
from flask import current_app
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from database import Database
from middleware_data_classes import User


class AuthService:
    def __init__(self, redis_conn: redis.Redis):
        self.redis = redis_conn
        self.db = Database()

    def login(self, email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
        """Authenticate user and return JWT tokens."""
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            
            if not user or not check_password_hash(user.password, password):
                current_app.logger.warning(f"Login attempt failed for email: {email}")
                return None, "Invalid credentials"

            # Generate JWT with unique identifier
            jti = str(uuid.uuid4())
            auth_token = create_access_token(
                identity=email,
                additional_claims={"jti": jti}  # Remove role from claims
            )

            current_app.logger.info(f"User {email} logged in successfully")
            return auth_token, None
            
        except Exception as e:
            current_app.logger.error(f"Login error for {email}: {str(e)}", exc_info=True)
            return None, "Authentication service unavailable"
        finally:
            session.close()

    def logout(self, jti: str) -> bool:
        """Revoke JWT token by adding to redis deny list."""
        try:
            # Get token expiration from claims
            claims = get_jwt()
            exp_timestamp = claims["exp"]
            now = datetime.now(timezone.utc).timestamp()
            expires_in = exp_timestamp - now

            if expires_in > 0:
                self.redis.setex(f"revoked:{jti}", int(expires_in), "revoked")
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f"Logout error: {str(e)}", exc_info=True)
            return False

    def verify_token(self, token: str) -> bool:
        """Check if token is valid and not revoked."""
        try:
            claims = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            jti = claims["jti"]
            return not self.redis.exists(f"revoked:{jti}")
        except jwt.PyJWTError as e:
            current_app.logger.warning(f"Invalid token: {str(e)}")
            return False
        except Exception as e:
            current_app.logger.error(f"Token verification error: {str(e)}")
            return False

    @staticmethod
    def get_current_user() -> Optional[User]:
        """Retrieve current authenticated user from database."""
        session = Database().get_session()
        try:
            email = get_jwt_identity()
            return session.query(User).filter(User.email == email).first()
        except Exception as e:
            current_app.logger.error(f"Failed to fetch current user: {str(e)}")
            return None
        finally:
            session.close()

# Optional decorator for role-based access control
def roles_required(*required_roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role", "guest")
            
            if user_role not in required_roles:
                return {"error": "Insufficient permissions"}, 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper