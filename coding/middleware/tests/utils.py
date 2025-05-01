from flask import json
from werkzeug.security import generate_password_hash
from database import Database

############# AUTH RELATED #############

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

############# USER RELATED #############

def create_user_payload(email='test@example.com', password='ValidPass123!', license_key='test-license'):
    return {
            'email' : email,
            'password' : password,
            'licenseKey': license_key
            }

def assert_user_response(response, expected_email):
    assert response.status_code == 201
    assert 'user' in response.json
    assert 'created_at' in response.json
    assert response.json['user'] == expected_email

