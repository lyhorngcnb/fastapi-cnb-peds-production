from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.repositories.base import BaseRepository
from app.domain.reference_models import RequestType
from app.schemas.request_type import RequestTypeCreate, RequestTypeUpdate

class RequestTypeRepository(BaseRepository[RequestType, RequestTypeCreate, RequestTypeUpdate]):
    """Repository for RequestType operations."""
    
    def __init__(self):
        super().__init__(RequestType)
    
    def get_by_id(self, db: Session, request_type_id: int) -> Optional[RequestType]:
        """Get request type by ID."""
        return self.get(db, request_type_id)
    
    def get_by_code(self, db: Session, code: str) -> Optional[RequestType]:
        """Get request type by code."""
        return db.query(RequestType).filter(RequestType.code == code.upper()).first()
    
    def get_active_request_types(self, db: Session) -> List[RequestType]:
        """Get all active request types."""
        return db.query(RequestType).filter(RequestType.is_active == True).all()
    
    def search_request_types(
        self, 
        db: Session,
        search: Optional[str] = None, 
        is_active: Optional[bool] = None,
        requires_collateral: Optional[bool] = None,
        requires_guarantor: Optional[bool] = None,
        requires_insurance: Optional[bool] = None,
        approval_level: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[RequestType]:
        """Search request types with filters."""
        query = db.query(RequestType)
        
        if search:
            search_filter = or_(
                RequestType.code.ilike(f"%{search}%"),
                RequestType.name.ilike(f"%{search}%"),
                RequestType.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(RequestType.is_active == is_active)
        
        if requires_collateral is not None:
            query = query.filter(RequestType.requires_collateral == requires_collateral)
        
        if requires_guarantor is not None:
            query = query.filter(RequestType.requires_guarantor == requires_guarantor)
        
        if requires_insurance is not None:
            query = query.filter(RequestType.requires_insurance == requires_insurance)
        
        if approval_level is not None:
            query = query.filter(RequestType.approval_level == approval_level)
        
        return query.offset(skip).limit(limit).all()
    
    def count_request_types(
        self, 
        db: Session,
        search: Optional[str] = None, 
        is_active: Optional[bool] = None,
        requires_collateral: Optional[bool] = None,
        requires_guarantor: Optional[bool] = None,
        requires_insurance: Optional[bool] = None,
        approval_level: Optional[int] = None
    ) -> int:
        """Count request types with filters."""
        query = db.query(RequestType)
        
        if search:
            search_filter = or_(
                RequestType.code.ilike(f"%{search}%"),
                RequestType.name.ilike(f"%{search}%"),
                RequestType.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(RequestType.is_active == is_active)
        
        if requires_collateral is not None:
            query = query.filter(RequestType.requires_collateral == requires_collateral)
        
        if requires_guarantor is not None:
            query = query.filter(RequestType.requires_guarantor == requires_guarantor)
        
        if requires_insurance is not None:
            query = query.filter(RequestType.requires_insurance == requires_insurance)
        
        if approval_level is not None:
            query = query.filter(RequestType.approval_level == approval_level)
        
        return query.count()
    
    def code_exists(self, db: Session, code: str, exclude_id: Optional[int] = None) -> bool:
        """Check if request type code already exists."""
        query = db.query(RequestType).filter(RequestType.code == code.upper())
        if exclude_id:
            query = query.filter(RequestType.id != exclude_id)
        return query.first() is not None 