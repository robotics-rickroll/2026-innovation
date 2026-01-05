from __future__ import annotations
from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True
