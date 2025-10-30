from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app import crud, schemas, models
from app.database import get_db
from app.core.auth import create_access_token, get_current_active_user

router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.

    - **username**: Unique username (alphanumeric, underscores, hyphens only)
    - **email**: Valid email address
    - **password**: Password must contain uppercase, lowercase, digit, and special character
    """
    try:
        # Create the user
        db_user = await crud.create_user(db, user_data)
        logger.info(f"User registered: {db_user.username}")
        return db_user

    except ValueError as e:
        # Handle duplicate username/email
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/login", response_model=schemas.Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access token.

    - **username**: Username or email address
    - **password**: User password
    """
    try:
        # Authenticate user
        user = await crud.authenticate_user(db, form_data.username, form_data.password)

        if not user:
            logger.warning(f"Failed login attempt for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        logger.info(f"User logged in: {user.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_profile(
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get current user's profile information.

    Requires authentication.
    """
    try:
        return current_user
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me/urls", response_model=schemas.UserWithUrls)
async def get_current_user_urls(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's URLs with details.

    Requires authentication.
    """
    try:
        # Get user with their URLs loaded
        user_with_urls = await crud.get_user_with_urls(db, current_user.id)
        if not user_with_urls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user_with_urls

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user URLs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
