# Phase 3: Async Features and Background Tasks

## Overview

Phase 3 enhances the FastAPI URL shortener with comprehensive async operations and detailed analytics tracking. This phase focuses on implementing background processing for analytics, detailed click tracking, and data maintenance tasks.

## Learning Objectives

- Implement advanced async patterns throughout the application
- Create detailed analytics tracking for URL clicks
- Add middleware for request tracking and analytics collection
- Implement background tasks for data processing and maintenance
- Build comprehensive analytics reporting endpoints

## New Dependencies Added

```toml
"werkzeug>=2.0.0",        # Password hashing
"user-agents>=2.2.0",     # User agent parsing
```

## Database Schema Changes

### New Analytics Model

```python
class URLClick(Base):
    __tablename__ = "url_clicks"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    country = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    device_type = Column(String(20), nullable=True)  # mobile, desktop, tablet
    browser = Column(String(50), nullable=True)

    # Relationship to URL
    url = relationship("URL", back_populates="click_data")
```

### Updated URL Model

```python
class URL(Base):
    # ... existing fields ...

    # Relationship to URL clicks
    click_data = relationship("URLClick", back_populates="url", cascade="all, delete-orphan")
```

## Analytics Processing Architecture

### Middleware Layer

The `AnalyticsMiddleware` captures analytics data for every request:

```python
class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract analytics data
        analytics_data = self._extract_request_data(request)

        # Store in request state for use by endpoints
        request.state.analytics_data = analytics_data

        # Process request
        response = await call_next(request)
        return response
```

### Enhanced Redirect Endpoint

The redirect endpoint now captures detailed analytics:

```python
@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    db_url = await crud.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Extract analytics data from middleware
    analytics_data = getattr(request.state, "analytics_data", {})

    # Create detailed analytics record
    await crud.create_click_analytics(
        db=db,
        url_id=db_url.id,
        ip_address=analytics_data.get("ip_address"),
        user_agent=analytics_data.get("user_agent"),
        referrer=analytics_data.get("referrer"),
    )

    # Legacy click counting (for backwards compatibility)
    await crud.increment_click_count(db, short_code)

    return RedirectResponse(url=db_url.original_url, status_code=302)
```

## Analytics CRUD Operations

### Click Analytics Creation

```python
async def create_click_analytics(
    db: AsyncSession,
    url_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None,
) -> URLClick:
    # Parse user agent for device/browser info
    device_type = browser = None
    if user_agent:
        ua = user_agents.parse(user_agent)
        device_type = "mobile" if ua.is_mobile else ("tablet" if ua.is_tablet else "desktop")
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
```

### Analytics Summary Generation

```python
async def get_url_analytics_summary(
    db: AsyncSession,
    url_id: int,
    days: int = 30
) -> AnalyticsSummary:
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)

    # Aggregate analytics data
    # - Total clicks
    # - Clicks in date range
    # - Device breakdown
    # - Browser breakdown
    # - Top referrers
    # - Daily click counts

    return AnalyticsSummary(...)
```

## Analytics Reporting Endpoints

### Individual URL Analytics

```python
@router.get("/analytics/{short_code}", response_model=schemas.AnalyticsSummary)
async def get_url_analytics(
    short_code: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analytics for a shortened URL."""
    db_url = await crud.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    analytics = await crud.get_url_analytics_summary(db, db_url.id, days=days)
    return analytics
```

### Global Analytics

```python
@router.get("/analytics/global", response_model=schemas.AnalyticsSummary)
async def get_global_analytics(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get global analytics for all URLs."""
    analytics = await crud.get_global_analytics_summary(db, days=days)
    return analytics
```

## User Analytics

### User-Specific Analytics Summary

```python
async def get_user_analytics_summary(
    db: AsyncSession,
    user_id: int,
    days: int = 30
) -> AnalyticsSummary:
    """Get analytics summary for all URLs owned by a user."""
    # Aggregates analytics across all user's URLs
```

## Background Tasks and Maintenance

### Data Cleanup Function

```python
async def cleanup_old_clicks(
    db: AsyncSession,
    days_to_keep: int = 90
) -> int:
    """Delete old click analytics data. Returns deleted count."""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    result = await db.execute(
        delete(URLClick).where(URLClick.clicked_at < cutoff_date)
    )
    await db.commit()
    return result.rowcount
```

## Pydantic Schemas

### Analytics Summary Schema

```python
class AnalyticsSummary(BaseModel):
    total_clicks: int
    clicks_in_range: int
    date_range_days: int
    device_breakdown: Dict[str, int]      # device_type: count
    browser_breakdown: Dict[str, int]     # browser: count
    top_referrers: Dict[str, int]         # referrer: count
    daily_clicks: Dict[str, int]          # date: count
```

### URL Click Response Schema

```python
class URLClickResponse(BaseModel):
    id: int
    clicked_at: datetime
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    country: Optional[str] = None
```

## Testing the Analytics System

### Basic Functionality Test

```bash
# Create a URL
curl -X POST "http://localhost:8000/api/v1/shorten" \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://example.com"}'
# Response: {"id": 1, "short_code": "abc123", "clicks": 0, ...}

# Access the shortened URL
curl -H "Referer: https://google.com" \
     "http://localhost:8000/api/v1/abc123"

# Get analytics
curl "http://localhost:8000/api/v1/analytics/abc123"
# Response includes device breakdowns, referrers, etc.
```

### Middleware Verification

```bash
# Check middleware is working
curl "http://localhost:8000/"
# Should see log entries with User-Agent/IP tracking
```

## Performance Considerations

### Efficient Analytics Queries

- Uses database indexes on frequently queried fields
- Aggregates data using SQL functions (COUNT, GROUP BY)
- Paginates large result sets
- Removes old data automatically (configurable retention)

### Async Database Operations

- All analytics operations are fully async
- Uses SQLAlchemy async sessions throughout
- Non-blocking I/O for analytics processing

## Security and Privacy

### Data Retention

- Analytics data is cleaned up after 90 days by default
- Configurable cleanup interval
- No permanent storage of sensitive tracking data

### Privacy Controls

- IP addresses collected but not exposed in public APIs
- User agent parsing for analytics only (not stored long-term)
- Click data anonymized by aggregation

## Phase 3 API Endpoints Summary

```
GET    /api/v1/analytics/{short_code}    # URL analytics
GET    /api/v1/analytics/global          # Global analytics
```

## Next Steps

Phase 3 is complete! The application now features:

- ✅ Comprehensive analytics tracking
- ✅ Async database operations throughout
- ✅ Middleware for request tracking
- ✅ Background cleanup processes
- ✅ Detailed reporting and aggregation

**Ready for Phase 4: Caching and Rate Limiting with Redis**

The analytics foundation is now solid and can be extended with caching layers and rate limiting in the next phase.
