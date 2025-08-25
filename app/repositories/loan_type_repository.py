from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.repositories.base import BaseRepository
from app.domain.reference_models import LoanType
from app.domain.loan_type import LoanTypeCreate, LoanTypeUpdate

class LoanTypeRepository(BaseRepository[LoanType, LoanTypeCreate, LoanTypeUpdate]):
    """Repository for LoanType operations."""
    
    def __init__(self):
        super().__init__(LoanType)
    
    def get_by_id(self, db: Session, loan_type_id: int) -> Optional[LoanType]:
        """Get loan type by ID."""
        return self.get(db, loan_type_id)
    
    def get_by_code(self, db: Session, code: str) -> Optional[LoanType]:
        """Get loan type by code."""
        return db.query(LoanType).filter(LoanType.code == code.upper()).first()
    
    def get_active_loan_types(self, db: Session) -> List[LoanType]:
        """Get all active loan types."""
        return db.query(LoanType).filter(LoanType.is_active == True).all()
    
    def search_loan_types(
        self, 
        db: Session,
        search: Optional[str] = None, 
        is_active: Optional[bool] = None,
        min_amount_usd: Optional[int] = None,
        max_amount_usd: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[LoanType]:
        """Search loan types with filters."""
        query = db.query(LoanType)
        
        if search:
            search_filter = or_(
                LoanType.code.ilike(f"%{search}%"),
                LoanType.name.ilike(f"%{search}%"),
                LoanType.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(LoanType.is_active == is_active)
        
        if min_amount_usd is not None:
            query = query.filter(LoanType.min_amount_usd >= min_amount_usd)
        
        if max_amount_usd is not None:
            query = query.filter(LoanType.max_amount_usd <= max_amount_usd)
        
        return query.offset(skip).limit(limit).all()
    
    def count_loan_types(
        self, 
        db: Session,
        search: Optional[str] = None, 
        is_active: Optional[bool] = None,
        min_amount_usd: Optional[int] = None,
        max_amount_usd: Optional[int] = None
    ) -> int:
        """Count loan types with filters."""
        query = db.query(LoanType)
        
        if search:
            search_filter = or_(
                LoanType.code.ilike(f"%{search}%"),
                LoanType.name.ilike(f"%{search}%"),
                LoanType.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(LoanType.is_active == is_active)
        
        if min_amount_usd is not None:
            query = query.filter(LoanType.min_amount_usd >= min_amount_usd)
        
        if max_amount_usd is not None:
            query = query.filter(LoanType.max_amount_usd <= max_amount_usd)
        
        return query.count()
    
    def code_exists(self, db: Session, code: str, exclude_id: Optional[int] = None) -> bool:
        """Check if loan type code already exists."""
        query = db.query(LoanType).filter(LoanType.code == code.upper())
        if exclude_id:
            query = query.filter(LoanType.id != exclude_id)
        return query.first() is not None 