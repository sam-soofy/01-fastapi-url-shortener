from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.database import get_db
import logging

router = APIRouter(tags=["URL Shortener"])
logger = logging.getLogger(__name__)


@router.post("/shorten", response_model=schemas.URLResponse, status_code=status.HTTP_201_CREATED)
async def create_short_url(
    url_create: schemas.URLCreate,
    db: AsyncSession = Depends(get_db)
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
            detail="Internal server error"
        )


@router.get("/{short_code}")
async def redirect_to_url(short_code: str, db: AsyncSession = Depends(get_db)):
    """
    Redirect to the original URL.

    - **short_code**: The short code from the shortened URL
    - Redirects to the original URL or returns 404 if not found
    """
    try:
        db_url = await crud.get_url_by_short_code(db, short_code)
        if db_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )

        # Increment click count
        await crud.increment_click_count(db, short_code)
        logger.info(f"Redirecting {short_code} to {db_url.original_url}")

        return RedirectResponse(url=db_url.original_url, status_code=status.HTTP_302_FOUND)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )

        return db_url

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting URL stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
