from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.repositories.loan_type_repository import LoanTypeRepository
from app.domain.reference_models import LoanType
from app.schemas.loan_type import LoanTypeCreate, LoanTypeUpdate, LoanTypeResponse, LoanTypeListResponse
from app.core.exceptions import ValidationException, ConflictException, NotFoundException

class LoanTypeService(BaseService[LoanType, LoanTypeCreate, LoanTypeUpdate]):
    """Service for LoanType business logic."""
    
    def __init__(self, db: Session):
        self.repository = LoanTypeRepository()
        super().__init__(self.repository)
        self.db = db
    
    def create_loan_type(self, loan_type_data: LoanTypeCreate) -> LoanTypeResponse:
        """Create a new loan type with validation."""
        # Check if code already exists
        if self.repository.code_exists(self.db, loan_type_data.code):
            raise ConflictException(f"Loan type with code '{loan_type_data.code}' already exists")
        
        # Validate business rules
        self._validate_loan_type_data(loan_type_data)
        
        # Create loan type
        created_loan_type = self.repository.create(self.db, loan_type_data)
        
        return LoanTypeResponse.from_orm(created_loan_type)
    
    def update_loan_type(self, loan_type_id: int, loan_type_data: LoanTypeUpdate) -> LoanTypeResponse:
        """Update an existing loan type with validation."""
        # Get existing loan type
        loan_type = self.repository.get_by_id(self.db, loan_type_id)
        if not loan_type:
            raise NotFoundException(f"Loan type with ID {loan_type_id} not found")
        
        # Check if code already exists (if being updated)
        if loan_type_data.code and self.repository.code_exists(self.db, loan_type_data.code, exclude_id=loan_type_id):
            raise ConflictException(f"Loan type with code '{loan_type_data.code}' already exists")
        
        # Validate business rules
        self._validate_loan_type_update(loan_type, loan_type_data)
        
        # Update loan type
        updated_loan_type = self.repository.update(self.db, loan_type_id, loan_type_data)
        
        return LoanTypeResponse.from_orm(updated_loan_type)
    
    def get_loan_type(self, loan_type_id: int) -> LoanTypeResponse:
        """Get a loan type by ID."""
        loan_type = self.repository.get_by_id(self.db, loan_type_id)
        if not loan_type:
            raise NotFoundException(f"Loan type with ID {loan_type_id} not found")
        
        return LoanTypeResponse.from_orm(loan_type)
    
    def get_loan_type_by_code(self, code: str) -> LoanTypeResponse:
        """Get a loan type by code."""
        loan_type = self.repository.get_by_code(self.db, code)
        if not loan_type:
            raise NotFoundException(f"Loan type with code '{code}' not found")
        
        return LoanTypeResponse.from_orm(loan_type)
    
    def list_loan_types(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        min_amount_usd: Optional[int] = None,
        max_amount_usd: Optional[int] = None,
        page: int = 1,
        size: int = 10
    ) -> LoanTypeListResponse:
        """List loan types with pagination and filters."""
        skip = (page - 1) * size
        
        # Get loan types
        loan_types = self.repository.search_loan_types(
            self.db,
            search=search,
            is_active=is_active,
            min_amount_usd=min_amount_usd,
            max_amount_usd=max_amount_usd,
            skip=skip,
            limit=size
        )
        
        # Get total count
        total = self.repository.count_loan_types(
            self.db,
            search=search,
            is_active=is_active,
            min_amount_usd=min_amount_usd,
            max_amount_usd=max_amount_usd
        )
        
        # Calculate pages
        pages = (total + size - 1) // size
        
        return LoanTypeListResponse(
            items=[LoanTypeResponse.from_orm(loan_type) for loan_type in loan_types],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def get_active_loan_types(self) -> List[LoanTypeResponse]:
        """Get all active loan types."""
        loan_types = self.repository.get_active_loan_types(self.db)
        return [LoanTypeResponse.from_orm(loan_type) for loan_type in loan_types]
    
    def delete_loan_type(self, loan_type_id: int) -> bool:
        """Delete a loan type."""
        loan_type = self.repository.get_by_id(self.db, loan_type_id)
        if not loan_type:
            raise NotFoundException(f"Loan type with ID {loan_type_id} not found")
        
        # Check if loan type is being used in loan requests
        if loan_type.loan_requests:
            raise ValidationException("Cannot delete loan type that has associated loan requests")
        
        return self.repository.delete(self.db, loan_type_id)
    
    def toggle_loan_type_status(self, loan_type_id: int) -> LoanTypeResponse:
        """Toggle loan type active status."""
        loan_type = self.repository.get_by_id(self.db, loan_type_id)
        if not loan_type:
            raise NotFoundException(f"Loan type with ID {loan_type_id} not found")
        
        # Toggle status
        update_data = LoanTypeUpdate(is_active=not loan_type.is_active)
        updated_loan_type = self.repository.update(self.db, loan_type_id, update_data)
        
        return LoanTypeResponse.from_orm(updated_loan_type)
    
    def _validate_loan_type_data(self, data: LoanTypeCreate) -> None:
        """Validate loan type data for business rules."""
        # Validate amount ranges
        if data.min_amount_usd and data.max_amount_usd:
            if data.min_amount_usd >= data.max_amount_usd:
                raise ValidationException("Minimum USD amount must be less than maximum USD amount")
        
        if data.min_amount_khr and data.max_amount_khr:
            if data.min_amount_khr >= data.max_amount_khr:
                raise ValidationException("Minimum KHR amount must be less than maximum KHR amount")
        
        # Validate interest rate ranges
        if data.interest_rate_min and data.interest_rate_max:
            if data.interest_rate_min >= data.interest_rate_max:
                raise ValidationException("Minimum interest rate must be less than maximum interest rate")
        
        # Validate term ranges
        if data.term_min_months and data.term_max_months:
            if data.term_min_months >= data.term_max_months:
                raise ValidationException("Minimum term must be less than maximum term")
    
    def _validate_loan_type_update(self, existing: LoanType, data: LoanTypeUpdate) -> None:
        """Validate loan type update data for business rules."""
        # Get current values
        current_data = {
            'min_amount_usd': existing.min_amount_usd,
            'max_amount_usd': existing.max_amount_usd,
            'min_amount_khr': existing.min_amount_khr,
            'max_amount_khr': existing.max_amount_khr,
            'interest_rate_min': existing.interest_rate_min,
            'interest_rate_max': existing.interest_rate_max,
            'term_min_months': existing.term_min_months,
            'term_max_months': existing.term_max_months,
        }
        
        # Update with new values
        update_dict = data.dict(exclude_unset=True)
        current_data.update(update_dict)
        
        # Validate amount ranges
        if current_data['min_amount_usd'] and current_data['max_amount_usd']:
            if current_data['min_amount_usd'] >= current_data['max_amount_usd']:
                raise ValidationException("Minimum USD amount must be less than maximum USD amount")
        
        if current_data['min_amount_khr'] and current_data['max_amount_khr']:
            if current_data['min_amount_khr'] >= current_data['max_amount_khr']:
                raise ValidationException("Minimum KHR amount must be less than maximum KHR amount")
        
        # Validate interest rate ranges
        if current_data['interest_rate_min'] and current_data['interest_rate_max']:
            if current_data['interest_rate_min'] >= current_data['interest_rate_max']:
                raise ValidationException("Minimum interest rate must be less than maximum interest rate")
        
        # Validate term ranges
        if current_data['term_min_months'] and current_data['term_max_months']:
            if current_data['term_min_months'] >= current_data['term_max_months']:
                raise ValidationException("Minimum term must be less than maximum term") 