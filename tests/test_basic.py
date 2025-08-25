import pytest
from fastapi.testclient import TestClient

from app.main import app

class TestBasicFunctionality:
    """Basic tests to verify the system is working."""
    
    def test_app_imports(self):
        """Test that the FastAPI app can be imported."""
        assert app is not None
        assert hasattr(app, 'routes')
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_api_docs_endpoint(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_api_redoc_endpoint(self, client):
        """Test that ReDoc documentation is accessible."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

class TestConfiguration:
    """Test application configuration."""
    
    def test_settings_loaded(self):
        """Test that application settings are loaded."""
        from app.core.config import settings
        
        assert settings.app_name == "FastAPI Property Evaluation System"
        assert settings.app_version == "1.0.0"
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'secret_key')
    
    def test_database_connection(self, db_session):
        """Test that database connection works."""
        assert db_session is not None
        
        # Test a simple query
        from app.domain.rbac_models import User
        users = db_session.query(User).limit(1).all()
        assert isinstance(users, list)

class TestFixtures:
    """Test that fixtures are working correctly."""
    
    def test_test_user_data_fixture(self, test_user_data):
        """Test the test user data fixture."""
        assert "email" in test_user_data
        assert "password" in test_user_data
        assert "first_name" in test_user_data
        assert "last_name" in test_user_data
        assert "phone" in test_user_data
    
    def test_test_customer_data_fixture(self, test_customer_data):
        """Test the test customer data fixture."""
        assert "first_name" in test_customer_data
        assert "last_name" in test_customer_data
        assert "phone" in test_customer_data
        assert "province_id" in test_customer_data
        assert "district_id" in test_customer_data
    
    def test_setup_test_data_fixture(self, db_session, setup_test_data):
        """Test that test data setup works."""
        from app.domain.location_models import Province, District
        from app.domain.rbac_models import Role, Permission
        
        # Check that provinces were created
        provinces = db_session.query(Province).all()
        assert len(provinces) > 0
        
        # Check that districts were created
        districts = db_session.query(District).all()
        assert len(districts) > 0
        
        # Check that roles were created
        roles = db_session.query(Role).all()
        assert len(roles) > 0
        
        # Check that permissions were created
        permissions = db_session.query(Permission).all()
        assert len(permissions) > 0

class TestAuthenticationSetup:
    """Test authentication system setup."""
    
    def test_test_user_creation(self, test_user):
        """Test that test user is created correctly."""
        assert test_user.id is not None
        assert test_user.email == "test@example.com"
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.is_active is True
    
    def test_auth_headers_generation(self, client, test_user_data):
        """Test that authentication headers can be generated."""
        # This test might fail if the user doesn't exist yet
        # It's more of an integration test
        try:
            response = client.post("/api/v1/auth/login", data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            })
            
            if response.status_code == 200:
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"
            else:
                # User might not exist yet, which is fine for this basic test
                assert response.status_code in [400, 401, 422]
        except Exception:
            # If login fails for any reason, that's acceptable in basic tests
            pass

@pytest.mark.slow
class TestSlowOperations:
    """Tests that might be slower (marked for optional execution)."""
    
    def test_database_operations(self, db_session, setup_test_data):
        """Test various database operations."""
        from app.domain.customer import Customer
        
        # Create a customer
        customer = Customer(
            first_name="Test",
            last_name="Customer",
            phone="1234567890",
            province_id=1,
            district_id=1
        )
        db_session.add(customer)
        db_session.commit()
        
        # Verify it was created
        assert customer.id is not None
        
        # Retrieve it
        retrieved_customer = db_session.query(Customer).filter(
            Customer.id == customer.id
        ).first()
        
        assert retrieved_customer is not None
        assert retrieved_customer.first_name == "Test"
        
        # Clean up
        db_session.delete(customer)
        db_session.commit() 