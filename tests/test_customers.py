import pytest
from fastapi import status
from decimal import Decimal

class TestCustomerCRUD:
    """Test customer CRUD operations."""
    
    def test_create_customer_success(self, client, auth_headers, test_customer_data):
        """Test successful customer creation."""
        response = client.post("/api/v1/customers/", 
                             json=test_customer_data, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["first_name"] == test_customer_data["first_name"]
        assert data["last_name"] == test_customer_data["last_name"]
        assert data["email"] == test_customer_data["email"]
        assert data["phone"] == test_customer_data["phone"]
        assert data["national_id"] == test_customer_data["national_id"]
        assert data["address"] == test_customer_data["address"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_customer_duplicate_email(self, client, auth_headers, test_customer_data, db_session):
        """Test customer creation with duplicate email fails."""
        # First customer creation
        response1 = client.post("/api/v1/customers/", 
                              json=test_customer_data, 
                              headers=auth_headers)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second customer with same email
        duplicate_data = test_customer_data.copy()
        duplicate_data["phone"] = "9876543210"
        duplicate_data["national_id"] = "987654321"
        
        response2 = client.post("/api/v1/customers/", 
                              json=duplicate_data, 
                              headers=auth_headers)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]
    
    def test_create_customer_duplicate_phone(self, client, auth_headers, test_customer_data, db_session):
        """Test customer creation with duplicate phone fails."""
        # First customer creation
        response1 = client.post("/api/v1/customers/", 
                              json=test_customer_data, 
                              headers=auth_headers)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second customer with same phone
        duplicate_data = test_customer_data.copy()
        duplicate_data["email"] = "different@example.com"
        duplicate_data["national_id"] = "987654321"
        
        response2 = client.post("/api/v1/customers/", 
                              json=duplicate_data, 
                              headers=auth_headers)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]
    
    def test_create_customer_duplicate_national_id(self, client, auth_headers, test_customer_data, db_session):
        """Test customer creation with duplicate national ID fails."""
        # First customer creation
        response1 = client.post("/api/v1/customers/", 
                              json=test_customer_data, 
                              headers=auth_headers)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second customer with same national ID
        duplicate_data = test_customer_data.copy()
        duplicate_data["email"] = "different@example.com"
        duplicate_data["phone"] = "9876543210"
        
        response2 = client.post("/api/v1/customers/", 
                              json=duplicate_data, 
                              headers=auth_headers)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]
    
    def test_create_customer_invalid_data(self, client, auth_headers):
        """Test customer creation with invalid data fails."""
        invalid_data = {
            "first_name": "",  # Empty first name
            "last_name": "Doe",
            "phone": "123",    # Invalid phone
            "email": "invalid-email"  # Invalid email
        }
        
        response = client.post("/api/v1/customers/", 
                             json=invalid_data, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_customers_list(self, client, auth_headers, sample_customers):
        """Test getting customers list with pagination."""
        response = client.get("/api/v1/customers/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "customers" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["customers"]) > 0
        assert data["total"] >= len(data["customers"])
    
    def test_get_customers_pagination(self, client, auth_headers, sample_customers):
        """Test customers list pagination."""
        # First page
        response1 = client.get("/api/v1/customers/?page=1&size=2", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1["customers"]) <= 2
        assert data1["page"] == 1
        assert data1["size"] == 2
        
        # Second page
        response2 = client.get("/api/v1/customers/?page=2&size=2", headers=auth_headers)
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert data2["page"] == 2
        assert data2["size"] == 2
        
        # Verify different customers on different pages
        if len(data1["customers"]) > 0 and len(data2["customers"]) > 0:
            assert data1["customers"][0]["id"] != data2["customers"][0]["id"]
    
    def test_get_customer_by_id(self, client, auth_headers, sample_customers):
        """Test getting a specific customer by ID."""
        customer_id = sample_customers[0].id
        
        response = client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == customer_id
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data
        assert "phone" in data
    
    def test_get_customer_not_found(self, client, auth_headers):
        """Test getting non-existent customer returns 404."""
        response = client.get("/api/v1/customers/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_customer_success(self, client, auth_headers, sample_customers):
        """Test successful customer update."""
        customer_id = sample_customers[0].id
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "9876543210"
        }
        
        response = client.put(f"/api/v1/customers/{customer_id}", 
                            json=update_data, 
                            headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert data["phone"] == update_data["phone"]
        assert "updated_at" in data
    
    def test_update_customer_not_found(self, client, auth_headers):
        """Test updating non-existent customer returns 404."""
        update_data = {"first_name": "Updated"}
        
        response = client.put("/api/v1/customers/99999", 
                            json=update_data, 
                            headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_customer_conflict(self, client, auth_headers, sample_customers, db_session):
        """Test customer update with conflicting data fails."""
        # Create another customer
        from app.domain.customer import Customer
        other_customer = Customer(
            first_name="Other",
            last_name="Customer",
            email="other@example.com",
            phone="1111111111",
            national_id="111111111",
            address="Other Street",
            province_id=1,
            district_id=1
        )
        db_session.add(other_customer)
        db_session.commit()
        
        # Try to update first customer with second customer's email
        customer_id = sample_customers[0].id
        update_data = {"email": "other@example.com"}
        
        response = client.put(f"/api/v1/customers/{customer_id}", 
                            json=update_data, 
                            headers=auth_headers)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]
    
    def test_delete_customer_success(self, client, auth_headers, sample_customers):
        """Test successful customer deletion."""
        customer_id = sample_customers[0].id
        
        response = client.delete(f"/api/v1/customers/{customer_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify customer was deleted
        get_response = client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_customer_not_found(self, client, auth_headers):
        """Test deleting non-existent customer returns 404."""
        response = client.delete("/api/v1/customers/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestCustomerSearch:
    """Test customer search and filtering functionality."""
    
    def test_search_customers_by_name(self, client, auth_headers, sample_customers):
        """Test searching customers by name."""
        search_term = "Customer0"  # Should match first customer
        
        response = client.get(f"/api/v1/customers/?search={search_term}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["customers"]) > 0
        # Verify search results contain the search term
        for customer in data["customers"]:
            assert (search_term.lower() in customer["first_name"].lower() or 
                   search_term.lower() in customer["last_name"].lower())
    
    def test_search_customers_by_email(self, client, auth_headers, sample_customers):
        """Test searching customers by email."""
        search_term = "customer0@test.com"
        
        response = client.get(f"/api/v1/customers/?search={search_term}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["customers"]) > 0
        assert any(search_term in customer["email"] for customer in data["customers"])
    
    def test_search_customers_by_phone(self, client, auth_headers, sample_customers):
        """Test searching customers by phone."""
        search_term = "1234567890"  # Should match first customer
        
        response = client.get(f"/api/v1/customers/?search={search_term}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["customers"]) > 0
        assert any(search_term in customer["phone"] for customer in data["customers"])
    
    def test_filter_customers_by_location(self, client, auth_headers, sample_customers):
        """Test filtering customers by location."""
        response = client.get("/api/v1/customers/?province_id=1&district_id=1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["customers"]) > 0
        # Verify all customers are from the specified location
        for customer in data["customers"]:
            assert customer["province_id"] == 1
            assert customer["district_id"] == 1
    
    def test_search_no_results(self, client, auth_headers):
        """Test search with no results returns empty list."""
        search_term = "nonexistentcustomer"
        
        response = client.get(f"/api/v1/customers/?search={search_term}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["customers"]) == 0
        assert data["total"] == 0

class TestCustomerValidation:
    """Test customer data validation."""
    
    @pytest.mark.parametrize("invalid_phone", [
        "123",           # Too short
        "1234567890123456",  # Too long
        "abc123def",     # Contains letters
        "",              # Empty
    ])
    def test_create_customer_invalid_phone(self, client, auth_headers, invalid_phone):
        """Test customer creation with invalid phone numbers."""
        customer_data = {
            "first_name": "Test",
            "last_name": "Customer",
            "phone": invalid_phone,
            "email": "test@example.com"
        }
        
        response = client.post("/api/v1/customers/", 
                             json=customer_data, 
                             headers=auth_headers)
        
        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
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
    
    def test_create_customer_missing_required_fields(self, client, auth_headers):
        """Test customer creation with missing required fields."""
        customer_data = {
            "first_name": "Test",
            # Missing last_name, phone
        }
        
        response = client.post("/api/v1/customers/", 
                             json=customer_data, 
                             headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestCustomerPermissions:
    """Test customer endpoint permissions."""
    
    def test_create_customer_unauthorized(self, client, test_customer_data):
        """Test customer creation without authentication fails."""
        response = client.post("/api/v1/customers/", json=test_customer_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_customers_unauthorized(self, client):
        """Test getting customers without authentication fails."""
        response = client.get("/api/v1/customers/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_customer_unauthorized(self, client, sample_customers):
        """Test customer update without authentication fails."""
        customer_id = sample_customers[0].id
        update_data = {"first_name": "Updated"}
        
        response = client.put(f"/api/v1/customers/{customer_id}", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_customer_unauthorized(self, client, sample_customers):
        """Test customer deletion without authentication fails."""
        customer_id = sample_customers[0].id
        
        response = client.delete(f"/api/v1/customers/{customer_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 