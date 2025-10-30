from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import validators


class URLBase(BaseModel):
    original_url: str = Field(..., description="The original URL to shorten")


class URLCreate(URLBase):
    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not validators.url(v):
            raise ValueError("Invalid URL format")
        return v


class URLResponse(URLBase):
    id: int
    short_code: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True


class URLStats(BaseModel):
    original_url: str
    short_code: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True
