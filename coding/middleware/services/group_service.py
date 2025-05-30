from database import Database
from middleware_data_classes import Group, Membership, Task, Role, InvitationStatus
from sqlalchemy import and_
from datetime import datetime
import random
from sqlalchemy.orm import joinedload


class GroupService:
    def __init__(self):
        self.db = Database()

    def get_groups(self, user_email):
        session = self.db.get_session()
        try:
            memberships = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.status == InvitationStatus.ACCEPTED
                )
            ).all()
            group_ids = [m.group_id for m in memberships]
            groups = session.query(Group).filter(Group.id.in_(group_ids)).all()
            return groups
        finally:
            session.close()

    def get_group(self, user_email, group_id):
        session = self.db.get_session()
        try:
            # Check if the user is a member of the group
            membership = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == group_id,
                    Membership.status == InvitationStatus.ACCEPTED
                )
            ).first()
            if not membership:
                return None
            # Fetch the group with its memberships eagerly loaded
            group = session.query(Group).options(joinedload(Group.memberships)).filter(Group.id == group_id).first()
            return group
        finally:
            session.close()

    def create_group(self, user_email, name, description):
        session = self.db.get_session()
        try:
            new_group = Group(
                name=name,
                description=description,
                created_at=datetime.utcnow()
            )
            session.add(new_group)
            session.flush()
            membership = Membership(
                user_id=user_email,
                group_id=new_group.id,
                role=Role.ADMIN,
                status=InvitationStatus.ACCEPTED,
                join_date=datetime.utcnow()
            )
            session.add(membership)
            session.commit()
            # Force loading of memberships before session closes
            _ = new_group.memberships
            return new_group
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def update_group(self, user_email, group_id, name=None, description=None):
        session = self.db.get_session()
        try:
            # Find the group
            group = session.query(Group).filter(Group.id == group_id).first()
            if not group:
                raise ValueError("Group not found")

            # Verify admin permissions
            membership = session.query(Membership).filter(
                Membership.user_id == user_email,
                Membership.group_id == group_id,
                Membership.status == 'ACCEPTED',
                Membership.role == 'ADMIN'
            ).first()
            if not membership:
                raise PermissionError("Only admins can update group details")

            # Update group attributes
            if name:
                group.name = name
            if description:
                group.description = description

            # Commit the changes
            session.commit()

            # Serialize the group data into a dictionary
            group_data = {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at.isoformat() if hasattr(group.created_at, 'isoformat') else str(group.created_at)
            }
            return group_data

        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def leave_group(self, user_email, group_id):
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
                raise ValueError("Not a member of this group")
            
            # Check if last admin
            if membership.role == Role.ADMIN:
                other_admins = session.query(Membership).filter(
                    and_(
                        Membership.group_id == group_id,
                        Membership.role == Role.ADMIN,
                        Membership.user_id != user_email,
                        Membership.status == InvitationStatus.ACCEPTED
                    )
                ).count()
                if other_admins == 0:
                    contributors = session.query(Membership).filter(
                        and_(
                            Membership.group_id == group_id,
                            Membership.role == Role.CONTRIBUTOR,
                            Membership.status == InvitationStatus.ACCEPTED
                        )
                    ).all()
                    if contributors:
                        new_admin = random.choice(contributors)
                        new_admin.role = Role.ADMIN
                    else:
                        readers = session.query(Membership).filter(
                            and_(
                                Membership.group_id == group_id,
                                Membership.role == Role.READER,
                                Membership.status == InvitationStatus.ACCEPTED
                            )
                        ).all()
                        if readers:
                            new_admin = random.choice(readers)
                            new_admin.role = Role.ADMIN
            
            session.delete(membership)
            remaining_members = session.query(Membership).filter(
                and_(
                    Membership.group_id == group_id,
                    Membership.status == InvitationStatus.ACCEPTED
                )
            ).count()
            if remaining_members == 0:
                session.query(Task).filter(Task.group_id == group_id).delete()
                session.query(Membership).filter(
                    and_(
                        Membership.group_id == group_id,
                        Membership.status == InvitationStatus.SENT
                    )
                ).delete()
                group = session.query(Group).filter(Group.id == group_id).first()
                session.delete(group)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()