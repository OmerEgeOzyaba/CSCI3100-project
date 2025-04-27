import jwt
import redis
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from functools import wraps

class AuthService:
    def __init__(self):
        self.redis = redis_conn
        self.auth_token = None
    def login(self, email, password):
        pass
    def logout(self):
        pass
    def authentiate_user(self): # REVISE ARGUMENTS
        pass
    def generate_token(self): # REVISE ARGUMENTS
        pass
    def validate_token(self): # REVISE ARGUMENTS
        pass
    def hash_password(self): # REVISE ARGUMENTS
        pass

