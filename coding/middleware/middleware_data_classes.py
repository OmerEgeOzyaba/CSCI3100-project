from dataclasses import dataclass
from enum import Enum

from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Database

Base = declarative_base()

@dataclass
class User(Base):
    __tablename__ = 'Users'

    email: Mapped[String] = mapped_column(String, primary_key=True)
    password: Mapped[String] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    invitations_received: Mapped[list['Membership']] = relationship("Membership", back_populates="invited_user", foreign_keys="[Membership.user_id]")
    invitations_sent: Mapped[list['Membership']] = relationship("Membership", back_populates="inviting_user", foreign_keys="[Membership.inviter_email]")

    def get_email(self):
        return self.email
    
    def set_email(self, email: Mapped[String]):
        self.email = email

    def get_password(self):
        return self.password

    def set_password(self, password: Mapped[String]):
        self.password = password

    def get_created_at(self):
        return self.created_at
    
    def get_invitations_received(self):
        return self.invitations_received
    
    def get_invitations_sent(self):
        return self.invitations_sent

@dataclass
class Task(Base):
    __tablename__ = 'Tasks'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[String] = mapped_column(String, nullable=False)
    description: Mapped[String] = mapped_column(String, nullable=True)
    group_id: Mapped[Integer] = mapped_column(Integer, ForeignKey('Groups.id'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    status: Mapped[Boolean] = mapped_column(Boolean, nullable=False)

    group: Mapped['Group'] = relationship("Group", back_populates="tasks")

    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def set_title(self, title: Mapped[String]):
        self.title = title

    def get_description(self):
        return self.description

    def set_description(self, description: Mapped[String]):
        self.description = description

    def get_group_id(self):
        return self.group_id

    def get_created_at(self):
        return self.created_at

    def get_due_date(self):
        return self.due_date

    def set_due_date(self, due_date: Mapped[DateTime]):
        self.due_date = due_date

    def get_status(self):
        return self.status

    def set_status(self, status: Mapped[Boolean]):
        self.status = status

    def get_group(self):
        return self.group

@dataclass
class Group(Base):
    __tablename__ = 'Groups'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[String] = mapped_column(String, nullable=False)
    description: Mapped[String] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    tasks: Mapped[list[Task]] = relationship("Task", back_populates="group")
    memberships: Mapped[list['Membership']] = relationship("Membership", back_populates="group")

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def set_name(self, name: Mapped[String]):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description: Mapped[String]):
        self.description = description

    def get_created_at(self):
        return self.created_at
    
    def get_tasks(self):
        return self.tasks
    
    def get_memberships(self):
        return self.memberships

class Role(Enum):
    ADMIN = "admin"
    CONTRIBUTOR = "contributor"
    READER = "reader"

class InvitationStatus(Enum):
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    
@dataclass
class Membership(Base):
    __tablename__ = 'Memberships'

    user_id: Mapped[String] = mapped_column(String, ForeignKey('Users.email'), primary_key=True)
    group_id: Mapped[Integer] = mapped_column(Integer, ForeignKey('Groups.id'), primary_key=True)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False)
    inviter_email: Mapped[String] = mapped_column(String, ForeignKey('Users.email'), nullable=True)
    invite_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    status: Mapped[InvitationStatus] = mapped_column(SQLEnum(InvitationStatus), nullable=False)
    join_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    invited_user: Mapped[User] = relationship("User", back_populates="invitations_received", foreign_keys=[user_id])
    inviting_user: Mapped[User] = relationship("User", back_populates="invitations_sent", foreign_keys=[inviter_email])
    group: Mapped[Group] = relationship("Group", back_populates="memberships")

    def get_user_id(self):
        return self.user_id

    def get_group_id(self):
        return self.group_id

    def get_role(self):
        return self.role

    def set_role(self, role: Role):
        self.role = role

    def get_inviter_email(self):
        return self.inviter_email

    def get_invite_date(self):
        return self.invite_date

    def get_status(self):
        return self.status

    def set_status(self, status: InvitationStatus):
        self.status = status

    def get_join_date(self):
        return self.join_date

    def set_join_date(self, join_date: Mapped[DateTime]):
        self.join_date = join_date

    def get_invited_user(self):
        return self.invited_user
    
    def get_inviting_user(self):
        return self.inviting_user
    
    def get_group(self):
        return self.group

@dataclass
class SoftwareLicense(Base):
    __tablename__ = 'SoftwareLicenses'

    key: Mapped[String] = mapped_column(String, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    used_status: Mapped[Boolean] = mapped_column(Boolean, nullable=False)

    def get_key(self):
        return self.key

    def get_created_at(self):
        return self.created_at

    def get_used_status(self):
        return self.used_status

    def set_used_status(self, used_status: Mapped[Integer]):
        self.used_status = used_status

def create_database():
    Base.metadata.create_all(Database().get_engine())
