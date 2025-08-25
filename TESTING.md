# 🧪 Testing Guide for FastAPI Property Evaluation System

This document provides comprehensive guidance on testing the FastAPI Property Evaluation System, ensuring code quality, reliability, and maintainability.

## 📋 Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## 🎯 Testing Philosophy

Our testing approach follows these principles:

- **Comprehensive Coverage**: Aim for 80%+ code coverage
- **Fast Execution**: Tests should run quickly for rapid feedback
- **Isolation**: Each test should be independent and not affect others
- **Realistic Data**: Use realistic test data that mirrors production scenarios
- **Clear Assertions**: Tests should clearly express what they're verifying
- **Maintainable**: Tests should be easy to understand and modify

## 🏗️ Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_auth.py             # Authentication tests
├── test_customers.py        # Customer management tests
├── test_services.py         # Business logic tests
├── test_repositories.py     # Data access tests
├── test_api.py              # API endpoint tests
└── test_integration.py      # End-to-end integration tests
```

### Key Testing Components

- **Fixtures** (`conftest.py`): Reusable test data and setup
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **API Tests**: Test HTTP endpoints and responses
- **Database Tests**: Test data persistence and retrieval

## 🚀 Running Tests

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --category auth
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run tests matching pattern
pytest -k "test_login"

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Test Runner Script Options

```bash
python run_tests.py --help

# Available options:
--all                    # Run all tests
--unit                   # Run unit tests only
--integration            # Run integration tests only
--category CATEGORY      # Run tests for specific category
--performance            # Run performance tests
--security               # Run security tests
--quality                # Run code quality checks
--install                # Install dependencies
--report                 # Generate test report
```

## 🏷️ Test Categories

### 1. Unit Tests (`--unit`)

Test individual functions and methods in isolation.

**Examples:**
- Service business logic validation
- Repository data access methods
- Schema validation rules
- Utility function calculations

**Location:** `tests/test_services.py`, `tests/test_repositories.py`

### 2. Integration Tests (`--integration`)

Test component interactions and data flow.

**Examples:**
- Service-repository interactions
- Database transaction handling
- API endpoint with database operations
- Authentication flow

**Location:** `tests/test_integration.py`

### 3. API Tests (`--api`)

Test HTTP endpoints and API behavior.

**Examples:**
- Request/response validation
- Authentication and authorization
- Error handling
- Response format verification

**Location:** `tests/test_auth.py`, `tests/test_customers.py`

### 4. Authentication Tests (`--category auth`)

Test authentication and authorization systems.

**Examples:**
- User registration and login
- JWT token validation
- Role-based access control
- Password management

**Location:** `tests/test_auth.py`

### 5. Customer Tests (`--category customer`)

Test customer management functionality.

**Examples:**
- CRUD operations
- Data validation
- Search and filtering
- Business rule enforcement

**Location:** `tests/test_customers.py`

### 6. Service Tests (`--category service`)

Test business logic and service layer.

**Examples:**
- Business rule validation
- Data transformation
- Error handling
- Service orchestration

**Location:** `tests/test_services.py`

## ✍️ Writing Tests

### Test Naming Convention

```python
def test_function_name_scenario():
    """Test description explaining what is being tested."""
    # Arrange
    # Act
    # Assert
```

### Test Structure (AAA Pattern)

```python
def test_create_customer_success(self, client, auth_headers, test_customer_data):
    """Test successful customer creation."""
    # Arrange - Set up test data and conditions
    customer_data = test_customer_data
    
    # Act - Execute the function being tested
    response = client.post("/api/v1/customers/", 
                         json=customer_data, 
                         headers=auth_headers)
    
    # Assert - Verify the expected outcomes
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["first_name"] == customer_data["first_name"]
    assert "id" in data
```

### Using Fixtures

```python
def test_customer_operations(self, db_session, setup_test_data, sample_customers):
    """Test customer operations using fixtures."""
    # setup_test_data creates test provinces, districts, etc.
    # sample_customers provides pre-created customer objects
    
    customer = sample_customers[0]
    assert customer.id is not None
    assert customer.first_name.startswith("Customer")
```

### Testing Exceptions

```python
def test_create_customer_duplicate_email(self, client, auth_headers, test_customer_data):
    """Test customer creation with duplicate email fails."""
    # Create first customer
    response1 = client.post("/api/v1/customers/", 
                          json=test_customer_data, 
                          headers=auth_headers)
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Try to create second customer with same email
    duplicate_data = test_customer_data.copy()
    duplicate_data["phone"] = "9876543210"  # Different phone
    
    response2 = client.post("/api/v1/customers/", 
                          json=duplicate_data, 
                          headers=auth_headers)
    
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response2.json()["detail"]
```

### Parametrized Tests

```python
@pytest.mark.parametrize("invalid_email", [
    "invalid-email",
    "@example.com",
    "user@",
    "user.example.com",
    ""
])
def test_create_customer_invalid_email(self, client, auth_headers, invalid_email):
    """Test customer creation with invalid email formats."""
    customer_data = {
        "first_name": "Test",
        "last_name": "Customer",
        "phone": "1234567890",
        "email": invalid_email
    }
    
    response = client.post("/api/v1/customers/", 
                         json=customer_data, 
                         headers=auth_headers)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

## 📊 Test Coverage

### Coverage Goals

- **Overall Coverage**: 80% minimum
- **Critical Paths**: 95% minimum
- **Business Logic**: 90% minimum
- **API Endpoints**: 85% minimum

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html

# Generate XML coverage report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Coverage Configuration

```ini
# pytest.ini
addopts = 
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml --cov-fail-under=80
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Ensure test database is accessible
# Check SQLite file permissions
# Verify database URL in conftest.py
```

#### 2. Import Errors

```bash
# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Install package in development mode
pip install -e .
```

#### 3. Fixture Errors

```bash
# Check fixture dependencies
# Verify fixture names match test parameters
# Ensure fixtures are properly scoped
```

#### 4. Slow Tests

```bash
# Run tests in parallel
pytest -n auto

# Profile slow tests
pytest --durations=10

# Skip slow tests during development
pytest -m "not slow"
```

### Debug Mode

```bash
# Run tests with debug output
pytest -v -s --tb=long

# Run single test with debug
pytest tests/test_auth.py::TestAuthentication::test_login_success -v -s

# Use pdb for debugging
pytest --pdb
```

### Test Database Management

```bash
# Clean test database
rm -f test.db

# Recreate test database
pytest --setup-show

# Check database state
sqlite3 test.db ".tables"
```

## 📚 Best Practices

### 1. Test Independence

- Each test should be able to run in isolation
- Use fixtures for setup and teardown
- Avoid test order dependencies

### 2. Meaningful Assertions

```python
# Good
assert response.status_code == status.HTTP_201_CREATED
assert "id" in response.json()
assert customer.email == "test@example.com"

# Avoid
assert response.status_code == 201  # Use constants
assert len(response.json()) > 0     # Too vague
```

### 3. Test Data Management

- Use factories for generating test data
- Keep test data realistic and varied
- Clean up test data after each test

### 4. Error Testing

- Test both success and failure scenarios
- Verify error messages and status codes
- Test edge cases and boundary conditions

### 5. Performance Considerations

- Use database transactions for test isolation
- Minimize external service calls
- Mock slow operations when appropriate

## 🎉 Conclusion

A comprehensive testing strategy is essential for maintaining code quality and reliability. This guide provides the foundation for building robust tests that will help ensure your FastAPI application works correctly in all scenarios.

Remember:
- **Test early, test often**
- **Aim for high coverage but focus on quality**
- **Keep tests maintainable and readable**
- **Use tests as documentation**

For additional help, refer to:
- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction) 