import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test successful user registration."""
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "password" not in data  # Password should not be in response

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test registration with duplicate username."""
        # Register first user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register with same username
        duplicate_user = test_user_data.copy()
        duplicate_user["email"] = "different@example.com"

        response = await client.post("/api/v1/auth/register", json=duplicate_user)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test registration with duplicate email."""
        # Register first user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register with same email
        duplicate_user = test_user_data.copy()
        duplicate_user["username"] = "differentuser"

        response = await client.post("/api/v1/auth/register", json=duplicate_user)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test registration with invalid email."""
        invalid_user = test_user_data.copy()
        invalid_user["email"] = "invalid-email"

        response = await client.post("/api/v1/auth/register", json=invalid_user)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_user_weak_password(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test registration with weak password."""
        weak_user = test_user_data.copy()
        weak_user["password"] = "weak"

        response = await client.post("/api/v1/auth/register", json=weak_user)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful user login."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_with_email(self, client: AsyncClient, test_user_data: dict):
        """Test login using email instead of username."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login with email
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test login with invalid credentials."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword",
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {"username": "nonexistent", "password": "password123"}
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_current_user_profile(
        self, client: AsyncClient, auth_headers: dict, test_user_data: dict
    ):
        """Test getting current user profile."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_profile_unauthorized(self, client: AsyncClient):
        """Test getting profile without authentication."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_urls_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting current user URLs when user has none."""
        response = await client.get("/api/v1/auth/me/urls", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "urls" in data
        assert len(data["urls"]) == 0

    @pytest.mark.asyncio
    async def test_get_current_user_urls_unauthorized(self, client: AsyncClient):
        """Test getting user URLs without authentication."""
        response = await client.get("/api/v1/auth/me/urls")

        assert response.status_code == 401
