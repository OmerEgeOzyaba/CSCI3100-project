from database import Database
from middleware_data_classes import Task, Membership, Role, InvitationStatus
from sqlalchemy import and_
from datetime import datetime

class TaskService:
    def __init__(self):
        self.db = Database()

    def get_tasks_for_user(self, user_email):
        session = self.db.get_session()
        try:
            memberships = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.status == InvitationStatus.ACCEPTED
                )
            ).all()
            group_ids = [m.group_id for m in memberships]
            tasks = session.query(Task).filter(Task.group_id.in_(group_ids)).all()
            return tasks
        finally:
            session.close()

    def get_tasks_for_group(self, user_email, group_id):
        session = self.db.get_session()
        try:
            membership = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == group_id,
                    Membership.status == InvitationStatus.ACCEPTED
                )
            ).first()
            if not membership:
                return []
            tasks = session.query(Task).filter(Task.group_id == group_id).all()
            return tasks
        finally:
            session.close()

    def get_task(self, user_email, task_id):
        session = self.db.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            membership = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == task.group_id,
                    Membership.status == InvitationStatus.ACCEPTED
                )
            ).first()
            if not membership:
                return None
            task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "status": "completed" if task.status else "pending",
                "group_id": task.group_id
            }
            return task_data
        finally:
            session.close()

    def create_task(self, user_email, title, description, group_id, due_date):
        session = self.db.get_session()
        try:
            membership = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == group_id,
                    Membership.status == InvitationStatus.ACCEPTED,
                    Membership.role.in_([Role.CONTRIBUTOR, Role.ADMIN])
                )
            ).first()
            if not membership:
                raise PermissionError("Insufficient permissions to create tasks in this group")
            new_task = Task(
                title=title,
                description=description,
                group_id=group_id,
                created_at=datetime.utcnow(),
                due_date=due_date,
                status=False
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)
            return new_task
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def update_task(self, user_email, task_id, title=None, description=None, due_date=None, status=None):
        session = self.db.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise ValueError("Task not found")
            membership = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == task.group_id,
                    Membership.status == InvitationStatus.ACCEPTED,
                    Membership.role.in_([Role.CONTRIBUTOR, Role.ADMIN])
                )
            ).first()
            if not membership:
                raise PermissionError("Insufficient permissions to update tasks in this group")
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if due_date is not None:
                task.due_date = due_date
            if status is not None:
                task.status = status
            session.commit()
            # Serialize task data into a dictionary before closing the session
            task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "status": "completed" if task.status else "pending",
                "group_id": task.group_id
            }
            return task_data
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_task(self, user_email, task_id):
        session = self.db.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise ValueError("Task not found")
            membership = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == task.group_id,
                    Membership.status == InvitationStatus.ACCEPTED,
                    Membership.role.in_([Role.CONTRIBUTOR, Role.ADMIN])
                )
            ).first()
            if not membership:
                raise PermissionError("Insufficient permissions to delete tasks in this group")
            session.delete(task)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()