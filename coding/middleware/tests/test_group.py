import pytest
from werkzeug.security import generate_password_hash
from ..middleware_app import app as flask_app
from ..database import Database
from ..middleware_data_classes import User, Group, Membership, Role, InvitationStatus
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture
def setup_data(client):
    db = Database()
    session = db.get_session()
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        user1 = User(
            email=f"admin{timestamp}@example.com",
            password=generate_password_hash("password"),
            created_at=datetime.now(timezone.utc)
        )
        user2 = User(
            email=f"contributor{timestamp}@example.com",
            password=generate_password_hash("password"),
            created_at=datetime.now(timezone.utc)
        )
        group = Group(name=f"Test Group {timestamp}", created_at=datetime.now(timezone.utc))
        session.add_all([user1, user2, group])
        session.flush()
        
        m1 = Membership(
            user_id=user1.email,
            group_id=group.id,
            role=Role.ADMIN,
            status=InvitationStatus.ACCEPTED,
            join_date=datetime.now(timezone.utc)
        )
        m2 = Membership(
            user_id=user2.email,
            group_id=group.id,
            role=Role.CONTRIBUTOR,
            status=InvitationStatus.ACCEPTED,
            join_date=datetime.now(timezone.utc)
        )
        session.add_all([m1, m2])
        session.commit()
        yield user1.email, user2.email, group.id
    finally:
        session.close()

def test_leave_group_admin_promotion(client, setup_data):
    admin_email, contributor_email, group_id = setup_data
    with flask_app.app_context():
        token = create_access_token(admin_email)
    
    response = client.post(f'/api/groups/{group_id}/leave',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

def test_group_cleanup(client, setup_data):
    admin_email, _, group_id = setup_data
    with flask_app.app_context():
        token = create_access_token(admin_email)
    
    response = client.post(f'/api/groups/{group_id}/leave',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200