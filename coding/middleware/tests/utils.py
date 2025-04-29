from flask import json
from werkzeug.security import generate_password_hash
from database import Database

def mock_user(mocker, email='test@example.com', password='password'):
    """Central mock user generator"""
    mock_user = mocker.Mock()
    mock_user.email = email
    mock_user.get_password.return_value = generate_password_hash(password)
    return mock_user

def auth_header(token):
    """Standard auth header formatter"""
    return {'Authorization': f'Bearer {token}'}

def assert_token_revoked(redis_client, jti):
    assert redis_client.exists(f"revoked:{jti}") == 1

