from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, PastDate

from src.auth.schemas import UserResponseSchema


class ContactSchema(BaseModel):
    name: str
    second_name: str
    email: EmailStr
    phone: str
    birthday: PastDate
    address: Optional[str] = None


class ContactResponseSchema(BaseModel):
    id: int
    name: str
    second_name: str
    email: EmailStr
    phone: str
    birthday: PastDate
    address: str | None
    created_at: datetime | None
    created_at: datetime | None
    user: UserResponseSchema | None

    class Config:
        from_attributes = True
