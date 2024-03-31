from enum import Enum


class Role(Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'
