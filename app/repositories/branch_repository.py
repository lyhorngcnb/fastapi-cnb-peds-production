from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.repositories.base import BaseRepository
from app.domain.reference_models import Branch
from app.domain.branch_model import BranchCreate, BranchUpdate

class BranchRepository(BaseRepository[Branch, BranchCreate, BranchUpdate]):
    """Repository for Branch operations."""
    
    def __init__(self):
        super().__init__(Branch)
    
    def get_by_id(self, db: Session, branch_id: int) -> Optional[Branch]:
        """Get branch by ID."""
        return self.get(db, branch_id)
    
    def get_by_code(self, db: Session, code: str) -> Optional[Branch]:
        """Get branch by code."""
        return db.query(Branch).filter(Branch.code == code.upper()).first()
    
    def get_active_branches(self, db: Session) -> List[Branch]:
        """Get all active branches."""
        return db.query(Branch).filter(Branch.is_active == True).all()
    
    def search_branches(
        self, 
        db: Session,
        search: Optional[str] = None, 
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Branch]:
        """Search branches with filters."""
        query = db.query(Branch)
        
        if search:
            search_filter = or_(
                Branch.code.ilike(f"%{search}%"),
                Branch.name.ilike(f"%{search}%"),
                Branch.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(Branch.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def count_branches(
        self, 
        db: Session,
        search: Optional[str] = None, 
        is_active: Optional[bool] = None
    ) -> int:
        """Count branches with filters."""
        query = db.query(Branch)
        
        if search:
            search_filter = or_(
                Branch.code.ilike(f"%{search}%"),
                Branch.name.ilike(f"%{search}%"),
                Branch.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(Branch.is_active == is_active)
        
        return query.count()
    
    def code_exists(self, db: Session, code: str, exclude_id: Optional[int] = None) -> bool:
        """Check if branch code already exists."""
        query = db.query(Branch).filter(Branch.code == code.upper())
        if exclude_id:
            query = query.filter(Branch.id != exclude_id)
        return query.first() is not None 