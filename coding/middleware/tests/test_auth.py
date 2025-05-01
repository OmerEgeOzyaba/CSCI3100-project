import pytest
from tests.utils import mock_user, auth_header
from middleware_app import app as flask_app
from database import Database
from flask_jwt_extended import decode_token

class TestAuthService:
    def test_login_success(self, auth_service, mocker):
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = mock_user(mocker)
        with flask_app.app_context():
            token, error = auth_service.login('test@example.com', 'password')
            assert token and not error

    def test_login_failure(self, auth_service, mocker):
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = None
        with flask_app.app_context():
            token, error = auth_service.login('bad@example.com', 'wrong')
            assert not token and error

class TestAuthRoutes:
    def test_login_success(self, client, mocker):
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = mock_user(mocker)
        response = client.post('/api/auth/login', 
                               json={'email':'test@example.com', 'password':'password'}, 
                               content_type = 'application/json')

        assert response.status_code == 200
        assert 'access_token' in response.json
        assert response.json['user']['email'] == 'test@example.com'

        token = response.json['access_token']
        decoded = decode_token(token)
        assert decoded['sub'] == 'test@example.com'
        assert 'jti' in decoded
        assert decoded['type'] == 'access'

    def test_login_failure(self, client, mocker):
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = None

        response = client.post('/api/auth/login', 
                               json={'email':'wrong@example.com', 'password':'wrong'}, 
                               content_type = 'application/json')

        assert response.status_code == 401
        assert response.json == {"error": "Bad credentials"}

    def test_logout_flow(self, client, auth_service, mocker):
        mocker.patch.object(Database, 'get_session').return_value.query.return_value.filter.return_value.first.return_value = mock_user(mocker)

        login_res = client.post('/api/auth/login',
                                json = {'email':'test@example.com', 'password':'password'})

        token = login_res.json['access_token']
        jti = decode_token(token)['jti']

        logout_res = client.post('/api/auth/logout', 
                                 headers={'Authorization': f'Bearer {token}'})

        assert logout_res.status_code == 200
        assert logout_res.json == {"msg":"Logout successful"}
        assert auth_service.redis.exists(f"revoked:{jti}") == 1       
