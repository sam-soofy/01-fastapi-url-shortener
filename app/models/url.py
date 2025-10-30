from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.analytics import URLClick
    from app.models.user import User


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(
        String(8), unique=True, index=True, nullable=False
    )
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Foreign key to user
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Relationship to User
    user: Mapped[Optional["User"]] = relationship("User", back_populates="urls")

    # Relationship to URL clicks - renamed clicks relationship to avoid conflict with clicks column
    click_data: Mapped[list["URLClick"]] = relationship(
        "URLClick", back_populates="url", cascade="all, delete-orphan"
    )
