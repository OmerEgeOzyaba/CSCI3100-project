from dataclasses import dataclass
from enum import Enum
from datetime import datetime

@dataclass
class User:
    email: str
    password: str
    created_at: datetime

    def get_email(self):
        return self.email
    
    def set_email(self, email: str):
        self.email = email

    def get_password(self):
        return self.password

    def set_password(self, password: str):
        self.password = password

    def get_created_at(self):
        return self.created_at

@dataclass
class Task:
    id: int 
    title: str
    description: str
    group_id: int
    created_at: datetime
    due_date: datetime
    status: bool

    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def set_title(self, title: str):
        self.title = title

    def get_description(self):
        return self.description

    def set_description(self, description: str):
        self.description = description

    def get_group_id(self):
        return self.group_id

    def get_created_at(self):
        return self.created_at

    def get_due_date(self):
        return self.due_date

    def set_due_date(self, due_date: datetime):
        self.due_date = due_date

    def get_status(self):
        return self.status

    def set_status(self, status: bool):
        self.status = status

@dataclass
class Group:
    id: int
    name: str
    description: str
    created_at: datetime

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description: str):
        self.description = description

    def get_created_at(self):
        return self.created_at

class Role(Enum):
    ADMIN = "admin"
    CONTRIBUTOR = "contributor"
    READER = "reader"

class InvitationStatus(Enum):
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    
@dataclass
class Membership:
    user: User
    group: Group
    role: Role
    inviter_email: str
    invite_date: datetime
    status: InvitationStatus
    join_date: datetime

    def get_user(self):
        return self.user

    def get_group(self):
        return self.group

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

    def set_join_date(self, join_date: datetime):
        self.join_date = join_date

@dataclass
class SoftwareLicense:
    key: str
    created_at: datetime
    used_status: int

    def get_key(self):
        return self.key

    def get_created_at(self):
        return self.created_at

    def get_used_status(self):
        return self.used_status

    def set_used_status(self, used_status: int):
        self.used_status = used_status
