import pytest
from werkzeug.security import generate_password_hash
from ..middleware_app import app as flask_app
from ..database import Database
from ..middleware_data_classes import User, Group, Membership, Role, InvitationStatus
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone

@pytest.fixture
def setup_data(client):
    db = Database()
    session = db.get_session()
    try:
        user1 = User(
            email="inviter@example.com",
            password=generate_password_hash("password"),
            created_at=datetime.now(timezone.utc)
        )
        user2 = User(
            email="invitee@example.com",
            password=generate_password_hash("password"),
            created_at=datetime.now(timezone.utc)
        )
        group = Group(name="Test Group", created_at=datetime.now(timezone.utc))
        session.add_all([user1, user2, group])
        session.flush()
        
        membership = Membership(
            user_id=user1.email,
            group_id=group.id,
            role=Role.ADMIN,
            status=InvitationStatus.ACCEPTED,
            join_date=datetime.now(timezone.utc)
        )
        session.add(membership)
        session.commit()
        return user1.email, user2.email, group.id
    finally:
        session.close()

def test_send_invitation(client, setup_data):
    inviter_email, invitee_email, group_id = setup_data
    with flask_app.app_context():
        token = create_access_token(inviter_email)
    
    response = client.post('/api/invites/send',
                         json={"email": invitee_email, "group_id": group_id},
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201