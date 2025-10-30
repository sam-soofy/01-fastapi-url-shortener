from datetime import UTC, datetime, timedelta
from typing import Optional

import user_agents
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.analytics import URLClick
from app.schemas.analytics import AnalyticsSummary


async def create_click_analytics(
    db: AsyncSession,
    url_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None,
) -> URLClick:
    """
    Create a URL click analytics record.
    """
    # Parse user agent for additional info
    device_type = browser = None
    if user_agent:
        ua = user_agents.parse(user_agent)
        device_type = (
            "mobile" if ua.is_mobile else ("tablet" if ua.is_tablet else "desktop")
        )
        browser = ua.browser.family

    db_click = URLClick(
        url_id=url_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
        device_type=device_type,
        browser=browser,
    )
    db.add(db_click)
    await db.commit()
    await db.refresh(db_click)
    return db_click


async def get_url_clicks(
    db: AsyncSession, url_id: int, skip: int = 0, limit: int = 100
) -> list[URLClick]:
    """
    Get all clicks for a URL with pagination.
    """
    result = await db.execute(
        select(URLClick)
        .where(URLClick.url_id == url_id)
        .offset(skip)
        .limit(limit)
        .order_by(URLClick.clicked_at.desc())
    )
    return list(result.scalars().all())


async def get_url_analytics_summary(
    db: AsyncSession, url_id: int, days: int = 30
) -> AnalyticsSummary:
    """
    Get analytics summary for a URL.
    """
    # Calculate date range
    start_date = datetime.now(UTC) - timedelta(days=days)

    # Get total clicks
    total_clicks_result = await db.execute(
        select(func.count(URLClick.id)).where(URLClick.url_id == url_id)
    )
    total_clicks: int = total_clicks_result.scalar() or 0

    # Get clicks in date range
    range_clicks_result = await db.execute(
        select(func.count(URLClick.id)).where(
            URLClick.url_id == url_id, URLClick.clicked_at >= start_date
        )
    )
    range_clicks: int = range_clicks_result.scalar() or 0

    # Get device type breakdown
    device_result = await db.execute(
        select(URLClick.device_type, func.count(URLClick.id))
        .where(URLClick.url_id == url_id, URLClick.clicked_at >= start_date)
        .group_by(URLClick.device_type)
    )
    device_stats = {device: count for device, count in device_result.all() if device}

    # Get browser breakdown
    browser_result = await db.execute(
        select(URLClick.browser, func.count(URLClick.id))
        .where(URLClick.url_id == url_id, URLClick.clicked_at >= start_date)
        .group_by(URLClick.browser)
    )
    browser_stats = {
        browser: count for browser, count in browser_result.all() if browser
    }

    # Get unique visitors (distinct IP addresses) in date range
    unique_visitors_result = await db.execute(
        select(func.count(func.distinct(URLClick.ip_address))).where(
            URLClick.url_id == url_id, URLClick.clicked_at >= start_date
        )
    )
    unique_visitors: int = unique_visitors_result.scalar() or 0

    # Get referrer breakdown (top 10)
    referrer_result = await db.execute(
        select(URLClick.referrer, func.count(URLClick.id))
        .where(
            URLClick.url_id == url_id,
            URLClick.clicked_at >= start_date,
            URLClick.referrer.isnot(None),
        )
        .group_by(URLClick.referrer)
        .order_by(func.count(URLClick.id).desc())
        .limit(10)
    )
    referrer_stats = {ref: count for ref, count in referrer_result.all() if ref}

    # Get daily click counts for the last 30 days
    daily_clicks_result = await db.execute(
        select(
            func.date(URLClick.clicked_at).label("date"),
            func.count(URLClick.id).label("count"),
        )
        .where(URLClick.url_id == url_id, URLClick.clicked_at >= start_date)
        .group_by(func.date(URLClick.clicked_at))
        .order_by("date")
    )
    daily_clicks = {str(date): count for date, count in daily_clicks_result.all()}

    return AnalyticsSummary(
        total_clicks=total_clicks,
        clicks_in_range=range_clicks,
        unique_visitors=unique_visitors,
        date_range_days=days,
        device_breakdown=device_stats,
        browser_breakdown=browser_stats,
        top_referrers=referrer_stats,
        daily_clicks=daily_clicks,
    )


async def get_global_analytics_summary(
    db: AsyncSession, days: int = 30
) -> AnalyticsSummary:
    """
    Get global analytics summary (all URLs).
    """
    # Calculate date range
    start_date = datetime.now(UTC) - timedelta(days=days)

    # Get total clicks
    total_clicks_result = await db.execute(select(func.count(URLClick.id)))
    total_clicks: int = total_clicks_result.scalar() or 0

    # Get clicks in date range
    range_clicks_result = await db.execute(
        select(func.count(URLClick.id)).where(URLClick.clicked_at >= start_date)
    )
    range_clicks: int = range_clicks_result.scalar() or 0

    # Get unique visitors (distinct IP addresses) in date range
    unique_visitors_result = await db.execute(
        select(func.count(func.distinct(URLClick.ip_address))).where(
            URLClick.clicked_at >= start_date
        )
    )
    unique_visitors: int = unique_visitors_result.scalar() or 0

    # Get device type breakdown
    device_result = await db.execute(
        select(URLClick.device_type, func.count(URLClick.id))
        .where(URLClick.clicked_at >= start_date)
        .group_by(URLClick.device_type)
    )
    device_stats = {device: count for device, count in device_result.all() if device}

    # Get browser breakdown
    browser_result = await db.execute(
        select(URLClick.browser, func.count(URLClick.id))
        .where(URLClick.clicked_at >= start_date)
        .group_by(URLClick.browser)
    )
    browser_stats = {
        browser: count for browser, count in browser_result.all() if browser
    }

    # Get daily click counts for the last 30 days
    daily_clicks_result = await db.execute(
        select(
            func.date(URLClick.clicked_at).label("date"),
            func.count(URLClick.id).label("count"),
        )
        .where(URLClick.clicked_at >= start_date)
        .group_by(func.date(URLClick.clicked_at))
        .order_by("date")
    )
    daily_clicks = {str(date): count for date, count in daily_clicks_result.all()}

    return AnalyticsSummary(
        total_clicks=total_clicks,
        clicks_in_range=range_clicks,
        unique_visitors=unique_visitors,
        date_range_days=days,
        device_breakdown=device_stats,
        browser_breakdown=browser_stats,
        top_referrers={},  # Not relevant for global stats
        daily_clicks=daily_clicks,
    )


async def cleanup_old_clicks(db: AsyncSession, days_to_keep: int = 90) -> int:
    """
    Delete old click analytics data.
    Returns the number of records deleted.
    """
    cutoff_date = datetime.now(UTC) - timedelta(days=days_to_keep)

    # First get the count of records to be deleted
    count_stmt = select(func.count(URLClick.id)).where(
        URLClick.clicked_at < cutoff_date
    )
    count_result = await db.execute(count_stmt)
    count: int = count_result.scalar() or 0

    # Only delete if there are records to delete
    if count > 0:
        stmt = delete(URLClick).where(URLClick.clicked_at < cutoff_date)
        await db.execute(stmt)
        await db.commit()

    return count


async def get_user_analytics_summary(
    db: AsyncSession, user_id: int, days: int = 30
) -> AnalyticsSummary:
    """
    Get analytics summary for all URLs owned by a user.
    """
    # Calculate date range
    start_date = datetime.now(UTC) - timedelta(days=days)

    # Get total clicks for user's URLs
    total_clicks_result = await db.execute(
        select(func.count(URLClick.id))
        .join(URLClick.url)
        .where(URLClick.url.has(user_id=user_id))
    )
    total_clicks: int = total_clicks_result.scalar() or 0

    # Get clicks in date range
    range_clicks_result = await db.execute(
        select(func.count(URLClick.id))
        .join(URLClick.url)
        .where(URLClick.url.has(user_id=user_id), URLClick.clicked_at >= start_date)
    )
    range_clicks: int = range_clicks_result.scalar() or 0

    # Get unique visitors (distinct IP addresses) in date range
    unique_visitors_result = await db.execute(
        select(func.count(func.distinct(URLClick.ip_address)))
        .join(URLClick.url)
        .where(URLClick.url.has(user_id=user_id), URLClick.clicked_at >= start_date)
    )
    unique_visitors: int = unique_visitors_result.scalar() or 0

    # Get device type breakdown
    device_result = await db.execute(
        select(URLClick.device_type, func.count(URLClick.id))
        .join(URLClick.url)
        .where(URLClick.url.has(user_id=user_id), URLClick.clicked_at >= start_date)
        .group_by(URLClick.device_type)
    )
    device_stats = {device: count for device, count in device_result.all() if device}

    # Get browser breakdown
    browser_result = await db.execute(
        select(URLClick.browser, func.count(URLClick.id))
        .join(URLClick.url)
        .where(URLClick.url.has(user_id=user_id), URLClick.clicked_at >= start_date)
        .group_by(URLClick.browser)
    )
    browser_stats = {
        browser: count for browser, count in browser_result.all() if browser
    }

    # Get daily click counts for the last 30 days
    daily_clicks_result = await db.execute(
        select(
            func.date(URLClick.clicked_at).label("date"),
            func.count(URLClick.id).label("count"),
        )
        .join(URLClick.url)
        .where(URLClick.url.has(user_id=user_id), URLClick.clicked_at >= start_date)
        .group_by(func.date(URLClick.clicked_at))
        .order_by("date")
    )
    daily_clicks = {str(date): count for date, count in daily_clicks_result.all()}

    return AnalyticsSummary(
        total_clicks=total_clicks,
        clicks_in_range=range_clicks,
        unique_visitors=unique_visitors,
        date_range_days=days,
        device_breakdown=device_stats,
        browser_breakdown=browser_stats,
        top_referrers={},  # Not calculated for user-wide stats
        daily_clicks=daily_clicks,
    )
