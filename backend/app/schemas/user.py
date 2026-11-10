from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole, UserType

class UserCreate(BaseModel): 
    full_name: str = Field(min_length=2,max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    user_type: UserType = UserType.STUDENT
    group_or_department: Optional[str] = None
    phone: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    user_type: UserType
    group_or_department: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    created_at: datetime