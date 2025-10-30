import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .url import URLResponse


class UserBase(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username for the user"
    )
    email: EmailStr = Field(..., description="Email address of the user")


class UserCreate(UserBase):
    password: str = Field(
        ..., min_length=8, description="Password for the user account"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        if v.lower() in ["admin", "root", "superuser", "administrator"]:
            raise ValueError("This username is not allowed")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email for login")
    password: str = Field(..., description="Password for the account")


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithUrls(UserResponse):
    urls: list[URLResponse] = []

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
