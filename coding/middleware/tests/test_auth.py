import pytest
from werkzeug.security import generate_password_hash
from ..middleware_data_classes import User
from .utils import mock_user, auth_header
from ..middleware_app import app as flask_app
from ..database import Database
from flask_jwt_extended import decode_token
from datetime import datetime, timezone

class TestAuthService:
    def test_login_success(self, auth_service, mocker):
        # Create a real User instance with hashed password
        
        mock_user = User(
            email="test@example.com",
            password=generate_password_hash("password"),
            created_at=datetime.now(timezone.utc)
        )
        
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = mock_user

        with flask_app.app_context():
            token, error = auth_service.login('test@example.com', 'password')
            assert token is not None
            assert error is None

    def test_login_failure(self, auth_service, mocker):
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = None
        with flask_app.app_context():
            token, error = auth_service.login('bad@example.com', 'wrong')
            assert not token and error

class TestAuthRoutes:
    def test_login_success(self, client, mocker):
        mock_user = User(
            email="test@example.com",
            password=generate_password_hash("password"),
            created_at=datetime.now(timezone.utc)
        )
        
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = mock_user

        response = client.post('/api/auth/login',
                            json={'email': 'test@example.com', 'password': 'password'},
                            content_type='application/json')
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        token = response.json['access_token']
        decoded = decode_token(token)
        assert decoded['sub'] == 'test@example.com'

    def test_login_failure(self, client, mocker):
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = None
        response = client.post('/api/auth/login',
                             json={'email': 'wrong@example.com', 'password': 'wrong'},
                             content_type='application/json')
        assert response.status_code == 401

    def test_logout_flow(self, client, test_user_token):
    # Directly use the pre-made token
        response = client.post('/api/auth/logout',
                         headers={'Authorization': f'Bearer {test_user_token}'})
        assert response.status_code == 200