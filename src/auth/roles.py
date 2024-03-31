from fastapi import Request, Depends, HTTPException, status

from src.auth.service import get_current_user
from src.models import Role
from src.models import User


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request, user: User = Depends(get_current_user)):
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='FORBIDDEN')
