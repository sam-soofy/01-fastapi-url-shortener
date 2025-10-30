# URL Shortener API - FastAPI Learning Project

A comprehensive URL shortener API built with FastAPI, designed as a learning project to master modern Python web development concepts including async operations, data validation, database management, and containerization.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

## 🎯 Current Features (Phase 1 Complete)

### ✅ Core Functionality

- **URL Shortening**: Create short codes for long URLs
- **URL Redirection**: Fast redirects with click tracking
- **Analytics Dashboard**: View click statistics for shortened URLs
- **Async Operations**: High-performance async/await patterns throughout

### ✅ Data Management

- **Pydantic Validation**: Comprehensive input validation and data sanitization
- **SQLAlchemy Integration**: Async database operations with SQLite/PostgreSQL support
- **Type Safety**: Full Python type hints for robust development experience

### ✅ API Quality

- **Interactive Documentation**: Swagger UI at `/docs` with live testing
- **Comprehensive Error Handling**: Proper HTTP status codes and detailed error messages
- **RESTful Design**: Clean API endpoints following REST principles

### ✅ Developer Experience

- **Docker Support**: Containerized deployment with docker-compose
- **Development Tools**: Hot reload, logging, and debugging ready
- **Modern Python**: Uses Python 3.12+ with latest FastAPI features

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.12 or higher
- **uv**: Modern Python package manager (`pip install uv`)
- **Docker**: Optional, for containerized development

### Development Setup

1. **Clone and Setup**:

   ```bash
   cd fastapi-url-shortener
   uv sync
   ```

2. **Run Development Server**:

   ```bash
   uv run uvicorn main:app --reload --port 8000
   ```

3. **Access the API**:
   - **API Base**: <http://localhost:8000>
   - **Interactive Docs**: <http://localhost:8000/docs>
   - **Alternative Docs**: <http://localhost:8000/redoc>

### Docker Setup (Optional)

```bash
# Using Docker Compose
docker-compose up --build

# Or build manually
docker build -t url-shortener .
docker run -p 8000:8000 url-shortener
```

## 📖 API Endpoints

### URL Management

- `POST /api/v1/shorten` - Create a shortened URL
- `GET /{short_code}` - Redirect to original URL (with click tracking)
- `GET /api/v1/stats/{short_code}` - Get URL statistics

### Example Usage

```bash
# Create shortened URL
curl -X POST "http://localhost:8000/api/v1/shorten" \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://www.example.com/very/long/url"}'

# Response
{
  "id": 1,
  "original_url": "https://www.example.com/very/long/url",
  "short_code": "abc12345",
  "clicks": 0,
  "created_at": "2025-01-30T11:00:00Z"
}

# Access shortened URL (triggers redirect and click count)
curl -I "http://localhost:8000/abc12345"

# Get statistics
curl "http://localhost:8000/api/v1/stats/abc12345"
```

## 📋 Project Roadmap

This project is structured in phases to provide a comprehensive learning experience:

### Phase 1 ✅ **Completed**

- Basic URL shortening and redirection
- Data validation and error handling
- Database integration with async SQLAlchemy
- Docker containerization
- API documentation with Swagger

### Phase 2: User Authentication & Advanced Validation

- JWT-based user authentication
- User registration and login
- Role-based access control
- Advanced input sanitization

### Phase 3: Async Features & Background Tasks

- Complete async refactoring
- Click analytics with background processing
- Scheduled maintenance tasks
- Performance optimization

### Phase 4: Caching & Rate Limiting with Redis

- Redis caching layer
- API rate limiting
- Session management
- Distributed features

### Phase 5: Production Features

- Advanced analytics (geolocation, referrers)
- API versioning
- Performance monitoring
- Production deployment pipeline

📄 **Full Project Plan**: [View Complete Roadmap](docs/plan.md)

## 📚 Learning Resources

### Comprehensive Tutorial

This project includes an extensive learning guide covering:

- [**FastAPI Fundamentals**](docs/TUTORIALS-PHASE-1.md#starting-a-fastapi-project) - Basic setup and application structure
- [**Routes & Controllers**](docs/TUTORIALS-PHASE-1.md#routes-and-controllers-routers) - HTTP routing patterns and dependency injection
- [**Pydantic & Type Hints**](docs/TUTORIALS-PHASE-1.md#pydantic-and-python-type-hints) - Data validation and Python typing
- [**Data Validation**](docs/TUTORIALS-PHASE-1.md#data-validation-and-sanitization) - Input sanitization and business logic validation
- [**Project Architecture**](docs/TUTORIALS-PHASE-1.md#project-structure-and-patterns) - Design patterns and code organization
- [**Async/Await Patterns**](docs/TUTORIALS-PHASE-1.md#asyncawait-in-python-and-fastapi) - Asynchronous programming in FastAPI
- [**Database Operations**](docs/TUTORIALS-PHASE-1.md#sqlalchemy-for-postgresql) - Async SQLAlchemy with PostgreSQL
- [**API Documentation**](docs/TUTORIALS-PHASE-1.md#api-documentation-with-swagger) - Interactive docs with Swagger/OpenAPI

🚀 **Start Learning**: [Complete Tutorial Guide](docs/TUTORIALS-PHASE-1.md)

### Key Technologies Used

| Technology | Purpose | Learning Focus |
|------------|---------|----------------|
| **FastAPI** | Modern web framework | Routing, dependency injection, async operations |
| **Pydantic** | Data validation | Type hints, model validation, serialization |
| **SQLAlchemy** | Database ORM | Async queries, relationships, migrations |
| **uv** | Package management | Modern Python dependency management |
| **Docker** | Containerization | Deployment, environment consistency |
| **PostgreSQL** | Database | ACID transactions, indexing, optimization |

## 🔧 Development

### Code Quality

- **Type Hints**: Full Python typing throughout
- **PEP 8**: Ruff formatting and linting
- **Async Throughout**: Proper async/await usage
- **Error Handling**: Comprehensive exception management

### Project Structure

```
fastapi-url-shortener/
├── app/                    # Main application package
│   ├── routers/           # Route handlers
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── crud/              # Database operations
│   └── database.py        # Database configuration
├── docs/                  # Documentation and tutorials
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Container definition
├── pyproject.toml        # Project dependencies
└── README.md             # This file
```

### Testing

```bash
# Run with pytest (future implementation)
pytest

# Run with coverage
pytest --cov=app
```

## 🚢 Deployment

### Production Setup

```bash
# Using Docker (recommended)
docker-compose -f docker-compose.prod.yml up -d

# Traditional deployment
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
SECRET_KEY=your-secret-key-here
DEBUG=False
```

## 🤝 Contributing

This is a learning project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The modern Python web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and parsing
- [SQLAlchemy](https://sqlalchemy.org/) - Python SQL toolkit and ORM
- [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer

---

**Ready to learn FastAPI?** Start with the [tutorial guide](docs/TUTORIALS-PHASE-1.md) and build your skills progressively through each phase!
