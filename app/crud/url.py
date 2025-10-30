import secrets
import string
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.url import URL
from app.schemas.url import URLCreate


def generate_short_code(length: int = 8) -> str:
    """Generate a random short code for URLs."""
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


async def create_url(
    db: AsyncSession, url_create: URLCreate, user_id: Optional[int] = None
) -> URL:
    """Create a new URL entry."""
    short_code = generate_short_code()
    # Ensure unique short code
    while await get_url_by_short_code(db, short_code):
        short_code = generate_short_code()

    db_url = URL(
        original_url=url_create.original_url,
        short_code=short_code,
        clicks=0,
        user_id=user_id,
    )
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    return db_url


async def get_url_by_short_code(db: AsyncSession, short_code: str) -> Optional[URL]:
    """Get URL by short code."""
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    return result.scalars().first()


async def get_url_by_id(db: AsyncSession, url_id: int) -> Optional[URL]:
    """Get URL by ID."""
    result = await db.execute(select(URL).where(URL.id == url_id))
    return result.scalars().first()


async def increment_click_count(db: AsyncSession, short_code: str) -> bool:
    """Increment click count for a URL."""
    # Verify URL exists first
    db_url = await get_url_by_short_code(db, short_code)
    if not db_url:
        return False

    await db.execute(
        update(URL).where(URL.short_code == short_code).values(clicks=URL.clicks + 1)
    )
    await db.commit()
    return True


async def get_urls_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> list[URL]:
    """Get URLs for a specific user with pagination."""
    result = await db.execute(
        select(URL).where(URL.user_id == user_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_url_by_id_and_user(
    db: AsyncSession, url_id: int, user_id: int
) -> Optional[URL]:
    """Get URL by ID and ensure it belongs to the user."""
    result = await db.execute(
        select(URL).where(URL.id == url_id, URL.user_id == user_id)
    )
    return result.scalars().first()


async def update_url(
    db: AsyncSession, url_id: int, user_id: int, url_update: URLCreate
) -> Optional[URL]:
    """Update a URL for a specific user."""
    db_url = await get_url_by_id_and_user(db, url_id, user_id)
    if not db_url:
        return None

    # Update using SQLAlchemy's update statement to avoid type issues
    await db.execute(
        update(URL).where(URL.id == url_id).values(original_url=url_update.original_url)
    )
    await db.commit()
    await db.refresh(db_url)
    return db_url


async def delete_url_by_user(db: AsyncSession, url_id: int, user_id: int) -> bool:
    """Delete a URL by ID and ensure it belongs to the user."""
    db_url = await get_url_by_id_and_user(db, url_id, user_id)
    if db_url:
        await db.delete(db_url)
        await db.commit()
        return True
    return False


async def get_all_urls(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[URL]:
    """Get all URLs with pagination."""
    result = await db.execute(select(URL).offset(skip).limit(limit))
    return list(result.scalars().all())


async def delete_url(db: AsyncSession, url_id: int) -> bool:
    """Delete a URL by ID."""
    db_url = await get_url_by_id(db, url_id)
    if db_url:
        await db.delete(db_url)
        await db.commit()
        return True
    return False
