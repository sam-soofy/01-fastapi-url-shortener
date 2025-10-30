# FastAPI URL Shortener Tutorial - Phase 2: User Authentication

## Table of Contents

1. [Continuing from Phase 1](#continuing-from-phase-1)
2. [Learning Through Phase 2](#learning-through-phase-2)
3. [User Authentication and Authorization](#user-authentication-and-authorization)
4. [JWT Tokens and Security](#jwt-tokens-and-security)
5. [Database Relationships with Users](#database-relationships-with-users)
6. [Advanced Pydantic Validation](#advanced-pydantic-validation)
7. [Password Security and Hashing](#password-security-and-hashing)
8. [User-Specific URL Management](#user-specific-url-management)
9. [Authentication Endpoints](#authentication-endpoints)
10. [Testing Authentication](#testing-authentication)
11. [Security Best Practices Learned](#security-best-practices-learned)

## Continuing from Phase 1

### Prerequisites

Before starting Phase 2, ensure you have:

- ✅ Phase 1 completed (basic URL shortening)
- ✅ FastAPI, SQLAlchemy, and PostgreSQL running
- ✅ Basic understanding of async operations
- ✅ Docker environment set up

### Moving to Phase 2

Phase 2 introduces **user management and security** to our URL shortener. This adds complexity but teaches essential real-world skills.

### Quick Setup for Phase 2

```bash
# Ensure you're on the right branch/commit
git checkout phase-2

# Install new dependencies (if not already installed)
uv add "werkzeug>=2.0.0" "PyJWT>=2.0.0" "email-validator>=2.0.0"

# Start the application
uv run uvicorn main:app --reload --port 8000
```

## Learning Through Phase 2

### What's New in Phase 2?

Phase 2 adds complete user authentication and authorization:

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| URL Creation | ✅ Anonymous | ✅ Anonymous + Authenticated |
| User Management | ❌ None | ✅ Registration/Login |
| Security | ❌ None | ✅ JWT, Password Hashing |
| Data Validation | ✅ Basic | ✅ Advanced + Security |
| API Endpoints | ✅ Public | ✅ Public + Protected |
| Database | ✅ Single table | ✅ Multiple tables + Relationships |

### Recommended Learning Order

1. **Study Database Models**: Understand user relationships
2. **Learn JWT Authentication**: Master token-based security
3. **Explore Password Security**: Understand hashing and validation
4. **Master Authorization**: Learn user-specific operations
5. **Practice Advanced Validation**: Study Pydantic validators
6. **Experiment with Protected Routes**: Test authentication flows

### Key Learning Goals

After completing Phase 2, you'll understand:

- **JWT Authentication**: Token-based user sessions
- **Password Security**: Hashing, salting, and storage
- **Database Relationships**: User ownership and cascading
- **Advanced Validation**: Security-focused input validation
- **Authorization**: Protecting resources by user
- **API Security**: Headers, tokens, and error responses

## User Authentication and Authorization

### Authentication vs Authorization

#### What is Authentication?

```python
# Authentication answers: "Who are you?"
# Example: Verifying username/password combination

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if user and user.check_password(password):
        return user  # ✅ Authentication successful
    return None     # ❌ Authentication failed
```

#### What is Authorization?

```python
# Authorization answers: "What can you do?"
# Example: Check if user owns the URL

async def get_user_url(url_id: int, current_user: User, db: AsyncSession):
    url = await get_url_by_id_and_user(db, url_id, current_user.id)
    if not url:
        raise HTTPException(403, "You don't own this URL")  # ❌ Not authorized
    return url  # ✅ Authorized
```

### Authentication Flow

```
1. User registers: POST /api/v1/auth/register
   ↓
2. System creates user with hashed password
   ↓
3. User logs in: POST /api/v1/auth/login
   ↓
4. System validates credentials, issues JWT token
   ↓
5. User includes token in: Authorization: Bearer <token>
   ↓
6. System validates token, provides access
```

### Authorization Levels

```python
# app/core/auth.py
async def get_current_user(token: str) -> User:
    """Require authentication - any logged-in user"""
    return user

async def get_current_active_user(user: User) -> User:
    """Check user status - placeholder for future features"""
    # Could check: account active, email verified, etc.
    return user
```

## JWT Tokens and Security

### What are JWT Tokens?

JWT (JSON Web Tokens) are secure tokens for user sessions:

```
Header:       Payload:               Signature:
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9  .  eyJzdWIiOiJ1c2VyMTIzIiwiaWF0IjoxNjQzODAwMDAwfQ  .  signature_hash
```

#### JWT Components

1. **Header**: Algorithm and token type

   ```json
   {"typ": "JWT", "alg": "HS256"}
   ```

2. **Payload**: User data and claims

   ```json
   {"sub": "username", "iat": 1643800000, "exp": 1643803600}
   ```

3. **Signature**: Ensures token integrity

   ```
   HMACSHA256(base64(header) + "." + base64(payload), secret_key)
   ```

### JWT in Our Application

#### Token Configuration

```python
# app/core/auth.py
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

#### Token Creation

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### Token Verification

```python
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(401, detail="Invalid authentication credentials")
```

### FastAPI JWT Integration

#### HTTP Bearer Authentication

```python
# app/core/auth.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = verify_token(credentials.credentials)
    username = payload.get("sub")

    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(401, detail="User not found")

    return user
```

#### Using Authentication in Routes

```python
@router.post("/user/shorten")
async def create_user_url(
    url_data: URLCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # current_user automatically injected from JWT token
    db_url = await crud.create_url(db, url_data, current_user.id)
    return db_url
```

### JWT Security Best Practices

#### Our Implementation ✓

```python
# ✅ Short expiration time (30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ✅ Strong secret key (should be from environment)
SECRET_KEY = os.getenv("SECRET_KEY")

# ✅ Secure algorithm (HMAC-SHA256)
ALGORITHM = "HS256"

# ✅ Proper error handling without exposing details
except jwt.PyJWTError:
    raise HTTPException(401, detail="Invalid authentication credentials")
```

#### Additional Security Measures (For Future)

```python
# Refresh tokens (not implemented yet)
# Token blacklisting (not implemented yet)
# Rate limiting authentication attempts
# Account lockout after failed attempts
```

## Database Relationships with Users

### User Model Design

```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to URLs
    urls = relationship("URL", back_populates="user", cascade="all, delete")

    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the user's password"""
        return check_password_hash(self.hashed_password, password)
```

### URL-User Relationship

```python
# app/models/url.py - Updated URL model
class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String(8), unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign key to user (nullable for backwards compatibility)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship to User
    user = relationship("User", back_populates="urls")
```

### Understanding Relationships

#### One-to-Many Relationship

```
┌─────────┐       ┌─────────┐
│   User  │──────▶│   URL   │
│         │       │         │
│ id: 1   │       │ id: 1   │
│ username│       │ user_id │
│ "john"  │       │ 1       │
└─────────┘       └─────────┘
                  ┌─────────┐
                  │ id: 2   │
                  │ user_id │
                  │ 1       │
                  └─────────┘
```

#### SQLAlchemy Relationship Benefits

```python
# Accessing user URLs
user = await get_user_with_urls(db, user_id)
for url in user.urls:  # Automatic loading via relationship
    print(f"Short code: {url.short_code}")

# Creating URL with user
url = URL(original_url="https://example.com", user_id=user.id)
# OR
url = URL(original_url="https://example.com", user=user)
```

#### Cascading Deletes

```python
# When user is deleted, all their URLs are deleted automatically
urls = relationship("URL", back_populates="user", cascade="all, delete")
```

### Querying with Relationships

#### Get User's URLs

```python
async def get_urls_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(URL).where(URL.user_id == user_id)
    )
    return result.scalars().all()
```

#### Get URL with User Info

```python
async def get_url_with_user(db: AsyncSession, url_id: int):
    result = await db.execute(
        select(URL).options(joinedload(URL.user)).where(URL.id == url_id)
    )
    return result.scalars().first()
```

#### Check URL Ownership

```python
async def get_url_by_id_and_user(db: AsyncSession, url_id: int, user_id: int):
    result = await db.execute(
        select(URL).where(
            (URL.id == url_id) &
            (URL.user_id == user_id)
        )
    )
    return result.scalars().first()
```

## Advanced Pydantic Validation

### User Schema Validation

```python
# app/schemas/user.py
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
```

### Custom Field Validators

#### Username Validation

```python
@field_validator("username")
@classmethod
def validate_username(cls, v: str) -> str:
    """Validate username format and security"""
    if not re.match(r'^[a-zA-Z0-9_-]+$', v):
        raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")

    # Security: prevent common admin usernames
    if v.lower() in ['admin', 'root', 'superuser', 'administrator']:
        raise ValueError("This username is not allowed")

    return v
```

#### Password Strength Validation

```python
@field_validator("password")
@classmethod
def validate_password(cls, v: str) -> str:
    """Enforce strong password requirements"""
    if not re.search(r'[A-Z]', v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', v):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', v):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        raise ValueError("Password must contain at least one special character")
    return v
```

### Email Validation with email-validator

```python
# In pyproject.toml
dependencies = [
    "email-validator>=2.0.0",  # For EmailStr validation
    # ... other dependencies
]

# In schemas
from pydantic import EmailStr

class UserCreate(BaseModel):
    email: EmailStr  # Automatic email format validation
```

### Validation Error Handling

#### FastAPI Automatic Responses

```python
# Input validation errors automatically return detailed responses
{
    "detail": [
        {
            "loc": ["body", "username"],
            "msg": "Username can only contain letters, numbers, underscores, and hyphens",
            "type": "value_error"
        }
    ]
}
```

#### Custom Error Messages

```python
# In your route handlers
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e)
    )
```

## Password Security and Hashing

### Why Hash Passwords?

Plain text storage is dangerous:

```python
# ❌ NEVER DO THIS
user.password = "mypassword123"

# Investigations show passwords in databases get leaked!
# Hackers can use stolen passwords on other sites
```

### Werkzeug Password Hashing

#### Installing and Using

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash password
hashed = generate_password_hash("mypassword123")
# Result: "pbkdf2:sha256:260000$salt$hash"

# Verify password
is_valid = check_password_hash(hashed, "mypassword123")  # True
is_valid = check_password_hash(hashed, "wrongpassword")  # False
```

#### Integration in User Model

```python
class User(Base):
    hashed_password = Column(String(128), nullable=False)

    def set_password(self, password: str):
        """Hash and store password"""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.hashed_password, password)
```

### PBKDF2 Hashing Algorithm

Werkzeug uses PBKDF2 (Password-Based Key Derivation Function 2):

```
PBKDF2_SHA256(iterations=260000, salt=random, password)
↓
Hashed password stored in database
```

#### Security Features

- **Salt**: Random value prevents rainbow table attacks
- **Iterations**: Slows down brute force attacks
- **SHA256**: Cryptographically secure hash function

### Password Security Best Practices

#### Our Implementation ✓

```python
# ✅ Secure hashing with salt and many iterations
set_password() uses generate_password_hash()

# ✅ Constant-time comparison
check_password() uses check_password_hash()

# ✅ Strong password requirements via validation
# ✅ No plaintext password storage
# ✅ Proper error messages (no password hints)
```

#### Future Enhancements

```python
# Password reset functionality
# Account lockout after failed attempts
# Password history (prevent reuse)
# Two-factor authentication
```

## User-Specific URL Management

### Authentication-Required Endpoints

#### Creating User URLs

```python
@router.post("/user/shorten", response_model=schemas.URLResponse)
async def create_user_short_url(
    url_create: schemas.URLCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # User association automatic
    db_url = await crud.create_url(db, url_create, current_user.id)
    return db_url
```

#### Accessing User URLs

```python
@router.get("/user/urls", response_model=List[schemas.URLResponse])
async def get_user_urls(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Only return URLs owned by authenticated user
    urls = await crud.get_urls_by_user(db, current_user.id)
    return urls
```

### Authorization Checks

#### URL Ownership Verification

```python
async def update_url(
    db: AsyncSession,
    url_id: int,
    user_id: int,
    url_update: URLCreate
) -> Optional[URL]:
    # Ensure user owns the URL
    db_url = await get_url_by_id_and_user(db, url_id, user_id)
    if not db_url:
        return None  # Not authorized

    db_url.original_url = url_update.original_url
    await db.commit()
    return db_url
```

### CRUD Operations with Authorization

#### List User URLs with Pagination

```python
@router.get("/user/urls")
async def get_user_urls(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_urls_by_user(db, current_user.id, skip, limit)
```

#### Update Specific URL

```python
@router.put("/user/urls/{url_id}")
async def update_user_url(
    url_id: int,
    url_update: URLCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    url = await crud.update_url(db, url_id, current_user.id, url_update)
    if not url:
        raise HTTPException(404, "URL not found or not owned by you")
    return url
```

#### Delete User URL

```python
@router.delete("/user/urls/{url_id}")
async def delete_user_url(
    url_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_url_by_user(db, url_id, current_user.id)
    if not success:
        raise HTTPException(404, "URL not found or not owned by you")
    return {"message": "URL deleted successfully"}
```

## Authentication Endpoints

### Registration Endpoint

```python
@router.post("/auth/register", response_model=UserResponse, status_code=201)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.

    Validates username/email uniqueness and password strength.
    Creates user with hashed password.
    """
    # Validation handled by Pydantic + CRUD layer
    db_user = await crud.create_user(db, user_data)
    return db_user
```

### Login Endpoint

```python
@router.post("/auth/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    Accepts username or email for login.
    Returns bearer token for authenticated requests.
    """
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Incorrect username/email or password")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

### User Profile Endpoints

```python
@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user's profile information."""
    return current_user

@router.get("/auth/me/urls", response_model=UserWithUrls)
async def get_current_user_urls(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Get current user's URLs with full details."""
    return await crud.get_user_with_urls(db, current_user.id)
```

### API Endpoint Summary

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/auth/register` | POST | ❌ | Create new user account |
| `/auth/login` | POST | ❌ | Authenticate and get token |
| `/auth/me` | GET | ✅ | Get current user profile |
| `/auth/me/urls` | GET | ✅ | Get user's URLs |
| `/user/shorten` | POST | ✅ | Create URL for user |
| `/user/urls` | GET | ✅ | List user's URLs |
| `/user/urls/{id}` | GET | ✅ | Get specific user URL |
| `/user/urls/{id}` | PUT | ✅ | Update user URL |
| `/user/urls/{id}` | DELETE | ✅ | Delete user URL |
| `/shorten` | POST | ❌ | Public URL creation (unchanged) |
| `/{short_code}` | GET | ❌ | Public URL redirection (unchanged) |
| `/stats/{short_code}` | GET | ❌ | Public URL stats (unchanged) |

## Testing Authentication

### Manual Testing with Swagger

1. **Start the server**: `uv run uvicorn main:app --reload`
2. **Open documentation**: `http://localhost:8000/docs`

#### Register a User

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

#### Login to Get Token

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=SecurePass123!
```

Response includes:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Use Token for Authenticated Requests

```bash
GET /api/v1/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

GET /api/v1/user/urls
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Testing Edge Cases

#### Invalid Credentials

```bash
POST /api/v1/auth/login
username=wronguser&password=wrongpass
# Should return 401 Unauthorized
```

#### Missing Token

```bash
GET /api/v1/auth/me
# Should return 401 Unauthorized with Bearer challenge
```

#### Token Expiration

```bash
# Wait 30+ minutes after login, then try authenticated request
GET /api/v1/auth/me
Authorization: Bearer <expired_token>
# Should return 401 Unauthorized
```

### Testing with curl

```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123!"}'

# Login and get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=TestPass123!" | jq -r .access_token)

# Use token for authenticated request
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

## Security Best Practices Learned

### Phase 2 Security Features

#### ✅ Authentication & Authorization

- JWT-based user identification
- Password hashing with salt and iterations
- User-specific resource protection
- Token expiration (30 minutes)

#### ✅ Input Validation

- Email format validation
- Strong password requirements
- Username format restrictions
- SQL injection prevention (ORM)

#### ✅ Error Handling

- Generic error messages (no data leakage)
- Proper HTTP status codes
- Auth challenge headers
- Structured error responses

#### ✅ Data Protection

- Password never stored in plain text
- User data segregation
- Relationship constraints
- Foreign key integrity

### Production Readiness Checklist

- [x] Environment variable for JWT secret
- [x] Password hashing implementation
- [x] Input validation and sanitization
- [x] Authorization for user resources
- [x] Proper error handling
- [ ] Rate limiting (for future)
- [ ] HTTPS enforcement (for production)
- [ ] Password reset functionality (for future)
- [ ] Account email verification (for future)

### Security Concepts Mastered

1. **Authentication**: Verifying user identity
2. **Authorization**: Controlling resource access
3. **Session Management**: JWT token lifecycle
4. **Password Security**: Hashing and validation
5. **Input Validation**: Preventing injection attacks
6. **Error Handling**: Safe failure responses
7. **Database Security**: Relationship integrity

### Future Security Enhancements

#### Phase 3+ Features (Not Yet Implemented)

```python
# Rate limiting per IP/user
@router.post("/user/shorten")
@limiter.limit("10/minute")
async def create_url(...):

# Two-factor authentication
class UserSettings(BaseModel):
    two_factor_enabled: bool
    phone_number: Optional[str]

# Account lockout after failed attempts
class User(Base):
    failed_login_attempts: int = 0
    locked_until: Optional[datetime]

# Password reset tokens
class PasswordReset(Base):
    user_id: int
    reset_token: str
    expires_at: datetime
```

### Learning Transferable Skills

The security patterns learned in Phase 2 apply to:

- **Web Applications**: User accounts and sessions
- **APIs**: Token-based authentication
- **Mobile Apps**: JWT integration
- **Databases**: User data management
- **Security Auditing**: Common vulnerability prevention

---

## Project Evolution Summary

### Phase 1 → Phase 2 Growth

| Aspect | Phase 1 | Phase 2 |
|--------|---------|---------|
| **Complexity** | Basic CRUD | Authentication + Authorization |
| **Security** | None | JWT, Hashing, Validation |
| **Data Model** | Single table | Multi-table relationships |
| **API Endpoints** | 3 public routes | 7 authenticated + 3 public |
| **Validation** | Basic URL checks | Comprehensive user + data validation |
| **Error Handling** | Basic HTTP errors | Security-aware error responses |
| **User Experience** | Anonymous usage | Personal URL management |

### Next Steps

Phase 2 complete! Ready for **Phase 3: Async Features and Background Tasks**:

- Analytics tracking for URL clicks
- Background task processing
- Scheduled maintenance jobs
- Performance optimizations
- Advanced caching strategies
- Rate limiting implementation

Keep building! 🚀
