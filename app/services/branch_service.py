from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.repositories.branch_repository import BranchRepository
from app.domain.reference_models import Branch
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse, BranchListResponse
from app.core.exceptions import ValidationException, ConflictException, NotFoundException

class BranchService(BaseService[Branch, BranchCreate, BranchUpdate]):
    """Service for Branch business logic."""
    
    def __init__(self, db: Session):
        self.repository = BranchRepository()
        super().__init__(self.repository)
        self.db = db
    
    def create_branch(self, branch_data: BranchCreate) -> BranchResponse:
        """Create a new branch with validation."""
        # Check if code already exists
        if self.repository.code_exists(self.db, branch_data.code):
            raise ConflictException(f"Branch with code '{branch_data.code}' already exists")
        
        # Create branch
        created_branch = self.repository.create(self.db, branch_data)
        
        return BranchResponse.from_orm(created_branch)
    
    def update_branch(self, branch_id: int, branch_data: BranchUpdate) -> BranchResponse:
        """Update an existing branch with validation."""
        # Get existing branch
        branch = self.repository.get_by_id(self.db, branch_id)
        if not branch:
            raise NotFoundException(f"Branch with ID {branch_id} not found")
        
        # Check if code already exists (if being updated)
        if branch_data.code and self.repository.code_exists(self.db, branch_data.code, exclude_id=branch_id):
            raise ConflictException(f"Branch with code '{branch_data.code}' already exists")
        
        # Update branch
        updated_branch = self.repository.update(self.db, branch_id, branch_data)
        
        return BranchResponse.from_orm(updated_branch)
    
    def get_branch(self, branch_id: int) -> BranchResponse:
        """Get a branch by ID."""
        branch = self.repository.get_by_id(self.db, branch_id)
        if not branch:
            raise NotFoundException(f"Branch with ID {branch_id} not found")
        
        return BranchResponse.from_orm(branch)
    
    def get_branch_by_code(self, code: str) -> BranchResponse:
        """Get a branch by code."""
        branch = self.repository.get_by_code(self.db, code)
        if not branch:
            raise NotFoundException(f"Branch with code '{code}' not found")
        
        return BranchResponse.from_orm(branch)
    
    def list_branches(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 10
    ) -> BranchListResponse:
        """List branches with pagination and filters."""
        skip = (page - 1) * size
        
        # Get branches
        branches = self.repository.search_branches(
            self.db,
            search=search,
            is_active=is_active,
            skip=skip,
            limit=size
        )
        
        # Get total count
        total = self.repository.count_branches(self.db, search=search, is_active=is_active)
        
        # Calculate pages
        pages = (total + size - 1) // size
        
        return BranchListResponse(
            items=[BranchResponse.from_orm(branch) for branch in branches],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def get_active_branches(self) -> List[BranchResponse]:
        """Get all active branches."""
        branches = self.repository.get_active_branches(self.db)
        return [BranchResponse.from_orm(branch) for branch in branches]
    
    def delete_branch(self, branch_id: int) -> bool:
        """Delete a branch."""
        branch = self.repository.get_by_id(self.db, branch_id)
        if not branch:
            raise NotFoundException(f"Branch with ID {branch_id} not found")
        
        # Check if branch is being used in loan requests
        if branch.loan_requests:
            raise ValidationException("Cannot delete branch that has associated loan requests")
        
        return self.repository.delete(self.db, branch_id)
    
    def toggle_branch_status(self, branch_id: int) -> BranchResponse:
        """Toggle branch active status."""
        branch = self.repository.get_by_id(self.db, branch_id)
        if not branch:
            raise NotFoundException(f"Branch with ID {branch_id} not found")
        
        # Toggle status
        update_data = BranchUpdate(is_active=not branch.is_active)
        updated_branch = self.repository.update(self.db, branch_id, update_data)
        
        return BranchResponse.from_orm(updated_branch) 