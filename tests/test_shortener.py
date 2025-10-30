from httpx import AsyncClient
import pytest


class TestShortenerEndpoints:
    """Test URL shortener endpoints."""

    @pytest.mark.asyncio

    async def test_create_short_url_success(
        self, client: AsyncClient, test_url_data: dict
    ):
        """Test successful URL shortening."""
        response = await client.post("/api/v1/shorten", json=test_url_data)

        assert response.status_code == 201
        data = response.json()
        assert data["original_url"] == test_url_data["original_url"]
        assert "short_code" in data
        assert "id" in data
        assert data["clicks"] == 0

    @pytest.mark.asyncio

    async def test_create_short_url_invalid_url(self, client: AsyncClient):
        """Test URL shortening with invalid URL."""
        invalid_data = {"original_url": "invalid-url"}
        response = await client.post("/api/v1/shorten", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio

    async def test_redirect_to_url_success(
        self, client: AsyncClient, test_url_data: dict
    ):
        """Test successful URL redirect."""
        # Create short URL first
        create_response = await client.post("/api/v1/shorten", json=test_url_data)
        short_code = create_response.json()["short_code"]

        # Test redirect
        response = await client.get(f"/api/v1/{short_code}")

        assert response.status_code == 302  # Redirect status
        assert response.headers["location"] == test_url_data["original_url"]

    @pytest.mark.asyncio

    async def test_redirect_to_url_not_found(self, client: AsyncClient):
        """Test redirect with non-existent short code."""
        response = await client.get("/api/v1/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio

    async def test_get_url_stats_success(
        self, client: AsyncClient, test_url_data: dict
    ):
        """Test getting URL statistics."""
        # Create short URL first
        create_response = await client.post("/api/v1/shorten", json=test_url_data)
        short_code = create_response.json()["short_code"]

        # Get stats
        response = await client.get(f"/api/v1/stats/{short_code}")

        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == test_url_data["original_url"]
        assert data["short_code"] == short_code
        assert data["clicks"] == 0

    @pytest.mark.asyncio

    async def test_get_url_stats_not_found(self, client: AsyncClient):
        """Test getting stats for non-existent URL."""
        response = await client.get("/api/v1/stats/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio

    async def test_get_url_analytics_success(
        self, client: AsyncClient, test_url_data: dict
    ):
        """Test getting URL analytics."""
        # Create short URL first
        create_response = await client.post("/api/v1/shorten", json=test_url_data)
        short_code = create_response.json()["short_code"]

        # Get analytics
        response = await client.get(f"/api/v1/analytics/{short_code}")

        assert response.status_code == 200
        data = response.json()
        assert "total_clicks" in data
        assert "unique_visitors" in data
        assert "device_breakdown" in data
        assert "browser_breakdown" in data

    @pytest.mark.asyncio

    async def test_get_url_analytics_not_found(self, client: AsyncClient):
        """Test getting analytics for non-existent URL."""
        response = await client.get("/api/v1/analytics/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio

    async def test_get_global_analytics(self, client: AsyncClient):
        """Test getting global analytics."""
        response = await client.get("/api/v1/analytics/global")

        assert response.status_code == 200
        data = response.json()
        assert "total_clicks" in data
        assert "unique_visitors" in data
        assert "device_breakdown" in data
        assert "browser_breakdown" in data

    @pytest.mark.asyncio

    async def test_redirect_increments_clicks(
        self, client: AsyncClient, test_url_data: dict
    ):
        """Test that redirect increments click count."""
        # Create short URL first
        create_response = await client.post("/api/v1/shorten", json=test_url_data)
        short_code = create_response.json()["short_code"]

        # Initial stats
        stats_response = await client.get(f"/api/v1/stats/{short_code}")
        initial_clicks = stats_response.json()["clicks"]
        assert initial_clicks == 0

        # Perform redirect
        await client.get(f"/api/v1/{short_code}")

        # Check stats again
        stats_response = await client.get(f"/api/v1/stats/{short_code}")
        final_clicks = stats_response.json()["clicks"]
        assert final_clicks == 1


class TestUserShortenerEndpoints:
    """Test user-specific URL shortener endpoints."""

    @pytest.mark.asyncio

    async def test_create_user_short_url_success(
        self, client: AsyncClient, auth_headers: dict, test_url_data: dict
    ):
        """Test creating short URL for authenticated user."""
        response = await client.post(
            "/api/v1/user/shorten", json=test_url_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["original_url"] == test_url_data["original_url"]
        assert "short_code" in data
        assert "id" in data
        assert data["clicks"] == 0

    @pytest.mark.asyncio

    async def test_create_user_short_url_unauthorized(
        self, client: AsyncClient, test_url_data: dict
    ):
        """Test creating user short URL without authentication."""
        response = await client.post("/api/v1/user/shorten", json=test_url_data)

        assert response.status_code == 401

    @pytest.mark.asyncio

    async def test_get_user_urls_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting user URLs when user has none."""
        response = await client.get("/api/v1/user/urls", headers=auth_headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    @pytest.mark.asyncio

    async def test_get_user_urls_with_data(
        self, client: AsyncClient, auth_headers: dict, test_url_data: dict
    ):
        """Test getting user URLs when user has created URLs."""
        # Create a short URL first
        await client.post(
            "/api/v1/user/shorten", json=test_url_data, headers=auth_headers
        )

        # Get user URLs
        response = await client.get("/api/v1/user/urls", headers=auth_headers)

        assert response.status_code == 200
        urls = response.json()
        assert len(urls) == 1
        assert urls[0]["original_url"] == test_url_data["original_url"]

    @pytest.mark.asyncio

    async def test_get_user_urls_unauthorized(self, client: AsyncClient):
        """Test getting user URLs without authentication."""
        response = await client.get("/api/v1/user/urls")

        assert response.status_code == 401

    @pytest.mark.asyncio

    async def test_get_user_url_by_id_success(
        self, client: AsyncClient, auth_headers: dict, test_url_data: dict
    ):
        """Test getting user URL by ID."""
        # Create a short URL first
        create_response = await client.post(
            "/api/v1/user/shorten", json=test_url_data, headers=auth_headers
        )
        url_id = create_response.json()["id"]

        # Get URL by ID
        response = await client.get(f"/api/v1/user/urls/{url_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == url_id
        assert data["original_url"] == test_url_data["original_url"]

    @pytest.mark.asyncio

    async def test_get_user_url_by_id_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent user URL by ID."""
        response = await client.get("/api/v1/user/urls/999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio

    async def test_get_user_url_by_id_unauthorized(self, client: AsyncClient):
        """Test getting user URL by ID without authentication."""
        response = await client.get("/api/v1/user/urls/1")

        assert response.status_code == 401

    @pytest.mark.asyncio

    async def test_update_user_url_success(
        self, client: AsyncClient, auth_headers: dict, test_url_data: dict
    ):
        """Test updating user URL."""
        # Create a short URL first
        create_response = await client.post(
            "/api/v1/user/shorten", json=test_url_data, headers=auth_headers
        )
        url_id = create_response.json()["id"]

        # Update URL
        updated_data = {"original_url": "https://www.updated-example.com"}
        response = await client.put(
            f"/api/v1/user/urls/{url_id}", json=updated_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == url_id
        assert data["original_url"] == updated_data["original_url"]

    @pytest.mark.asyncio

    async def test_update_user_url_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent user URL."""
        updated_data = {"original_url": "https://www.updated-example.com"}
        response = await client.put(
            "/api/v1/user/urls/999", json=updated_data, headers=auth_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio

    async def test_update_user_url_unauthorized(
        self, client: AsyncClient, test_url_data: dict
    ):
        """Test updating user URL without authentication."""
        response = await client.put("/api/v1/user/urls/1", json=test_url_data)

        assert response.status_code == 401

    @pytest.mark.asyncio

    async def test_delete_user_url_success(
        self, client: AsyncClient, auth_headers: dict, test_url_data: dict
    ):
        """Test deleting user URL."""
        # Create a short URL first
        create_response = await client.post(
            "/api/v1/user/shorten", json=test_url_data, headers=auth_headers
        )
        url_id = create_response.json()["id"]

        # Delete URL
        response = await client.delete(
            f"/api/v1/user/urls/{url_id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify URL is deleted
        get_response = await client.get(
            f"/api/v1/user/urls/{url_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio

    async def test_delete_user_url_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent user URL."""
        response = await client.delete("/api/v1/user/urls/999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio

    async def test_delete_user_url_unauthorized(self, client: AsyncClient):
        """Test deleting user URL without authentication."""
        response = await client.delete("/api/v1/user/urls/1")

        assert response.status_code == 401

    @pytest.mark.asyncio

    async def test_user_urls_pagination(
        self, client: AsyncClient, auth_headers: dict, test_url_data: dict
    ):
        """Test user URLs pagination."""
        # Create multiple URLs
        for i in range(5):
            url_data = {"original_url": f"https://www.example{i}.com"}
            await client.post(
                "/api/v1/user/shorten", json=url_data, headers=auth_headers
            )

        # Test pagination
        response = await client.get(
            "/api/v1/user/urls?skip=2&limit=2", headers=auth_headers
        )

        assert response.status_code == 200
        urls = response.json()
        assert len(urls) == 2
