import pytest
import redis
from datetime import timedelta
from middleware_app import app as flask_app
from database import Database
from flask_jwt_extended import create_access_token

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

