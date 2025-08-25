from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.base import BaseService
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreateSchema, CustomerUpdateSchema
from app.domain.customer import Customer
from app.core.exceptions import ValidationException, ConflictException

class CustomerService(BaseService[Customer, CustomerCreateSchema, CustomerUpdateSchema]):
    """Customer service with customer-specific business logic."""
    
    def __init__(self):
        super().__init__(CustomerRepository())
    
    def create_customer(self, db: Session, customer_data: CustomerCreateSchema) -> Customer:
        """Create a new customer with business rule validation."""
        self._validate_customer_data(db, customer_data)
        return self.create(db, customer_data)
    
    def update_customer(self, db: Session, customer_id: int, customer_data: CustomerUpdateSchema) -> Customer:
        """Update an existing customer with business rule validation."""
        self._validate_customer_update(db, customer_id, customer_data)
        return self.update(db, customer_id, customer_data)
    
    def get_customer_by_email(self, db: Session, email: str) -> Optional[Customer]:
        """Get customer by email address."""
        return self.repository.get_by_email(db, email)
    
    def get_customer_by_phone(self, db: Session, phone: str) -> Optional[Customer]:
        """Get customer by phone number."""
        return self.repository.get_by_phone(db, phone)
    
    def get_customer_by_national_id(self, db: Session, national_id: str) -> Optional[Customer]:
        """Get customer by national ID."""
        return self.repository.get_by_national_id(db, national_id)
    
    def search_customers(
        self, 
        db: Session, 
        search_term: str, 
        page: int = 1, 
        size: int = 20
    ) -> Dict[str, Any]:
        """Search customers with pagination."""
        skip = (page - 1) * size
        customers = self.repository.search_customers(db, search_term, skip, size)
        total = self.repository.count(db)
        
        return {
            "customers": customers,
            "total": total,
            "page": page,
            "size": size
        }
    
    def get_customers_by_location(
        self, 
        db: Session, 
        province_id: Optional[int] = None,
        district_id: Optional[int] = None,
        commune_id: Optional[int] = None,
        village_id: Optional[int] = None,
        page: int = 1, 
        size: int = 20
    ) -> Dict[str, Any]:
        """Get customers filtered by location with pagination."""
        skip = (page - 1) * size
        customers = self.repository.get_customers_by_location(
            db, province_id, district_id, commune_id, village_id, skip, size
        )
        total = self.repository.count(db)
        
        return {
            "customers": customers,
            "total": total,
            "page": page,
            "size": size
        }
    
    def get_customers_with_loan_requests(
        self, 
        db: Session, 
        page: int = 1, 
        size: int = 20
    ) -> Dict[str, Any]:
        """Get customers who have submitted loan requests with pagination."""
        skip = (page - 1) * size
        customers = self.repository.get_customers_with_loan_requests(db, skip, size)
        total = self.repository.count(db)
        
        return {
            "customers": customers,
            "total": total,
            "page": page,
            "size": size
        }
    
    def _validate_customer_data(self, db: Session, customer_data: CustomerCreateSchema) -> None:
        """Validate customer data before creation."""
        # Check if email already exists
        if customer_data.email:
            existing_customer = self.get_customer_by_email(db, customer_data.email)
            if existing_customer:
                raise ConflictException(f"Customer with email {customer_data.email} already exists")
        
        # Check if phone already exists
        existing_customer = self.get_customer_by_phone(db, customer_data.phone)
        if existing_customer:
            raise ConflictException(f"Customer with phone {customer_data.phone} already exists")
        
        # Check if national ID already exists
        if customer_data.national_id:
            existing_customer = self.get_customer_by_national_id(db, customer_data.national_id)
            if existing_customer:
                raise ConflictException(f"Customer with national ID {customer_data.national_id} already exists")
        
        # Validate phone number format (basic validation)
        if not self._is_valid_phone(customer_data.phone):
            raise ValidationException("Invalid phone number format")
        
        # Validate national ID format if provided
        if customer_data.national_id and not self._is_valid_national_id(customer_data.national_id):
            raise ValidationException("Invalid national ID format")
    
    def _validate_customer_update(self, db: Session, customer_id: int, customer_data: CustomerUpdateSchema) -> None:
        """Validate customer data before update."""
        # Check if email already exists for other customers
        if customer_data.email:
            existing_customer = self.get_customer_by_email(db, customer_data.email)
            if existing_customer and existing_customer.id != customer_id:
                raise ConflictException(f"Customer with email {customer_data.email} already exists")
        
        # Check if phone already exists for other customers
        if customer_data.phone:
            existing_customer = self.get_customer_by_phone(db, customer_data.phone)
            if existing_customer and existing_customer.id != customer_id:
                raise ConflictException(f"Customer with phone {customer_data.phone} already exists")
        
        # Check if national ID already exists for other customers
        if customer_data.national_id:
            existing_customer = self.get_customer_by_national_id(db, customer_data.national_id)
            if existing_customer and existing_customer.id != customer_id:
                raise ConflictException(f"Customer with national ID {customer_data.national_id} already exists")
        
        # Validate phone number format if provided
        if customer_data.phone and not self._is_valid_phone(customer_data.phone):
            raise ValidationException("Invalid phone number format")
        
        # Validate national ID format if provided
        if customer_data.national_id and not self._is_valid_national_id(customer_data.national_id):
            raise ValidationException("Invalid national ID format")
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Basic phone number validation."""
        # Remove spaces, dashes, and parentheses
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        # Check if it's 9-15 digits (common international phone number lengths)
        return 9 <= len(cleaned_phone) <= 15
    
    def _is_valid_national_id(self, national_id: str) -> bool:
        """Basic national ID validation."""
        # Remove spaces and dashes
        cleaned_id = ''.join(filter(str.isdigit, national_id))
        # Check if it's 8-15 digits (common national ID lengths)
        return 8 <= len(cleaned_id) <= 15 