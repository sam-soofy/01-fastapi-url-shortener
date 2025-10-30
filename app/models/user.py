from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import Base

if TYPE_CHECKING:
    from app.models.url import URL


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship to URLs
    urls: Mapped[list["URL"]] = relationship(
        "URL", back_populates="user", cascade="all, delete"
    )

    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the user's password"""
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
