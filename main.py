import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.middleware.analytics import AnalyticsMiddleware
from app.models import Base
from app.routers import auth, shortener

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting FastAPI application...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown logic
    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title="URL Shortener API",
    description="A FastAPI URL shortener with analytics tracking",
    version="0.1.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(AnalyticsMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(shortener.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "URL Shortener API", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
