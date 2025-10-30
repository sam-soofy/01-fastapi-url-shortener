# Testing Guide

This document provides comprehensive information about testing the FastAPI URL Shortener application.

## Test Structure

The test suite is organized into the following modules:

- `tests/test_auth.py` - Authentication endpoint tests
- `tests/test_shortener.py` - URL shortener endpoint tests  
- `tests/test_crud.py` - CRUD operation tests
- `tests/test_analytics.py` - Analytics functionality tests

## Running Tests

### Quick Start

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Use the convenience script
python run_tests.py --coverage --verbose
```

### Test Categories

#### Unit Tests

Test individual functions and classes in isolation:

```bash
python -m pytest tests/ -m unit
```

#### Integration Tests

Test multiple components working together:

```bash
python -m pytest tests/ -m integration
```

#### Specific Test Files

```bash
# Test authentication only
python -m pytest tests/test_auth.py

# Test URL shortener only
python -m pytest tests/test_shortener.py

# Test CRUD operations
python -m pytest tests/test_crud.py

# Test analytics
python -m pytest tests/test_analytics.py
```

### Test Options

```bash
# Verbose output
python -m pytest tests/ -v

# Stop on first failure
python -m pytest tests/ -x

# Run specific test
python -m pytest tests/test_auth.py::TestAuthEndpoints::test_register_user_success

# Run with coverage report
python -m pytest tests/ --cov=app --cov-report=html

# Run with specific markers
python -m pytest tests/ -m "not slow"
```

## Test Coverage

The test suite aims for >80% code coverage. Coverage reports are generated in:

- Terminal output (with `--cov-report=term-missing`)
- HTML report (with `--cov-report=html:htmlcov`)

## Test Database

Tests use an in-memory SQLite database to ensure:

- **Isolation**: Each test runs with a fresh database
- **Speed**: In-memory database is much faster than PostgreSQL
- **No Cleanup**: Database is automatically cleaned up after each test

## Test Fixtures

### Core Fixtures

- `client`: HTTPX AsyncClient for making requests
- `db_session`: Async database session
- `test_user_data`: Sample user registration data
- `auth_headers`: Authentication headers for authenticated requests
- `test_url_data`: Sample URL creation data

### Usage Example

```python
async def test_example(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
```

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Structure

```python
import pytest
from httpx import AsyncClient

class TestFeature:
    """Test feature description."""
    
    async def test_success_scenario(self, client: AsyncClient):
        """Test successful case."""
        # Arrange
        test_data = {"key": "value"}
        
        # Act
        response = await client.post("/endpoint", json=test_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["key"] == "expected_value"
    
    async def test_error_scenario(self, client: AsyncClient):
        """Test error case."""
        # Arrange
        invalid_data = {"key": "invalid"}
        
        # Act
        response = await client.post("/endpoint", json=invalid_data)
        
        # Assert
        assert response.status_code == 422
```

### Best Practices

1. **Arrange-Act-Assert**: Structure tests clearly
2. **Descriptive Names**: Use clear, descriptive test names
3. **Test Data**: Use fixtures for consistent test data
4. **Isolation**: Each test should be independent
5. **Edge Cases**: Test both success and failure scenarios
6. **Authentication**: Test both authenticated and unauthenticated cases

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - run: pip install -e .[dev]
      - run: python -m pytest tests/ --cov=app --cov-fail-under=80
```

## Debugging Tests

### Running Single Test

```bash
python -m pytest tests/test_auth.py::TestAuthEndpoints::test_register_user_success -v -s
```

### Using pdb

```python
def test_example():
    import pdb; pdb.set_trace()
    # Your test code here
```

### Print Debugging

```bash
python -m pytest tests/ -v -s --tb=short
```

## Performance Testing

### Running Performance Tests

```bash
# Install performance testing dependencies
pip install pytest-benchmark

# Run benchmarks
python -m pytest tests/ --benchmark-only
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Issues**: Check test database configuration
3. **Async Issues**: Ensure async/await is used correctly
4. **Fixture Issues**: Check fixture dependencies and scoping

### Test Database Reset

If tests fail due to database issues:

```bash
# Clean up test artifacts
rm -rf .pytest_cache/
rm -rf htmlcov/
```

## Contributing

When adding new features:

1. Write tests before implementing the feature (TDD)
2. Ensure >80% test coverage
3. Test both success and failure scenarios
4. Update documentation if needed
5. Run full test suite before submitting

## Test Metrics

Current test coverage:

- Overall coverage: Target >80%
- Authentication: Full coverage
- URL Shortener: Full coverage
- CRUD Operations: Full coverage
- Analytics: Full coverage

## Future Improvements

- [ ] Add performance benchmarks
- [ ] Add load testing
- [ ] Add end-to-end tests
- [ ] Add visual regression tests
- [ ] Add security testing
