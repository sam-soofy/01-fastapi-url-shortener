import secrets
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import Optional
from app.models.url import URL
from app.schemas.url import URLCreate


def generate_short_code(length: int = 8) -> str:
    """Generate a random short code for URLs."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


async def create_url(db: AsyncSession, url_create: URLCreate) -> URL:
    """Create a new URL entry."""
    short_code = generate_short_code()
    # Ensure unique short code
    while await get_url_by_short_code(db, short_code):
        short_code = generate_short_code()

    db_url = URL(
        original_url=url_create.original_url,
        short_code=short_code,
        clicks=0
    )
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    return db_url


async def get_url_by_short_code(db: AsyncSession, short_code: str) -> Optional[URL]:
    """Get URL by short code."""
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    return result.scalars().first()


async def get_url_by_id(db: AsyncSession, url_id: int) -> Optional[URL]:
    """Get URL by ID."""
    result = await db.execute(
        select(URL).where(URL.id == url_id)
    )
    return result.scalars().first()


async def increment_click_count(db: AsyncSession, short_code: str) -> bool:
    """Increment click count for a URL."""
    result = await db.execute(
        update(URL)
        .where(URL.short_code == short_code)
        .values(clicks=URL.clicks + 1)
    )
    await db.commit()
    return result.rowcount > 0


async def get_all_urls(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all URLs with pagination."""
    result = await db.execute(
        select(URL).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def delete_url(db: AsyncSession, url_id: int) -> bool:
    """Delete a URL by ID."""
    db_url = await get_url_by_id(db, url_id)
    if db_url:
        await db.delete(db_url)
        await db.commit()
        return True
    return False
