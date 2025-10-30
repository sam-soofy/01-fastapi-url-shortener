from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app import crud, schemas


class TestAnalyticsCRUD:
    """Test analytics CRUD operations."""

    @pytest.mark.asyncio

    async def test_create_click_analytics(self, db_session: AsyncSession):
        """Test creating click analytics."""
        # Create URL first
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data)

        # Create analytics
        analytics = await crud.create_click_analytics(
            db=db_session,
            url_id=url.id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0 (Test Browser)",
            referrer="https://www.google.com",
        )

        assert analytics is not None
        assert analytics.url_id == url.id
        assert analytics.ip_address == "192.168.1.1"
        assert analytics.user_agent == "Mozilla/5.0 (Test Browser)"
        assert analytics.referrer == "https://www.google.com"

    @pytest.mark.asyncio

    async def test_get_url_analytics_summary(self, db_session: AsyncSession):
        """Test getting URL analytics summary."""
        # Create URL first
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data)

        # Create some analytics data
        for i in range(5):
            await crud.create_click_analytics(
                db=db_session,
                url_id=url.id,
                ip_address=f"192.168.1.{i}",
                user_agent=f"Mozilla/5.0 (Test Browser {i})",
                referrer="https://www.google.com",
            )

        # Get analytics summary
        summary = await crud.get_url_analytics_summary(db_session, url.id, days=30)

        assert summary is not None
        assert summary.total_clicks == 5
        assert summary.unique_visitors == 5  # All different IPs
        assert "device_breakdown" in summary.__dict__
        assert "browser_breakdown" in summary.__dict__

    @pytest.mark.asyncio

    async def test_get_global_analytics_summary(self, db_session: AsyncSession):
        """Test getting global analytics summary."""
        # Create multiple URLs
        urls = []
        for i in range(3):
            url_data = schemas.URLCreate(original_url=f"https://www.example{i}.com")
            url = await crud.create_url(db_session, url_data)
            urls.append(url)

        # Create analytics data for different URLs
        for i, url in enumerate(urls):
            for j in range(2):
                await crud.create_click_analytics(
                    db=db_session,
                    url_id=url.id,
                    ip_address=f"192.168.1.{i}{j}",
                    user_agent=f"Mozilla/5.0 (Test Browser {i}{j})",
                    referrer="https://www.google.com",
                )

        # Get global analytics summary
        summary = await crud.get_global_analytics_summary(db_session, days=30)

        assert summary is not None
        assert summary.total_clicks == 6  # 3 URLs * 2 clicks each
        assert summary.unique_visitors == 6  # All different IPs
        assert "device_breakdown" in summary.__dict__
        assert "browser_breakdown" in summary.__dict__

    @pytest.mark.asyncio

    async def test_analytics_device_detection(self, db_session: AsyncSession):
        """Test device detection in analytics."""
        # Create URL first
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data)

        # Create analytics with different user agents
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        tablet_ua = "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15"

        await crud.create_click_analytics(
            db=db_session, url_id=url.id, ip_address="192.168.1.1", user_agent=mobile_ua
        )

        await crud.create_click_analytics(
            db=db_session,
            url_id=url.id,
            ip_address="192.168.1.2",
            user_agent=desktop_ua,
        )

        await crud.create_click_analytics(
            db=db_session, url_id=url.id, ip_address="192.168.1.3", user_agent=tablet_ua
        )

        # Get analytics summary
        summary = await crud.get_url_analytics_summary(db_session, url.id, days=30)

        assert summary is not None
        assert summary.total_clicks == 3
        assert summary.unique_visitors == 3

        # Check device breakdown (implementation specific)
        device_breakdown = getattr(summary, "device_breakdown", {})
        assert len(device_breakdown) > 0

    @pytest.mark.asyncio

    async def test_analytics_browser_detection(self, db_session: AsyncSession):
        """Test browser detection in analytics."""
        # Create URL first
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data)

        # Create analytics with different browsers
        chrome_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        firefox_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        safari_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"

        await crud.create_click_analytics(
            db=db_session, url_id=url.id, ip_address="192.168.1.1", user_agent=chrome_ua
        )

        await crud.create_click_analytics(
            db=db_session,
            url_id=url.id,
            ip_address="192.168.1.2",
            user_agent=firefox_ua,
        )

        await crud.create_click_analytics(
            db=db_session, url_id=url.id, ip_address="192.168.1.3", user_agent=safari_ua
        )

        # Get analytics summary
        summary = await crud.get_url_analytics_summary(db_session, url.id, days=30)

        assert summary is not None
        assert summary.total_clicks == 3
        assert summary.unique_visitors == 3

        # Check browser breakdown (implementation specific)
        browser_breakdown = getattr(summary, "browser_breakdown", {})
        assert len(browser_breakdown) > 0

    @pytest.mark.asyncio

    async def test_analytics_time_filtering(self, db_session: AsyncSession):
        """Test analytics time filtering."""
        # Create URL first
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data)

        # Create analytics data
        for i in range(5):
            await crud.create_click_analytics(
                db=db_session,
                url_id=url.id,
                ip_address=f"192.168.1.{i}",
                user_agent=f"Mozilla/5.0 (Test Browser {i})",
            )

        # Get analytics for different time periods
        summary_7_days = await crud.get_url_analytics_summary(
            db_session, url.id, days=7
        )
        summary_30_days = await crud.get_url_analytics_summary(
            db_session, url.id, days=30
        )

        # Both should include all clicks since they're created recently
        assert summary_7_days.total_clicks == 5
        assert summary_30_days.total_clicks == 5
        assert summary_7_days.unique_visitors == 5
        assert summary_30_days.unique_visitors == 5

    @pytest.mark.asyncio

    async def test_analytics_with_no_data(self, db_session: AsyncSession):
        """Test analytics when no data exists."""
        # Create URL first
        url_data = schemas.URLCreate(original_url="https://www.example.com")
        url = await crud.create_url(db_session, url_data)

        # Get analytics without any clicks
        summary = await crud.get_url_analytics_summary(db_session, url.id, days=30)

        assert summary is not None
        assert summary.total_clicks == 0
        assert summary.unique_visitors == 0
        assert "device_breakdown" in summary.__dict__
        assert "browser_breakdown" in summary.__dict__
