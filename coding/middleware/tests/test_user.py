import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

from ..services.user_service import UserService

class TestUserService:
    def test_create_user_success(self, user_service, mock_db_session):
        user_service.db.get_session.return_value.query.return_value.filter.return_value.first.return_value = None
        #mock_session = user_service.db.get_session.return_value
        mock_db_session.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = Mock(used_status=False)

        user, message = user_service.create_user(
                email="test@example.com",
                password="ValidPass123!",
                license_key="valid-license"
                )

        assert message == "Added new user"
        assert user.email == "test@example.com"
        mock_db_session.commit.assert_called_once()

    def test_create_user_invalid_email(self, user_service):
        user, message = user_service.create_user(
                email="invalid-email",
                password="ValidPass123!",
                license_key="valid-license")

        assert user is None
        assert message == "Invalid email format"

    def test_create_user_weak_password(self, user_service):
        user, message = user_service.create_user(
                email = "valid@example.com",
                password = "weak",
                license_key="valid-license")

        assert user is None
        assert "Password must be between 8-32 characters" in message
    def test_create_user_existing_email(self, user_service, mock_db_session):
        #mock_session = user_service.db.get_session.return_value
        mock_db_session.query.return_value.filter.return_value.first.return_value = Mock()

        user, message = user_service.create_user(
                email="existing@example.com",
                password="ValidPass123!",
                license_key="valid-license")

        assert user is None
        assert message == "Email already registered"

    def test_create_user_invalid_license(self, user_service, mock_db_session):
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None

        user, message = user_service.create_user(
                email="valid@example.com",
                password="ValidPass123!", 
                license_key="invalid-license")

        assert user is None
        assert message == "Invalid software license"

    def test_create_user_used_license(self, user_service, mock_db_session):
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = Mock(used_status = True)

        user, message = user_service.create_user(
                email="valid@example.com", 
                password="ValidPass123!",
                license_key="used-license")

        assert user is None
        assert message == "Software license already used"

    def test_create_user_database_error(self, user_service, mock_db_session):
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = Mock(used_status = False)
        mock_db_session.commit.side_effect = Exception("DB error")

        user, message = user_service.create_user(
                email="valid@example.com",
                password="ValidPass123!",
                license_key="valid-license")

        assert user is None
        assert "User registration failed" in message
        mock_db_session.rollback.assert_called_once()

class TestUserRoutes:
    def test_signup_options(self, client):
        response = client.options('/api/users/signup')
        assert response.status_code == 200

    def test_create_user_success(self, client, mocker, mock_user_data):
        mocker.patch(
                'services.user_service.UserService.create_user',
                return_value=(Mock(email=mock_user_data['email'],
                              created_at = datetime.now(timezone.utc)),
                              "Added new user")

                )
        response = client.post('/api/users/signup',
                               json=mock_user_data)

        assert response.status_code == 201
        assert response.json['user'] == mock_user_data['email']

    def test_create_user_missing_fields(self, client, mock_user_data):
        for field in ['email', 'password', 'licenseKey']:
            bad_data = mock_user_data.copy()
            bad_data.pop(field)

            response = client.post('/api/users/signup',
                                   json=bad_data)

            assert response.status_code == 400
            assert "Missing email/password/software license" in response.json['error']

    def test_create_user_invalid_json(self, client):
        response = client.post('/api/users/signup', 
                              data='not json',
                              headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        assert "Bad request" in response.json['error']

    def test_create_user_service_errors(self, client, mocker):
        mocker.patch(
                'routes.user_routes.UserService.create_user',
                return_value=(None, "Email already registered"))

        response = client.post('/api/users/signup', 
                               json={
                                   "email": "existing@example.com",
                                   "password":"ValidPass123!",
                                   "licenseKey":"valid-license"})
        assert response.status_code == 400
        assert "Email already registered" in response.json["error"]

        mocker.patch('routes.user_routes.UserService.create_user',
                     return_value=(None, "User registration failed: DB error"))
        response = client.post(
                '/api/users/signup',
                json={
                    "email":"test@example.com",
                    "password": "ValidPass123!",
                    "licenseKey": "valid-license"})
        assert response.status_code == 500
        assert "DB error" in response.json["error"]

