import pytest
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreateSchema, CustomerUpdateSchema
from app.core.exceptions import ValidationException, ConflictException, NotFoundException
from app.domain.customer import Customer

class TestCustomerService:
    """Test customer service business logic."""
    
    def test_create_customer_success(self, db_session, setup_test_data):
        """Test successful customer creation through service."""
        service = CustomerService()
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        
        customer = service.create_customer(db_session, customer_data)
        
        assert customer is not None
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.email == "john.doe@example.com"
        assert customer.phone == "1234567890"
        assert customer.national_id == "123456789"
        assert customer.id is not None
    
    def test_create_customer_duplicate_email(self, db_session, setup_test_data):
        """Test customer creation with duplicate email fails."""
        service = CustomerService()
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        
        # Create first customer
        service.create_customer(db_session, customer_data)
        
        # Try to create second customer with same email
        duplicate_data = CustomerCreateSchema(
            first_name="Jane",
            last_name="Doe",
            email="john.doe@example.com",  # Same email
            phone="9876543210",
            national_id="987654321",
            address="456 Test Street",
            province_id=1,
            district_id=1
        )
        
        with pytest.raises(ConflictException, match="already exists"):
            service.create_customer(db_session, duplicate_data)
    
    def test_create_customer_duplicate_phone(self, db_session, setup_test_data):
        """Test customer creation with duplicate phone fails."""
        service = CustomerService()
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        
        # Create first customer
        service.create_customer(db_session, customer_data)
        
        # Try to create second customer with same phone
        duplicate_data = CustomerCreateSchema(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone="1234567890",  # Same phone
            national_id="987654321",
            address="456 Test Street",
            province_id=1,
            district_id=1
        )
        
        with pytest.raises(ConflictException, match="already exists"):
            service.create_customer(db_session, duplicate_data)
    
    def test_create_customer_duplicate_national_id(self, db_session, setup_test_data):
        """Test customer creation with duplicate national ID fails."""
        service = CustomerService()
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        
        # Create first customer
        service.create_customer(db_session, customer_data)
        
        # Try to create second customer with same national ID
        duplicate_data = CustomerCreateSchema(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone="9876543210",
            national_id="123456789",  # Same national ID
            address="456 Test Street",
            province_id=1,
            district_id=1
        )
        
        with pytest.raises(ConflictException, match="already exists"):
            service.create_customer(db_session, duplicate_data)
    
    def test_create_customer_invalid_phone(self, db_session, setup_test_data):
        """Test customer creation with invalid phone fails validation."""
        service = CustomerService()
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123",  # Invalid phone (too short)
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        
        with pytest.raises(ValidationException, match="Invalid phone number format"):
            service.create_customer(db_session, customer_data)
    
    def test_create_customer_invalid_national_id(self, db_session, setup_test_data):
        """Test customer creation with invalid national ID fails validation."""
        service = CustomerService()
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123",  # Invalid national ID (too short)
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        
        with pytest.raises(ValidationException, match="Invalid national ID format"):
            service.create_customer(db_session, customer_data)
    
    def test_update_customer_success(self, db_session, setup_test_data):
        """Test successful customer update through service."""
        service = CustomerService()
        
        # Create customer first
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        customer = service.create_customer(db_session, customer_data)
        
        # Update customer
        update_data = CustomerUpdateSchema(
            first_name="Johnny",
            last_name="Smith",
            phone="9876543210"
        )
        
        updated_customer = service.update_customer(db_session, customer.id, update_data)
        
        assert updated_customer.first_name == "Johnny"
        assert updated_customer.last_name == "Smith"
        assert updated_customer.phone == "9876543210"
        assert updated_customer.email == "john.doe@example.com"  # Unchanged
    
    def test_update_customer_not_found(self, db_session, setup_test_data):
        """Test updating non-existent customer raises exception."""
        service = CustomerService()
        update_data = CustomerUpdateSchema(first_name="Johnny")
        
        with pytest.raises(NotFoundException):
            service.update_customer(db_session, customer.id, update_data)
    
    def test_update_customer_conflict(self, db_session, setup_test_data):
        """Test customer update with conflicting data fails."""
        service = CustomerService()
        
        # Create first customer
        customer1_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        customer1 = service.create_customer(db_session, customer1_data)
        
        # Create second customer
        customer2_data = CustomerCreateSchema(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone="9876543210",
            national_id="987654321",
            address="456 Test Street",
            province_id=1,
            district_id=1
        )
        customer2 = service.create_customer(db_session, customer2_data)
        
        # Try to update first customer with second customer's email
        update_data = CustomerUpdateSchema(email="jane.doe@example.com")
        
        with pytest.raises(ConflictException, match="already exists"):
            service.update_customer(db_session, customer1.id, update_data)
    
    def test_get_customer_success(self, db_session, setup_test_data):
        """Test getting customer by ID through service."""
        service = CustomerService()
        
        # Create customer first
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        created_customer = service.create_customer(db_session, customer_data)
        
        # Get customer
        retrieved_customer = service.get(db_session, created_customer.id)
        
        assert retrieved_customer is not None
        assert retrieved_customer.id == created_customer.id
        assert retrieved_customer.first_name == "John"
        assert retrieved_customer.email == "john.doe@example.com"
    
    def test_get_customer_not_found(self, db_session, setup_test_data):
        """Test getting non-existent customer returns None."""
        service = CustomerService()
        customer = service.get(db_session, 99999)
        
        assert customer is None
    
    def test_get_customers_list(self, db_session, setup_test_data):
        """Test getting customers list with pagination."""
        service = CustomerService()
        
        # Create multiple customers
        for i in range(5):
            customer_data = CustomerCreateSchema(
                first_name=f"Customer{i}",
                last_name=f"Test{i}",
                email=f"customer{i}@test.com",
                phone=f"123456789{i}",
                national_id=f"12345678{i}",
                address=f"{i} Test Street",
                province_id=1,
                district_id=1
            )
            service.create_customer(db_session, customer_data)
        
        # Get customers with pagination
        customers = service.get_multi(db_session, skip=0, limit=3)
        
        assert len(customers) == 3
        assert all(isinstance(customer, Customer) for customer in customers)
    
    def test_search_customers(self, db_session, setup_test_data):
        """Test customer search functionality."""
        service = CustomerService()
        
        # Create customers with different names
        customer_data = [
            CustomerCreateSchema(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="1234567890",
                national_id="123456789",
                address="123 Test Street",
                province_id=1,
                district_id=1
            ),
            CustomerCreateSchema(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="9876543210",
                national_id="987654321",
                address="456 Test Street",
                province_id=1,
                district_id=1
            ),
            CustomerCreateSchema(
                first_name="Bob",
                last_name="Johnson",
                email="bob.johnson@example.com",
                phone="5555555555",
                national_id="555555555",
                address="789 Test Street",
                province_id=1,
                district_id=1
            )
        ]
        
        for data in customer_data:
            service.create_customer(db_session, data)
        
        # Search by name
        results = service.search_customers(db_session, "John", page=1, size=10)
        
        assert len(results["customers"]) > 0
        assert results["total"] > 0
        assert results["page"] == 1
        assert results["size"] == 10
        
        # Verify search results contain "John"
        for customer in results["customers"]:
            assert ("John" in customer.first_name or 
                   "John" in customer.last_name or 
                   "John" in customer.email)
    
    def test_get_customers_by_location(self, db_session, setup_test_data):
        """Test filtering customers by location."""
        service = CustomerService()
        
        # Create customers in different locations
        customer_data = [
            CustomerCreateSchema(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="1234567890",
                national_id="123456789",
                address="123 Test Street",
                province_id=1,
                district_id=1
            ),
            CustomerCreateSchema(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="9876543210",
                national_id="987654321",
                address="456 Test Street",
                province_id=1,
                district_id=1
            )
        ]
        
        for data in customer_data:
            service.create_customer(db_session, data)
        
        # Filter by province and district
        results = service.get_customers_by_location(
            db_session, 
            province_id=1, 
            district_id=1, 
            page=1, 
            size=10
        )
        
        assert len(results["customers"]) > 0
        assert results["total"] > 0
        
        # Verify all customers are from the specified location
        for customer in results["customers"]:
            assert customer.province_id == 1
            assert customer.district_id == 1
    
    def test_delete_customer_success(self, db_session, setup_test_data):
        """Test successful customer deletion through service."""
        service = CustomerService()
        
        # Create customer first
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        customer = service.create_customer(db_session, customer_data)
        
        # Delete customer
        success = service.delete(db_session, customer.id)
        
        assert success is True
        
        # Verify customer was deleted
        deleted_customer = service.get(db_session, customer.id)
        assert deleted_customer is None
    
    def test_delete_customer_not_found(self, db_session, setup_test_data):
        """Test deleting non-existent customer raises exception."""
        service = CustomerService()
        
        with pytest.raises(NotFoundException):
            service.delete(db_session, 99999)
    
    def test_count_customers(self, db_session, setup_test_data):
        """Test customer counting functionality."""
        service = CustomerService()
        
        # Create customers
        for i in range(3):
            customer_data = CustomerCreateSchema(
                first_name=f"Customer{i}",
                last_name=f"Test{i}",
                email=f"customer{i}@test.com",
                phone=f"123456789{i}",
                national_id=f"12345678{i}",
                address=f"{i} Test Street",
                province_id=1,
                district_id=1
            )
            service.create_customer(db_session, customer_data)
        
        # Count all customers
        total_count = service.count(db_session)
        assert total_count >= 3
        
        # Count customers with filter
        filtered_count = service.count(db_session, {"province_id": 1})
        assert filtered_count >= 3
    
    def test_customer_exists(self, db_session, setup_test_data):
        """Test customer existence checking."""
        service = CustomerService()
        
        # Create customer first
        customer_data = CustomerCreateSchema(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            national_id="123456789",
            address="123 Test Street",
            province_id=1,
            district_id=1
        )
        customer = service.create_customer(db_session, customer_data)
        
        # Check existence
        assert service.exists(db_session, customer.id) is True
        assert service.exists(db_session, 99999) is False

class TestCustomerServiceValidation:
    """Test customer service validation methods."""
    
    def test_phone_validation(self, db_session, setup_test_data):
        """Test phone number validation logic."""
        service = CustomerService()
        
        # Valid phone numbers
        valid_phones = ["123456789", "123456789012345", "+1234567890", "(123) 456-7890"]
        for phone in valid_phones:
            assert service._is_valid_phone(phone) is True
        
        # Invalid phone numbers
        invalid_phones = ["123", "12345678901234567", "abc123def", ""]
        for phone in invalid_phones:
            assert service._is_valid_phone(phone) is False
    
    def test_national_id_validation(self, db_session, setup_test_data):
        """Test national ID validation logic."""
        service = CustomerService()
        
        # Valid national IDs
        valid_ids = ["12345678", "123456789012345"]
        for id_num in valid_ids:
            assert service._is_valid_national_id(id_num) is True
        
        # Invalid national IDs
        invalid_ids = ["123", "12345678901234567", ""]
        for id_num in invalid_ids:
            assert service._is_valid_national_id(id_num) is False 