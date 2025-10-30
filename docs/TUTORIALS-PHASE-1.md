# FastAPI URL Shortener Tutorial - Phase 1

## Table of Contents

1. [Starting a FastAPI Project](#starting-a-fastapi-project)
2. [Learning Through This Project](#learning-through-this-project)
3. [Routes and Controllers (Routers)](#routes-and-controllers-routers)
4. [Pydantic and Python Type Hints](#pydantic-and-python-type-hints)
5. [Data Validation and Sanitization](#data-validation-and-sanitization)
6. [Project Structure and Patterns](#project-structure-and-patterns)
7. [Async/Await in Python and FastAPI](#asyncawait-in-python-and-fastapi)
8. [SQLAlchemy for PostgreSQL](#sqlalchemy-for-postgresql)
9. [API Documentation with Swagger](#api-documentation-with-swagger)

## Starting a FastAPI Project

### Project Initialization

1. **Create Project Directory**:

   ```bash
   mkdir fastapi-url-shortener
   cd fastapi-url-shortener
   ```

2. **Initialize Python Project**:

   ```bash
   uv init
   # or: pip install uv && uv init
   ```

3. **Install Dependencies**:
   Create/modify `pyproject.toml`:

   ```toml
   [project]
   name = "fastapi-url-shortener"
   version = "0.1.0"
   requires-python = ">=3.12"
   dependencies = [
       "fastapi>=0.120.2",
       "uvicorn[standard]>=0.38.0",
       "sqlalchemy>=2.0.0",
       "asyncpg>=0.29.0",
       "aiosqlite>=0.20.0",
       "pydantic>=2.0.0",
       "validators>=0.28.0",
   ]
   ```

4. **Install Dependencies**:

   ```bash
   uv sync
   ```

### Basic FastAPI Application Setup

```python
# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Application starting...")
    yield
    # Shutdown logic
    logger.info("Application shutting down...")

app = FastAPI(
    title="URL Shortener API",
    description="A FastAPI URL shortener with analytics tracking",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "URL Shortener API", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### Running the Application

```bash
# Development mode with auto-reload
uv run uvicorn main:app --reload --port 8000

# Production mode
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# With Docker (if configured)
docker-compose up --build
```

## Learning Through This Project

### Recommended Learning Order

1. **Start with FastAPI Fundamentals**:
   - Read the [FastAPI documentation](https://fastapi.tiangolo.com/)
   - Understand routing, dependency injection, and request/response handling

2. **Study the Project Structure**:
   - Examine each file in the `app/` directory
   - Understand how modules are organized and imported

3. **Focus on Key Concepts**:
   - Start with synchronous endpoints, then move to async
   - Study Pydantic models and validation
   - Learn SQLAlchemy ORM patterns

4. **Practice by Modification**:
   - Add new endpoints
   - Modify existing schemas
   - Experiment with different validations

### Debugging Tips

- Use FastAPI's automatic documentation at `/docs`
- Enable SQLAlchemy query logging: `echo=True` in database config
- Use Python debugger: `import pdb; pdb.set_trace()`
- Check logs for database connections and errors

## Routes and Controllers (Routers)

### Router Structure

```python
# app/routers/shortener.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.database import get_db
import logging

router = APIRouter(tags=["URL Shortener"])
logger = logging.getLogger(__name__)
```

### Key Route Concepts

#### 1. **Path Parameters**

```python
@router.get("/{short_code}")
async def redirect_to_url(short_code: str, db: AsyncSession = Depends(get_db)):
    # short_code is extracted from URL path
```

#### 2. **Query Parameters**

```python
@router.get("/urls/")
async def get_urls(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # skip and limit are optional query parameters with defaults
```

#### 3. **Request Body**

```python
@router.post("/shorten", response_model=schemas.URLResponse)
async def create_short_url(
    url_create: schemas.URLCreate,  # Request body
    db: AsyncSession = Depends(get_db)
):
```

#### 4. **Response Models**

```python
@router.post("/shorten", response_model=schemas.URLResponse, status_code=status.HTTP_201_CREATED)
# response_model ensures returned data matches the schema
# status_code sets HTTP status for successful creation
```

#### 5. **Dependency Injection**

```python
async def create_short_url(db: AsyncSession = Depends(get_db)):
    # get_db dependency provides database session
    # Automatically injected for each request
```

### Controller Patterns Used

#### Separation of Concerns

- **Routes**: Handle HTTP requests/responses
- **CRUD**: Database operations
- **Schemas**: Data validation and serialization
- **Models**: Database table definitions

#### Error Handling

```python
try:
    result = await some_operation()
except SomeException as e:
    logger.error(f"Operation failed: {str(e)}")
    raise HTTPException(status_code=500, detail="Operation failed")
```

## Pydantic and Python Type Hints

### Python Type Hints Basics

```python
# Basic types
name: str
age: int
height: float
is_active: bool

# Collections
from typing import List, Dict, Optional
names: List[str]
user_data: Dict[str, str]
nickname: Optional[str] = None  # Can be None or string

# Custom classes
class User:
    pass

user: User
users: List[User]
```

### Pydantic Models

```python
# app/schemas/url.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    original_url: str = Field(..., description="The original URL to shorten")

class URLCreate(URLBase):
    # Field validators run automatically
    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not validators.url(v):
            raise ValueError("Invalid URL format")
        return v

class URLResponse(URLBase):
    id: int
    short_code: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM conversion
```

### Advanced Pydantic Features

#### Field Constraints

```python
class URLCreate(BaseModel):
    original_url: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Original URL to shorten"
    )
```

#### Custom Validators

```python
@field_validator("original_url")
@classmethod
def validate_url(cls, v: str) -> str:
    if not validators.url(v):
        raise ValueError("Invalid URL format")
    if len(v) > 2048:
        raise ValueError("URL too long")
    return v
```

#### Model Configuration

```python
class Config:
    from_attributes = True  # Convert ORM objects to Pydantic
    str_strip_whitespace = True  # Strip whitespace from strings
    validate_assignment = True  # Validate when assigning values
```

### Type Hints Benefits

1. **IDE Support**: Better autocomplete and error detection
2. **Runtime Validation**: Pydantic catches invalid data automatically
3. **Documentation**: Types serve as living documentation
4. **Refactoring**: Type checks help safe refactoring
5. **Development Speed**: Faster development with IDE assistance

## Data Validation and Sanitization

### Validation Layers

#### 1. **Pydantic Schema Validation**

- Automatic validation on request/response
- Custom field validators
- Type coercion and conversion

#### 2. **Business Logic Validation**

```python
# URL uniqueness check
async def create_url(db: AsyncSession, url_create: URLCreate) -> URL:
    # Check if URL already exists
    existing = await get_url_by_original_url(db, url_create.original_url)
    if existing:
        # Return existing instead of creating duplicate
        return existing
```

#### 3. **Database-Level Constraints**

```python
# app/models/url.py
class URL(Base):
    short_code = Column(String(8), unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    # unique=True prevents duplicates at database level
```

### Validation Examples

#### URL Format Validation

```python
import validators

@field_validator("original_url")
@classmethod
def validate_url(cls, v: str) -> str:
    if not validators.url(v):
        raise ValueError("Invalid URL format")
    return v
```

#### Length Validation

```python
@field_validator("original_url")
@classmethod
def validate_length(cls, v: str) -> str:
    if len(v) > 2048:
        raise ValueError("URL too long (max 2048 characters)")
    return v
```

### Sanitization Techniques

#### Input Cleaning

```python
@field_validator("original_url")
@classmethod
def clean_url(cls, v: str) -> str:
    # Remove whitespace
    v = v.strip()
    # Convert to lowercase for consistency
    return v.lower()
```

#### Output Sanitization

```python
class URLResponse(BaseModel):
    # Only include safe fields in responses
    short_code: str
    clicks: int
    # Don't expose internal IDs or sensitive data
```

## Project Structure and Patterns

### Directory Structure

```
fastapi-url-shortener/
├── app/                    # Main application package
│   ├── __init__.py        # Package marker
│   ├── main.py            # FastAPI application (relative import)
│   ├── database.py        # Database configuration
│   ├── models/            # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── url.py
│   ├── schemas/           # Pydantic schemas
│   │   ├── __init__.py
│   │   └── url.py
│   ├── crud/              # Database operations
│   │   ├── __init__.py
│   │   └── url.py
│   ├── routers/           # Route handlers
│   │   ├── __init__.py
│   │   └── shortener.py
│   └── core/              # Core functionality (for future)
├── docs/                  # Documentation
│   ├── plan.md
│   └── tutorials-phase-1.md
├── docker-compose.yml     # Docker services
├── Dockerfile            # Container configuration
├── pyproject.toml        # Project dependencies
├── uv.lock              # Dependency lock file
├── README.md            # Project documentation
└── .python-version      # Python version
```

### Design Patterns Used

#### 1. **Repository Pattern**

```python
# crud/url.py - Data access layer
async def create_url(db: AsyncSession, url_create: URLCreate) -> URL:
    # Repository handles data persistence
```

#### 2. **Service Layer Pattern**

```python
# routers/shortener.py - Business logic layer
async def create_short_url(url_create: schemas.URLCreate, db: AsyncSession):
    # Router handles HTTP concerns
    # Delegates data operations to CRUD layer
    db_url = await crud.create_url(db, url_create)
    return db_url
```

#### 3. **Factory Pattern**

```python
# Database session creation
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### 4. **Dependency Injection Pattern**

```python
# Routes use injected dependencies
async def create_short_url(db: AsyncSession = Depends(get_db)):
    # Database session injected automatically
    # Easy to test with mock sessions
```

#### 5. **Builder Pattern**

```python
# FastAPI app construction
app = FastAPI(
    title="URL Shortener API",
    description="Description",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(shortener.router, prefix="/api/v1")
# Router added to main app
```

### Code Organization Principles

#### **Separation of Concerns**

- Each module has a single responsibility
- Business logic separated from presentation
- Data access separated from business logic

#### **DRY (Don't Repeat Yourself)**

- Common validation logic in Pydantic validators
- Shared database session creation
- Reusable schema components

#### **SOLID Principles**

- **Single Responsibility**: Each class/function has one job
- **Open/Closed**: Models/schemas open for extension but closed for modification
- **Liskov Substitution**: Interface consistency
- **Interface Segregation**: Focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Async/Await in Python and FastAPI

### Synchronous vs Asynchronous

#### Synchronous (Blocking)

```python
# Each operation waits for the previous one
def synchronous_operation():
    result1 = database.query()  # Waits for DB
    result2 = api_call()        # Waits for API
    result3 = file_read()       # Waits for file
    return combine_results(result1, result2, result3)
```

#### Asynchronous (Non-blocking)

```python
# Operations can run concurrently
async def asynchronous_operation():
    # These start simultaneously
    task1 = database.query()
    task2 = api_call()
    task3 = file_read()

    # Wait for all to complete
    results = await asyncio.gather(task1, task2, task3)
    return combine_results(*results)
```

### FastAPI Async Features

#### 1. **Async Route Handlers**

```python
# app/routers/shortener.py
@app.post("/shorten")
async def create_short_url(url_create: schemas.URLCreate, db: AsyncSession):
    # Can use await for async database operations
    db_url = await crud.create_url(db, url_create)
    return db_url
```

#### 2. **Async Dependencies**

```python
# app/database.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### 3. **Async SQLAlchemy**

```python
# SQLAlchemy 2.0 async operations
async def get_url_by_short_code(db: AsyncSession, short_code: str):
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    return result.scalars().first()
```

#### 4. **Async Context Managers**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - runs before app starts
    await initialize_database()
    yield
    # Cleanup - runs when app shuts down
    await close_database_connections()
```

### Async Benefits in FastAPI

#### **Concurrency**

- Handle multiple requests simultaneously
- Better resource utilization
- Improved throughput under load

#### **I/O Operations**

```python
# FastAPI handles async I/O automatically
@app.get("/data")
async def get_data():
    # Network calls, file I/O, DB queries are all async
    data = await fetch_from_api()
    return data
```

#### **Scalability**

- Single thread can handle thousands of concurrent connections
- Efficient use of system resources
- Horizontal scaling friendly

### Async Pitfalls to Avoid

#### **Don't Use async for CPU-bound Tasks**

```python
# Wrong - blocks event loop
async def cpu_heavy_task():
    result = heavy_computation()  # CPU intensive
    return result

# Right - use ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()

async def cpu_heavy_task():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, heavy_computation)
    return result
```

#### **Always await Async Functions**

```python
# Wrong - doesn't actually wait
async def create_url():
    db_url = crud.create_url(db, url_data)  # Missing await
    return db_url

# Right - properly awaits
async def create_url():
    db_url = await crud.create_url(db, url_data)  # Correct
    return db_url
```

## SQLAlchemy for PostgreSQL

### ORM Basics

#### Model Definition

```python
# app/models/url.py
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String(8), unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### Database Types

- `String`: VARCHAR/text fields
- `Integer`: INT fields
- `DateTime`: TIMESTAMP fields
- `Boolean`: BOOLEAN fields
- `Float`: DECIMAL/FLOAT fields

#### Constraints and Indexes

```python
short_code = Column(
    String(8),
    unique=True,      # Prevents duplicates
    index=True,       # Creates index for fast lookups
    nullable=False    # Required field
)
```

### Async SQLAlchemy Operations

#### Connection Setup

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

#### CRUD Operations

```python
# Create
async def create_url(db: AsyncSession, url_create: URLCreate) -> URL:
    db_url = URL(
        original_url=url_create.original_url,
        short_code=generate_short_code(),
        clicks=0
    )
    db.add(db_url)           # Add to session
    await db.commit()        # Save to database
    await db.refresh(db_url) # Refresh with database values
    return db_url

# Read
async def get_url_by_short_code(db: AsyncSession, short_code: str) -> Optional[URL]:
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    return result.scalars().first()

# Update
async def increment_click_count(db: AsyncSession, short_code: str) -> bool:
    from sqlalchemy import update
    result = await db.execute(
        update(URL)
        .where(URL.short_code == short_code)
        .values(clicks=URL.clicks + 1)
    )
    await db.commit()
    return result.rowcount > 0

# Delete
async def delete_url(db: AsyncSession, url_id: int) -> bool:
    db_url = await get_url_by_id(db, url_id)
    if db_url:
        await db.delete(db_url)
        await db.commit()
        return True
    return False
```

### Query Building

#### Basic Queries

```python
# Select with WHERE
query = select(URL).where(URL.short_code == "abc123")

# Select with multiple conditions
query = select(URL).where(
    (URL.clicks > 10) &
    (URL.created_at > datetime.now() - timedelta(days=7))
)

# Order and limit
query = select(URL).order_by(URL.created_at.desc()).limit(10)
```

#### Joins and Relationships

```python
# If we had a User model with relationship to URLs
query = select(URL).join(User).where(User.id == user_id)

# Eager loading relationships
query = select(URL).options(joinedload(URL.user))
```

#### Aggregations

```python
from sqlalchemy import func

# Count URLs
total_count = await db.execute(select(func.count(URL.id)))

# Sum clicks
total_clicks = await db.execute(select(func.sum(URL.clicks)))

# Group by with aggregations
stats = await db.execute(
    select(
        func.date(URL.created_at),
        func.count(URL.id),
        func.sum(URL.clicks)
    )
    .group_by(func.date(URL.created_at))
)
```

### Migrations

#### Creating Tables

```python
# In lifespan event or startup script
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

#### Migration Scripts (Production)

```bash
# Using Alembic (recommended for production)
alembic init alembic
alembic revision --autogenerate -m "Create URL table"
alembic upgrade head
```

### Best Practices

#### 1. **Session Management**

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### 2. **Avoid N+1 Queries**

```python
# Bad - N+1 queries
urls = await db.execute(select(URL).limit(10))
for url in urls:
    user = await db.execute(select(User).where(User.id == url.user_id))
    # Executes N additional queries

# Good - Single query with join
urls = await db.execute(
    select(URL).options(joinedload(URL.user)).limit(10)
)
```

#### 3. **Transaction Management**

```python
async with db.begin():
    # All operations in this block are in a transaction
    db_url = URL(...)
    db.add(db_url)

    # If any operation fails, all are rolled back
    await some_external_api_call()
```

#### 4. **Connection Pooling**

Configurable in engine:

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,         # Max connections
    max_overflow=20,      # Extra connections when pool is full
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

## API Documentation with Swagger

### Automatic Documentation

FastAPI automatically generates OpenAPI documentation from your code:

```python
app = FastAPI(
    title="URL Shortener API",
    description="A FastAPI URL shortener with analytics tracking",
    version="1.0.0"
)
```

### Interactive Documentation

#### Swagger UI

- **URL**: `http://localhost:8000/docs`
- **Features**:
  - Interactive API testing
  - Request/response examples
  - Authentication testing
  - Schema visualization

#### ReDoc

- **URL**: `http://localhost:8000/redoc`
- **Features**:
  - Clean, readable documentation
  - Server selection
  - Advanced schema documentation

#### OpenAPI JSON

- **URL**: `http://localhost:8000/openapi.json`
- **Features**:
  - Machine-readable API specification
  - Used by code generators
  - Integrates with API gateways

### Documenting Routes

#### Function Docstrings

```python
@router.post("/shorten")
async def create_short_url(url_create: schemas.URLCreate, db: AsyncSession):
    """
    Create a shortened URL.

    - **original_url**: The URL to shorten (must be valid)
    - Returns the shortened URL information
    """
```

#### Response Documentation

```python
@router.get("/stats/{short_code}")
async def get_url_stats(short_code: str):
    """
    Get statistics for a shortened URL.

    - **short_code**: The short code from the shortened URL
    - Returns URL statistics or 404 if not found
    """
    return {"short_code": short_code, "clicks": 42}
```

#### Parameter Documentation

```python
@router.get("/urls/")
async def get_urls(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return")
):
    """Get list of URLs with pagination."""
```

### Schema Documentation

#### Field Descriptions

```python
class URLCreate(BaseModel):
    original_url: str = Field(
        ...,
        description="The original URL to shorten",
        example="https://example.com/long-url"
    )
```

#### Response Models

```python
@router.post("/shorten", response_model=URLResponse)
async def create_short_url(url_create: URLCreate):
    # Response automatically validated against URLResponse schema
    return URLResponse(id=1, short_code="abc123", ...)
```

#### Error Responses

```python
@router.get("/{short_code}")
async def redirect_to_url(short_code: str):
    """
    responses:
        302:
            description: Redirect to the original URL
        404:
            description: URL not found
        500:
            description: Internal server error
    """
```

### Advanced Documentation Features

#### Authentication Documentation

```python
security_schemes = {
    "Bearer": {"type": "http", "scheme": "bearer"}
}

app = FastAPI(
    security=[{"Bearer": []}],
    components={"securitySchemes": security_schemes}
)
```

#### Tags and Grouping

```python
router = APIRouter(tags=["URL Shortener"])

# Or for multiple tags
@router.post("/shorten", tags=["URLs", "Create"])
```

#### Custom Examples

```python
class URLCreate(BaseModel):
    original_url: str = Field(
        ...,
        examples=["https://google.com", "https://github.com/user/repo"]
    )
```

### Documentation Testing

#### Using Swagger UI

1. Open `http://localhost:8000/docs`
2. Select an endpoint
3. Click "Try it out"
4. Enter test data
5. Click "Execute"
6. View response

#### Using OpenAPI Spec

```python
import requests

# Get API specification
spec = requests.get("http://localhost:8000/openapi.json").json()

# Validate with third-party tools
import openapi_spec_validator
openapi_spec_validator.validate(spec)
```

### Best Practices

#### **Clear Descriptions**

- Use descriptive endpoint summaries
- Explain parameters and their purposes
- Document response formats

#### **Consistent Naming**

- Use RESTful naming conventions
- Keep parameter names consistent
- Use standard HTTP methods

#### **Versioning**

```python
app = FastAPI(
    title="URL Shortener API v1",
    version="1.0.0",
    servers=[
        {"url": "/api/v1", "description": "Production server"}
    ]
)
```

#### **Security Documentation**

- Document authentication requirements
- Specify authorization scopes
- Include rate limiting information

### Automation and CI/CD

#### **Documentation Generation**

```python
# Generate documentation in CI/CD
import json
from fastapi.openapi.utils import get_openapi

def export_openapi():
    openapi_schema = get_openapi(
        title="URL Shortener API",
        version="1.0.0",
        routes=app.routes,
    )

    with open("docs/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
```

#### **Documentation Testing**

```python
# Test that documentation is accessible
def test_api_docs():
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
```

---

## Learning Path Forward

1. **Experiment**: Modify existing endpoints and schemas
2. **Extend**: Add new features like custom short codes or analytics
3. **Test**: Write tests for CRUD operations
4. **Deploy**: Set up Docker and deployment pipeline
5. **Scale**: Add caching, rate limiting, and monitoring

Remember: **Learning by doing** is the most effective way. Start small, experiment often, and gradually build complexity.
