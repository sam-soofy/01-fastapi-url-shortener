from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import models, schemas


async def get_user_by_username(
    db: AsyncSession, username: str
) -> Optional[models.User]:
    """Get user by username"""
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Get user by email"""
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def get_user_with_urls(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Get user with their URLs"""
    result = await db.execute(
        select(models.User)
        .where(models.User.id == user_id)
        .options(selectinload(models.User.urls))
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    # Check if username already exists
    if await get_user_by_username(db, user.username):
        raise ValueError("Username already registered")

    # Check if email already exists
    if await get_user_by_email(db, user.email):
        raise ValueError("Email already registered")

    db_user = models.User(username=user.username, email=user.email)
    db_user.set_password(user.password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[models.User]:
    """Authenticate a user with username/email and password"""
    # Try to find user by username first, then by email
    user = await get_user_by_username(db, username)
    if not user:
        user = await get_user_by_email(db, username)

    if user and user.check_password(password):
        return user
    return None


async def update_user(
    db: AsyncSession, user_id: int, user_update: schemas.UserCreate
) -> Optional[models.User]:
    """Update user information"""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None

    # Check if username is taken by another user
    if user_update.username != db_user.username:
        existing_user = await get_user_by_username(db, user_update.username)
        if existing_user:
            raise ValueError("Username already taken")

    # Check if email is taken by another user
    if user_update.email != db_user.email:
        existing_user = await get_user_by_email(db, user_update.email)
        if existing_user:
            raise ValueError("Email already taken")

    # Update user attributes properly
    if user_update.username:
        db_user.username = user_update.username  # type: ignore
    if user_update.email:
        db_user.email = user_update.email  # type: ignore
    if user_update.password:
        db_user.set_password(user_update.password)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete a user"""
    db_user = await get_user_by_id(db, user_id)
    if db_user:
        await db.delete(db_user)
        await db.commit()
        return True
    return False


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[models.User]:
    """Get all users with pagination"""
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return list(result.scalars().all())
