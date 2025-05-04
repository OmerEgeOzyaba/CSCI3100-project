from database import Database
from middleware_data_classes import Membership, Role, InvitationStatus
from sqlalchemy import and_
from datetime import datetime, timezone  # Add this import

class MembershipService:
    def __init__(self):
        self.db = Database()

    def get_invitations(self, user_email):
        session = self.db.get_session()
        try:
            invitations = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.status == InvitationStatus.SENT
                )
            ).all()
            return invitations
        finally:
            session.close()

    def send_invitation(self, inviter_email, member_email, group_id, role=Role.READER):
        session = self.db.get_session()
        try:
            inviter_membership = session.query(Membership).filter(
                and_(
                    Membership.user_id == inviter_email,
                    Membership.group_id == group_id,
                    Membership.status == InvitationStatus.ACCEPTED,
                    Membership.role.in_([Role.ADMIN, Role.CONTRIBUTOR])
                )
            ).first()
            if not inviter_membership:
                raise PermissionError("Insufficient permissions to send invitations")
            existing = session.query(Membership).filter(
                and_(
                    Membership.user_id == member_email,
                    Membership.group_id == group_id
                )
            ).first()
            if existing and existing.status in [InvitationStatus.ACCEPTED, InvitationStatus.SENT]:
                raise ValueError("User already invited or a member")
            new_invite = Membership(
                user_id=member_email,
                group_id=group_id,
                role=role,
                inviter_email=inviter_email,
                invite_date=datetime.now(timezone.utc),
                status=InvitationStatus.SENT
            )
            session.add(new_invite)
            session.commit()
            
            # Return dictionary with serialized data
            return {
                "id": f"{new_invite.user_id}_{new_invite.group_id}",
                "email": new_invite.user_id,
                "group_id": new_invite.group_id,
                "inviter_email": new_invite.inviter_email,
                "invite_date": new_invite.invite_date.isoformat(),
                "status": new_invite.status.value
            }
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def accept_invitation(self, user_email, group_id):
        session = self.db.get_session()
        try:
            invite = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == group_id,
                    Membership.status == InvitationStatus.SENT
                )
            ).first()
            if not invite:
                raise ValueError("Invitation not found")
            invite.status = InvitationStatus.ACCEPTED
            invite.join_date = datetime.now(timezone.utc)
            session.commit()
            return invite
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def decline_invitation(self, user_email, group_id):
        session = self.db.get_session()
        try:
            invite = session.query(Membership).filter(
                and_(
                    Membership.user_id == user_email,
                    Membership.group_id == group_id,
                    Membership.status == InvitationStatus.SENT
                )
            ).first()
            if not invite:
                raise ValueError("Invitation not found")
            session.delete(invite)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()