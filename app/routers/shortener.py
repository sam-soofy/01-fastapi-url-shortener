import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core.auth import get_current_active_user
from app.database import get_db

router = APIRouter(tags=["URL Shortener"])
logger = logging.getLogger(__name__)


@router.post(
    "/shorten", response_model=schemas.URLResponse, status_code=status.HTTP_201_CREATED
)
async def create_short_url(
    url_create: schemas.URLCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a shortened URL.

    - **original_url**: The URL to shorten (must be valid)
    - Returns the shortened URL information
    """
    try:
        db_url = await crud.create_url(db, url_create)
        logger.info(f"Created short URL: {db_url.short_code}")
        return db_url
    except Exception as e:
        logger.error(f"Error creating short URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Redirect to the original URL.

    - **short_code**: The short code from the shortened URL
    - Redirects to the original URL or returns 404 if not found
    """
    try:
        db_url = await crud.get_url_by_short_code(db, short_code)
        if db_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
            )

        # Get analytics data from middleware
        analytics_data = getattr(request.state, "analytics_data", {})

        # Create analytics record for the click
        await crud.create_click_analytics(
            db=db,
            url_id=db_url.id,
            ip_address=analytics_data.get("ip_address"),
            user_agent=analytics_data.get("user_agent"),
            referrer=analytics_data.get("referrer"),
        )

        # Increment click count (legacy support)
        await crud.increment_click_count(db, short_code)
        logger.info(f"Redirecting {short_code} to {db_url.original_url}")

        return RedirectResponse(
            url=db_url.original_url, status_code=status.HTTP_302_FOUND
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/stats/{short_code}", response_model=schemas.URLStats)
async def get_url_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    """
    Get statistics for a shortened URL.

    - **short_code**: The short code from the shortened URL
    - Returns URL statistics or 404 if not found
    """
    try:
        db_url = await crud.get_url_by_short_code(db, short_code)
        if db_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
            )

        return db_url

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting URL stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/analytics/{short_code}", response_model=schemas.AnalyticsSummary)
async def get_url_analytics(
    short_code: str, days: int = 30, db: AsyncSession = Depends(get_db)
):
    """
    Get detailed analytics for a shortened URL.

    - **short_code**: The short code from the shortened URL
    - **days**: Number of days to look back (default: 30)
    - Returns detailed analytics including device/browser breakdown
    """
    try:
        db_url = await crud.get_url_by_short_code(db, short_code)
        if db_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
            )

        analytics = await crud.get_url_analytics_summary(db, db_url.id, days=days)
        return analytics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting URL analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/analytics/global", response_model=schemas.AnalyticsSummary)
async def get_global_analytics(days: int = 30, db: AsyncSession = Depends(get_db)):
    """
    Get global analytics for all URLs.

    - **days**: Number of days to look back (default: 30)
    - Returns global analytics statistics
    """
    try:
        analytics = await crud.get_global_analytics_summary(db, days=days)
        return analytics

    except Exception as e:
        logger.error(f"Error getting global analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# User-specific endpoints (require authentication)


@router.post(
    "/user/shorten",
    response_model=schemas.URLResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_short_url(
    url_create: schemas.URLCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a shortened URL for the authenticated user.

    - **original_url**: The URL to shorten (must be valid)
    - Requires authentication
    - Returns the shortened URL information associated with the user
    """
    try:
        db_url = await crud.create_url(db, url_create, current_user.id)
        logger.info(
            f"User {current_user.username} created short URL: {db_url.short_code}"
        )
        return db_url
    except Exception as e:
        logger.error(f"Error creating user short URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/user/urls", response_model=list[schemas.URLResponse])
async def get_user_urls(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all URLs created by the authenticated user.

    - **skip**: Number of URLs to skip (pagination)
    - **limit**: Maximum number of URLs to return (pagination)
    - Requires authentication
    - Returns list of user's URLs
    """
    try:
        urls = await crud.get_urls_by_user(db, current_user.id, skip=skip, limit=limit)
        return urls
    except Exception as e:
        logger.error(f"Error getting user URLs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/user/urls/{url_id}", response_model=schemas.URLResponse)
async def get_user_url(
    url_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific URL by ID for the authenticated user.

    - **url_id**: ID of the URL to retrieve
    - Requires authentication
    - Only returns URLs owned by the authenticated user
    """
    try:
        db_url = await crud.get_url_by_id_and_user(db, url_id, current_user.id)
        if db_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
            )
        return db_url
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/user/urls/{url_id}", response_model=schemas.URLResponse)
async def update_user_url(
    url_id: int,
    url_update: schemas.URLCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a URL owned by the authenticated user.

    - **url_id**: ID of the URL to update
    - **original_url**: New URL to shorten
    - Requires authentication
    - Only allows updating URLs owned by the authenticated user
    """
    try:
        db_url = await crud.update_url(db, url_id, current_user.id, url_update)
        if db_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
            )
        logger.info(f"User {current_user.username} updated URL {url_id}")
        return db_url
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/user/urls/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_url(
    url_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a URL owned by the authenticated user.

    - **url_id**: ID of the URL to delete
    - Requires authentication
    - Only allows deleting URLs owned by the authenticated user
    """
    try:
        success = await crud.delete_url_by_user(db, url_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
            )
        logger.info(f"User {current_user.username} deleted URL {url_id}")
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
