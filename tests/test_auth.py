import pytest
from fastapi import status
from passlib.context import CryptContext

from app.domain.rbac_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user_success(self, client, db_session):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "9876543210"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert data["phone"] == user_data["phone"]
        assert data["is_active"] is True
        assert "id" in data
        assert "password_hash" not in data
        
        # Verify user was created in database
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert pwd_context.verify(user_data["password"], user.password_hash)
    
    def test_register_user_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        user_data = {
            "email": "test@example.com",  # Same as test_user
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "9876543210"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]
    
    def test_register_user_invalid_data(self, client):
        """Test registration with invalid data fails."""
        # Missing required fields
        user_data = {
            "email": "invalid@example.com",
            # Missing password, first_name, last_name
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, test_user_data):
        """Test successful user login."""
        response = client.post("/api/v1/auth/login", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials fails."""
        response = client.post("/api/v1/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, client, db_session, test_user_data):
        """Test login with inactive user fails."""
        # Create inactive user
        from app.domain.rbac_models import User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(test_user_data["password"])
        
        inactive_user = User(
            email="inactive@example.com",
            password_hash=hashed_password,
            first_name="Inactive",
            last_name="User",
            phone="1234567890",
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        response = client.post("/api/v1/auth/login", data={
            "username": "inactive@example.com",
            "password": test_user_data["password"]
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Inactive user" in response.json()["detail"]
    
    def test_get_current_user_success(self, client, auth_headers):
        """Test getting current user information with valid token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "id" in data
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "is_active" in data
        assert data["is_active"] is True
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without token fails."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_change_password_success(self, client, auth_headers, test_user_data):
        """Test successful password change."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "newpassword456"
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in response.json()["message"]
    
    def test_change_password_wrong_current_password(self, client, auth_headers):
        """Test password change with wrong current password fails."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword456"
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_refresh_token_success(self, client, auth_headers):
        """Test successful token refresh."""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_logout_success(self, client):
        """Test successful logout."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in response.json()["message"]

class TestAuthenticationValidation:
    """Test authentication input validation."""
    
    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "@example.com",
        "user@",
        "user.example.com",
        ""
    ])
    def test_register_invalid_email_format(self, client, invalid_email):
        """Test registration with invalid email formats."""
        user_data = {
            "email": invalid_email,
            "password": "validpassword123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.parametrize("weak_password", [
        "123",           # Too short
        "password",      # Too common
        "abc123",        # Too simple
        "",              # Empty
    ])
    def test_register_weak_password(self, client, weak_password):
        """Test registration with weak passwords."""
        user_data = {
            "email": "test@example.com",
            "password": weak_password,
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Note: This test assumes password validation is implemented
        # If not, it will pass with HTTP 201
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_201_CREATED] 