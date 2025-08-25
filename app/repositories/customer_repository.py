from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.repositories.base import BaseRepository
from app.domain.customer import Customer
from app.domain.customer import CustomerCreateSchema, CustomerUpdateSchema

class CustomerRepository(BaseRepository[Customer, CustomerCreateSchema, CustomerUpdateSchema]):
    """Customer repository with customer-specific operations."""
    
    def __init__(self):
        super().__init__(Customer)
    
    def get_by_email(self, db: Session, email: str) -> Optional[Customer]:
        """Get customer by email address."""
        try:
            return db.query(Customer).filter(Customer.email == email).first()
        except Exception as e:
            raise DatabaseException(f"Error retrieving customer by email: {str(e)}")
    
    def get_by_phone(self, db: Session, phone: str) -> Optional[Customer]:
        """Get customer by phone number."""
        try:
            return db.query(Customer).filter(Customer.phone == phone).first()
        except Exception as e:
            raise DatabaseException(f"Error retrieving customer by phone: {str(e)}")
    
    def get_by_national_id(self, db: Session, national_id: str) -> Optional[Customer]:
        """Get customer by national ID."""
        try:
            return db.query(Customer).filter(Customer.national_id == national_id).first()
        except Exception as e:
            raise DatabaseException(f"Error retrieving customer by national ID: {str(e)}")
    
    def search_customers(
        self, 
        db: Session, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Search customers by name, email, phone, or national ID."""
        try:
            query = db.query(Customer).filter(
                or_(
                    Customer.first_name.ilike(f"%{search_term}%"),
                    Customer.last_name.ilike(f"%{search_term}%"),
                    Customer.email.ilike(f"%{search_term}%"),
                    Customer.phone.ilike(f"%{search_term}%"),
                    Customer.national_id.ilike(f"%{search_term}%")
                )
            )
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(f"Error searching customers: {str(e)}")
    
    def get_customers_by_location(
        self, 
        db: Session, 
        province_id: Optional[int] = None,
        district_id: Optional[int] = None,
        commune_id: Optional[int] = None,
        village_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Get customers filtered by location."""
        try:
            query = db.query(Customer)
            
            if province_id:
                query = query.filter(Customer.province_id == province_id)
            if district_id:
                query = query.filter(Customer.district_id == district_id)
            if commune_id:
                query = query.filter(Customer.commune_id == commune_id)
            if village_id:
                query = query.filter(Customer.village_id == village_id)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(f"Error retrieving customers by location: {str(e)}")
    
    def get_customers_with_loan_requests(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Get customers who have submitted loan requests."""
        try:
            from app.domain.loan_request import LoanRequest
            query = db.query(Customer).join(LoanRequest).distinct()
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(f"Error retrieving customers with loan requests: {str(e)}")

# Import the exception here to avoid circular imports
from app.core.exceptions import DatabaseException 