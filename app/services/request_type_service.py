from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.repositories.request_type_repository import RequestTypeRepository
from app.domain.reference_models import RequestType
from app.domain.request_type_model import RequestTypeCreate, RequestTypeUpdate, RequestTypeResponse, RequestTypeListResponse
from app.core.exceptions import ValidationException, ConflictException, NotFoundException

class RequestTypeService(BaseService[RequestType, RequestTypeCreate, RequestTypeUpdate]):
    """Service for RequestType business logic."""
    
    def __init__(self, db: Session):
        self.repository = RequestTypeRepository()
        super().__init__(self.repository)
        self.db = db
    
    def create_request_type(self, request_type_data: RequestTypeCreate) -> RequestTypeResponse:
        """Create a new request type with validation."""
        # Check if code already exists
        if self.repository.code_exists(self.db, request_type_data.code):
            raise ConflictException(f"Request type with code '{request_type_data.code}' already exists")
        
        # Create request type
        created_request_type = self.repository.create(self.db, request_type_data)
        
        return RequestTypeResponse.from_orm(created_request_type)
    
    def update_request_type(self, request_type_id: int, request_type_data: RequestTypeUpdate) -> RequestTypeResponse:
        """Update an existing request type with validation."""
        # Get existing request type
        request_type = self.repository.get_by_id(self.db, request_type_id)
        if not request_type:
            raise NotFoundException(f"Request type with ID {request_type_id} not found")
        
        # Check if code already exists (if being updated)
        if request_type_data.code and self.repository.code_exists(self.db, request_type_data.code, exclude_id=request_type_id):
            raise ConflictException(f"Request type with code '{request_type_data.code}' already exists")
        
        # Update request type
        updated_request_type = self.repository.update(self.db, request_type_id, request_type_data)
        
        return RequestTypeResponse.from_orm(updated_request_type)
    
    def get_request_type(self, request_type_id: int) -> RequestTypeResponse:
        """Get a request type by ID."""
        request_type = self.repository.get_by_id(self.db, request_type_id)
        if not request_type:
            raise NotFoundException(f"Request type with ID {request_type_id} not found")
        
        return RequestTypeResponse.from_orm(request_type)
    
    def get_request_type_by_code(self, code: str) -> RequestTypeResponse:
        """Get a request type by code."""
        request_type = self.repository.get_by_code(self.db, code)
        if not request_type:
            raise NotFoundException(f"Request type with code '{code}' not found")
        
        return RequestTypeResponse.from_orm(request_type)
    
    def list_request_types(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        requires_collateral: Optional[bool] = None,
        requires_guarantor: Optional[bool] = None,
        requires_insurance: Optional[bool] = None,
        approval_level: Optional[int] = None,
        page: int = 1,
        size: int = 10
    ) -> RequestTypeListResponse:
        """List request types with pagination and filters."""
        skip = (page - 1) * size
        
        # Get request types
        request_types = self.repository.search_request_types(
            self.db,
            search=search,
            is_active=is_active,
            requires_collateral=requires_collateral,
            requires_guarantor=requires_guarantor,
            requires_insurance=requires_insurance,
            approval_level=approval_level,
            skip=skip,
            limit=size
        )
        
        # Get total count
        total = self.repository.count_request_types(
            self.db,
            search=search,
            is_active=is_active,
            requires_collateral=requires_collateral,
            requires_guarantor=requires_guarantor,
            requires_insurance=requires_insurance,
            approval_level=approval_level
        )
        
        # Calculate pages
        pages = (total + size - 1) // size
        
        return RequestTypeListResponse(
            items=[RequestTypeResponse.from_orm(request_type) for request_type in request_types],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def get_active_request_types(self) -> List[RequestTypeResponse]:
        """Get all active request types."""
        request_types = self.repository.get_active_request_types(self.db)
        return [RequestTypeResponse.from_orm(request_type) for request_type in request_types]
    
    def delete_request_type(self, request_type_id: int) -> bool:
        """Delete a request type."""
        request_type = self.repository.get_by_id(self.db, request_type_id)
        if not request_type:
            raise NotFoundException(f"Request type with ID {request_type_id} not found")
        
        # Check if request type is being used in loan requests
        if request_type.loan_requests:
            raise ValidationException("Cannot delete request type that has associated loan requests")
        
        return self.repository.delete(self.db, request_type_id)
    
    def toggle_request_type_status(self, request_type_id: int) -> RequestTypeResponse:
        """Toggle request type active status."""
        request_type = self.repository.get_by_id(self.db, request_type_id)
        if not request_type:
            raise NotFoundException(f"Request type with ID {request_type_id} not found")
        
        # Toggle status
        update_data = RequestTypeUpdate(is_active=not request_type.is_active)
        updated_request_type = self.repository.update(self.db, request_type_id, update_data)
        
        return RequestTypeResponse.from_orm(updated_request_type) 