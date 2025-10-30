import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas


class TestUserCRUD:
    """Test user CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession):
        """Test successful user creation."""
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )

        user = await crud.create_user(db_session, user_data)

        assert user.username == user_data.username
        assert user.email == user_data.email
        assert user.id is not None
        assert user.hashed_password != user_data.password  # Should be hashed

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, db_session: AsyncSession):
        """Test creating user with duplicate username."""
        user_data = schemas.UserCreate(
            username="testuser", email="test1@example.com", password="TestPass123!"
        )

        # Create first user
        await crud.create_user(db_session, user_data)

        # Try to create user with same username
        duplicate_data = schemas.UserCreate(
            username="testuser", email="test2@example.com", password="TestPass123!"
        )

        with pytest.raises(ValueError, match="Username already registered"):
            await crud.create_user(db_session, duplicate_data)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_session: AsyncSession):
        """Test creating user with duplicate email."""
        user_data = schemas.UserCreate(
            username="testuser1", email="test@example.com", password="TestPass123!"
        )

        # Create first user
        await crud.create_user(db_session, user_data)

        # Try to create user with same email
        duplicate_data = schemas.UserCreate(
            username="testuser2", email="test@example.com", password="TestPass123!"
        )

        with pytest.raises(ValueError, match="Email already registered"):
            await crud.create_user(db_session, duplicate_data)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session: AsyncSession):
        """Test successful user authentication."""
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )

        # Create user
        created_user = await crud.create_user(db_session, user_data)

        # Authenticate with username
        authenticated_user = await crud.authenticate_user(
            db_session, user_data.username, user_data.password
        )

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id

    @pytest.mark.asyncio
    async def test_authenticate_user_with_email(self, db_session: AsyncSession):
        """Test user authentication with email."""
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )

        # Create user
        created_user = await crud.create_user(db_session, user_data)

        # Authenticate with email
        authenticated_user = await crud.authenticate_user(
            db_session, user_data.email, user_data.password
        )

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session: AsyncSession):
        """Test authentication with wrong password."""
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )

        # Create user
        await crud.create_user(db_session, user_data)

        # Try to authenticate with wrong password
        authenticated_user = await crud.authenticate_user(
            db_session, user_data.username, "wrongpassword"
        )

        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, db_session: AsyncSession):
        """Test authentication with non-existent user."""
        authenticated_user = await crud.authenticate_user(
            db_session, "nonexistent", "password123"
        )

        assert authenticated_user is None


class TestURLCRUD:
    """Test URL CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_url_success(self, db_session: AsyncSession):
        """Test successful URL creation."""
        url_data = schemas.URLCreate(original_url="https://www.example.com")

        url = await crud.create_url(db_session, url_data)

        assert url.original_url == url_data.original_url
        assert url.short_code is not None
        assert url.id is not None
        assert url.clicks == 0

    @pytest.mark.asyncio
    async def test_create_url_with_user(self, db_session: AsyncSession):
        """Test creating URL with user association."""
        # Create user first
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        user = await crud.create_user(db_session, user_data)

        # Create URL with user
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data, user.id)

        assert url.original_url == url_data.original_url
        assert url.user_id == user.id

    @pytest.mark.asyncio
    async def test_get_url_by_short_code_success(self, db_session: AsyncSession):
        """Test getting URL by short code."""
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        created_url = await crud.create_url(db_session, url_data)

        retrieved_url = await crud.get_url_by_short_code(
            db_session, created_url.short_code
        )

        assert retrieved_url is not None
        assert retrieved_url.id == created_url.id
        assert retrieved_url.short_code == created_url.short_code

    @pytest.mark.asyncio
    async def test_get_url_by_short_code_not_found(self, db_session: AsyncSession):
        """Test getting non-existent URL by short code."""
        url = await crud.get_url_by_short_code(db_session, "nonexistent")
        assert url is None

    @pytest.mark.asyncio
    async def test_get_urls_by_user(self, db_session: AsyncSession):
        """Test getting URLs by user."""
        # Create user
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        user = await crud.create_user(db_session, user_data)

        # Create URLs for user
        for i in range(3):
            url_data = schemas.URLCreate(original_url=f"https://www.example{i}.com")
            await crud.create_url(db_session, url_data, user.id)

        # Get user URLs
        urls = await crud.get_urls_by_user(db_session, user.id)

        assert len(urls) == 3
        for url in urls:
            assert url.user_id == user.id

    @pytest.mark.asyncio
    async def test_increment_click_count(self, db_session: AsyncSession):
        """Test incrementing URL click count."""
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data)

        initial_clicks = url.clicks
        assert initial_clicks == 0

        # Increment clicks
        await crud.increment_click_count(db_session, url.short_code)

        # Get updated URL
        updated_url = await crud.get_url_by_short_code(db_session, url.short_code)
        assert updated_url is not None
        assert updated_url.clicks == 1

    @pytest.mark.asyncio
    async def test_update_url_success(self, db_session: AsyncSession):
        """Test updating URL."""
        # Create user
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        user = await crud.create_user(db_session, user_data)

        # Create URL
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data, user.id)

        # Update URL
        updated_data = schemas.URLCreate(original_url="https://www.updated.com")
        updated_url = await crud.update_url(db_session, url.id, user.id, updated_data)

        assert updated_url is not None
        assert updated_url.original_url == updated_data.original_url

    @pytest.mark.asyncio
    async def test_update_url_not_found(self, db_session: AsyncSession):
        """Test updating non-existent URL."""
        updated_data = schemas.URLCreate(original_url="https://www.updated.com")
        updated_url = await crud.update_url(db_session, 999, 1, updated_data)

        assert updated_url is None

    @pytest.mark.asyncio
    async def test_delete_url_by_user_success(self, db_session: AsyncSession):
        """Test deleting URL by user."""
        # Create user
        user_data = schemas.UserCreate(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        user = await crud.create_user(db_session, user_data)

        # Create URL
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data, user.id)

        # Delete URL
        success = await crud.delete_url_by_user(db_session, url.id, user.id)

        assert success is True

        # Verify URL is deleted
        deleted_url = await crud.get_url_by_short_code(db_session, url.short_code)
        assert deleted_url is None

    @pytest.mark.asyncio
    async def test_delete_url_by_user_not_found(self, db_session: AsyncSession):
        """Test deleting non-existent URL by user."""
        success = await crud.delete_url_by_user(db_session, 999, 1)

        assert success is False
