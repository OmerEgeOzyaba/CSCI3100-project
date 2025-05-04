import pytest
from werkzeug.security import generate_password_hash
from ..middleware_app import app as flask_app
from ..database import Database
from ..middleware_data_classes import User, Group, Membership, Task, Role, InvitationStatus
from datetime import datetime, timezone

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            db = Database()
            session = db.get_session()
            session.query(Task).delete()
            session.query(Membership).delete()
            session.query(Group).delete()
            session.query(User).delete()
            session.commit()
            session.close()
        yield client

@pytest.fixture
def setup_data(client):
    db = Database()
    session = db.get_session()
    try:
        user = User(
            email="test@example.com",
            password=generate_password_hash("password"),
            created_at=datetime.now(timezone.utc),
        )
        group = Group(name="Test Group", created_at=datetime.now(timezone.utc))
        session.add(user)
        session.add(group)
        session.flush()
        
        membership = Membership(
            user_id=user.email,
            group_id=group.id,
            role=Role.CONTRIBUTOR,
            status=InvitationStatus.ACCEPTED,
            join_date=datetime.now(timezone.utc)
        )
        task = Task(
            title="Test Task",
            group_id=group.id,
            created_at=datetime.now(timezone.utc),
            status=False
        )
        session.add(membership)
        session.add(task)
        session.commit()
        return user.email, group.id, task.id
    finally:
        session.close()

def test_create_task_role_check(client, setup_data, test_user_token):
    user_email, group_id, _ = setup_data
    db = Database()
    session = db.get_session()
    membership = session.query(Membership).filter(Membership.user_id == user_email).first()
    membership.role = Role.READER
    session.commit()
    session.close()

    response = client.post('/api/tasks/',
                         json={"title": "New Task", "group_id": group_id},
                         headers={'Authorization': f'Bearer {test_user_token}'})
    assert response.status_code == 403

def test_get_tasks_by_group(client, setup_data, test_user_token):
    user_email, group_id, _ = setup_data
    response = client.get(f'/api/tasks/group/{group_id}',
                        headers={'Authorization': f'Bearer {test_user_token}'})
    assert response.status_code == 200
    assert len(response.json["tasks"]) == 1