# Tests Directory

This directory contains all test files for the FastAPI Property Evaluation System.

## 📁 **Test Structure**

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and fixtures
├── __init__.py                  # Python package init
├── test_basic.py                # Basic API tests (health, docs)
├── test_auth.py                 # Authentication and authorization tests
├── test_customers.py            # Customer API tests
├── test_services.py             # Service layer tests
├── test_customer_api_v2.py      # Additional customer API tests
└── test_property_system_v2.py   # Property system tests
```

## 🧪 **Test Categories**

### **1. Basic Tests** (`test_basic.py`)
- Health check endpoints
- API documentation endpoints
- Basic connectivity tests

### **2. Authentication Tests** (`test_auth.py`)
- User registration
- User login/logout
- JWT token validation
- RBAC permissions
- Profile management

### **3. Customer Tests** (`test_customers.py`, `test_customer_api_v2.py`)
- Customer CRUD operations
- Customer image uploads
- Customer search and filtering
- Customer validation

### **4. Service Tests** (`test_services.py`)
- Business logic testing
- Service layer validation
- Error handling
- Data processing

### **5. Property Tests** (`test_property_system_v2.py`)
- Property management
- Property evaluation
- Document handling
- Property relationships

## 🚀 **Running Tests**

### **Run All Tests**
```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py

# Run with coverage
pytest --cov=app --cov-report=html
```

### **Run Specific Test Categories**
```bash
# Run only authentication tests
pytest tests/test_auth.py

# Run only customer tests
pytest tests/test_customers.py

# Run only service tests
pytest tests/test_services.py
```

### **Run Tests with Docker**
```bash
# Run tests in Docker container
docker compose exec fastapi pytest

# Run tests with specific markers
docker compose exec fastapi pytest -m "slow"
```

## 📋 **Test Guidelines**

### **Naming Conventions**
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### **Test Structure**
```python
def test_function_name():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

### **Fixtures**
- Use `conftest.py` for shared fixtures
- Use `@pytest.fixture` decorator
- Scope fixtures appropriately (function, class, module, session)

### **Assertions**
- Use descriptive assertion messages
- Test both positive and negative cases
- Validate response structure and content

### **Database Testing**
- Use test database
- Clean up after tests
- Use transactions for isolation

## 🔧 **Test Configuration**

### **pytest.ini**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### **conftest.py**
- Database fixtures
- Authentication fixtures
- Test client setup
- Mock services

## 📊 **Coverage**

### **Generate Coverage Report**
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

### **Coverage Targets**
- Aim for >80% code coverage
- Focus on critical business logic
- Test error paths and edge cases

## 🐛 **Debugging Tests**

### **Run Single Test**
```bash
pytest tests/test_auth.py::test_login_success -v
```

### **Run with Print Statements**
```bash
pytest tests/test_auth.py::test_login_success -s
```

### **Run with PDB**
```bash
pytest tests/test_auth.py::test_login_success --pdb
```

## 📝 **Writing New Tests**

### **Template for API Tests**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoint_name():
    """Test description."""
    # Arrange
    test_data = {"key": "value"}
    
    # Act
    response = client.post("/api/v1/endpoint", json=test_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "value"
```

### **Template for Service Tests**
```python
import pytest
from app.core.your_service import YourService
from app.core.database import SessionLocal

def test_service_method():
    """Test service method."""
    # Arrange
    db = SessionLocal()
    
    try:
        # Act
        result = YourService.your_method(db, test_data)
        
        # Assert
        assert result is not None
        assert result.property == expected_value
    finally:
        db.close()
```

## 🔄 **Continuous Integration**

### **GitHub Actions** (if applicable)
```yaml
- name: Run Tests
  run: |
    pytest --cov=app --cov-report=xml
    coverage report
```

### **Pre-commit Hooks**
- Run tests before commit
- Check code coverage
- Validate test structure

## 📚 **Resources**

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction) 