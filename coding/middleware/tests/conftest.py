import pytest
import redis
from datetime import timedelta
from middleware_app import app as flask_app
from database import Database
from flask_jwt_extended import create_access_token
from unittest.mock import Mock
from services.user_service import UserService

############# AUTH RELATED #############

@pytest.fixture(scope='session')
def test_app():
    """ Central app configuration for all tests"""
    flask_app.config.update({
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-secret-123',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=5),
        'REDIS_DB': 15
        })

    test_redis = redis.Redis(db=flask_app.config['REDIS_DB'])
    flask_app.config['REDIS_CLIENT'] = test_redis

    yield flask_app

    test_redis.flushdb
    test_redis.close()

@pytest.fixture
def client(test_app):
    """Test client fixture"""
    with test_app.test_client() as client:
        yield client

@pytest.fixture
def auth_service(test_app):
    """Central access to auth service"""
    with test_app.app_context():
        return test_app.extensions['auth_service']

@pytest.fixture
def test_user_token(test_app):
    """Pre-made valid JWT"""
    with test_app.app_context():
        return create_access_token('test@example.com')

############# USER RELATED #############

@pytest.fixture
def mock_db_session(mock_database):
    """Mock database session fixture"""
    session = mock_database.get_session.return_value
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None
    return session

@pytest.fixture
def mock_database(mocker):
    """Mock Database class fixture"""
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
    return {"email": "test@example.com",
            "password" : "ValidPass123!",
            "licenseKey": "test-license-123"}

@pytest.fixture
def created_user(user_service, mock_db_session):
    mock_user = Mock(email = "existing@example.com",
                     created_at=datetime.utcnow(),
                     password=generate_password_hash("ValidPass123!"))
    mock_db_session.query.return_value.felter.return_value.first.return_value = mock_user
    return mock_user
