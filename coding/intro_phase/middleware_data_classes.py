from dataclasses import dataclass
from enum import Enum
from datetime import datetime

@dataclass
class User:
    email: str
    password: str
    created_at: datetime

@dataclass
class Task:
    id: int 
    title: str
    description: str
    group_id: int
    created_at: datetime
    due_date: datetime
    status: bool

@dataclass
class Group:
    id: int
    name: str
    description: str
    created_at: datetime

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

@dataclass
class SoftwareLicense:
    key: str
    created_at: datetime
    used_status: int
