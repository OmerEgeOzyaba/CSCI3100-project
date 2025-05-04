import pytest
import redis
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from unittest.mock import Mock

from ..middleware_app import app as flask_app
from ..database import Database
from ..services.user_service import UserService
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session')
def test_app():
    flask_app.config.update({
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-secret-123',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=5),
        'REDIS_DB': 15,
        'JWT_TOKEN_LOCATION': ['headers', 'json'],
        'JWT_JSON_KEY': 'access_token',
    })
    test_redis = redis.Redis(db=flask_app.config['REDIS_DB'])
    flask_app.config['REDIS_CLIENT'] = test_redis
    yield flask_app
    test_redis.flushdb()
    test_redis.close()

@pytest.fixture
def client(test_app):
    with test_app.test_client() as client:
        yield client

@pytest.fixture
def auth_service(test_app):
    with test_app.app_context():
        return test_app.extensions['auth_service']

@pytest.fixture
def test_user_token(test_app):
    with test_app.app_context():
        return create_access_token('test@example.com')

@pytest.fixture
def mock_db_session(mock_database):
    session = mock_database.get_session.return_value
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None
    return session

@pytest.fixture
def mock_database(mocker):
    mock_db = mocker.MagicMock()
    mock_session = mocker.MagicMock()
    mock_db.get_session.return_value = mock_session
    return mock_db

@pytest.fixture
def user_service(test_app, mock_database):
    with test_app.app_context():
        service = UserService()
        service.db = mock_database
        return service

@pytest.fixture
def mock_user_data():
    return {
        "email": "test@example.com",
        "password": "ValidPass123!",
        "licenseKey": "test-license-123"
    }

@pytest.fixture
def created_user(user_service, mock_db_session):
    mock_user = Mock(
        email="existing@example.com",
        created_at=datetime.now(timezone.utc),
        password=generate_password_hash("ValidPass123!")
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user