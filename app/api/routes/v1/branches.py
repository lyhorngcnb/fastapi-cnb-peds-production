from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.rbac_models import User
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse, BranchListResponse
from app.services.branch_service import BranchService
from app.schemas.base import MessageResponseSchema

router = APIRouter(prefix="/branches", tags=["branches"])

@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch_data: BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new branch.
    
    This endpoint allows you to create a new branch with the following information:
    
    - **code**: Unique branch code (e.g., OLP, MRO, BBB) - required
    - **name**: Branch name - required
    - **description**: Branch description - optional
    - **address**: Branch address - optional
    - **phone**: Branch phone number - optional
    - **email**: Branch email - optional
    - **is_active**: Whether the branch is active - defaults to True
    
    **Example Request:**
    ```json
    {
        "code": "NEW_BRANCH",
        "name": "New Branch Location",
        "description": "A new branch for testing",
        "address": "123 Main Street, City",
        "phone": "+855-12-345-678",
        "email": "newbranch@example.com",
        "is_active": true
    }
    ```
    
    **Returns:** The created branch with all details including ID and timestamps.
    """
    # require_permission(current_user, "branch:create")
    
    branch_service = BranchService(db)
    return branch_service.create_branch(branch_data)

@router.get("/", response_model=BranchListResponse)
async def list_branches(
    search: Optional[str] = Query(None, description="Search in code, name, or description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number (minimum: 1)"),
    size: int = Query(10, ge=1, le=100, description="Page size (minimum: 1, maximum: 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List branches with pagination and filters.
    
    This endpoint returns a paginated list of branches with optional filtering:
    
    - **search**: Search term for code, name, or description
    - **is_active**: Filter by active status (true/false)
    - **page**: Page number (minimum: 1)
    - **size**: Page size (minimum: 1, maximum: 100)
    
    **Example Queries:**
    - `GET /api/v1/branches/` - Get all branches (first page)
    - `GET /api/v1/branches/?page=2&size=5` - Get second page with 5 items
    - `GET /api/v1/branches/?search=olympic` - Search for branches with "olympic"
    - `GET /api/v1/branches/?is_active=true` - Get only active branches
    
    **Returns:** Paginated list with total count, current page, and branch details.
    """
    # require_permission(current_user, "branch:read")
    
    branch_service = BranchService(db)
    return branch_service.list_branches(
        search=search,
        is_active=is_active,
        page=page,
        size=size
    )

@router.get("/active", response_model=list[BranchResponse])
async def get_active_branches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active branches.
    
    This endpoint returns a simple list of all active branches without pagination.
    Useful for dropdown menus and simple listings.
    
    **Returns:** List of all active branches with full details.
    """
    # require_permission(current_user, "branch:read")
    
    branch_service = BranchService(db)
    return branch_service.get_active_branches()

@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a branch by ID.
    
    This endpoint returns detailed information about a specific branch.
    
    - **branch_id**: Branch's unique identifier (integer)
    
    **Example:** `GET /api/v1/branches/1` - Get branch with ID 1
    
    **Returns:** Complete branch details including all fields and timestamps.
    
    **Errors:**
    - 404: Branch not found
    """
    # require_permission(current_user, "branch:read")
    
    branch_service = BranchService(db)
    return branch_service.get_branch(branch_id)

@router.get("/code/{code}", response_model=BranchResponse)
async def get_branch_by_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a branch by code.
    
    This endpoint returns detailed information about a specific branch using its unique code.
    
    - **code**: Branch's unique code (string, e.g., "OLP", "MRO")
    
    **Example:** `GET /api/v1/branches/code/OLP` - Get branch with code "OLP"
    
    **Returns:** Complete branch details including all fields and timestamps.
    
    **Errors:**
    - 404: Branch not found
    """
    # require_permission(current_user, "branch:read")
    
    branch_service = BranchService(db)
    return branch_service.get_branch_by_code(code)

@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a branch.
    
    This endpoint allows you to update an existing branch. All fields are optional.
    Only provided fields will be updated.
    
    - **branch_id**: Branch's unique identifier
    - **branch_data**: Updated branch data (all fields optional)
    
    **Example Request:**
    ```json
    {
        "name": "Updated Branch Name",
        "description": "Updated description",
        "email": "updated@example.com",
        "is_active": false
    }
    ```
    
    **Returns:** Updated branch with all current details.
    
    **Errors:**
    - 404: Branch not found
    - 400: Validation error (e.g., invalid email format)
    """
    # require_permission(current_user, "branch:update")
    
    branch_service = BranchService(db)
    return branch_service.update_branch(branch_id, branch_data)

@router.patch("/{branch_id}/toggle-status", response_model=BranchResponse)
async def toggle_branch_status(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle branch active status.
    
    This endpoint toggles the active status of a branch (true ↔ false).
    Useful for quickly enabling/disabling branches without full update.
    
    - **branch_id**: Branch's unique identifier
    
    **Example:** `PATCH /api/v1/branches/1/toggle-status` - Toggle status of branch ID 1
    
    **Returns:** Updated branch with toggled status.
    
    **Errors:**
    - 404: Branch not found
    """
    # require_permission(current_user, "branch:update")
    
    branch_service = BranchService(db)
    return branch_service.toggle_branch_status(branch_id)

@router.delete("/{branch_id}", response_model=MessageResponseSchema)
async def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a branch.
    
    This endpoint performs a soft delete of a branch (sets is_active to false).
    The branch data is preserved but marked as inactive.
    
    **Note:** Cannot delete branches that have associated loan requests.
    
    - **branch_id**: Branch's unique identifier
    
    **Example:** `DELETE /api/v1/branches/1` - Soft delete branch ID 1
    
    **Returns:** Success message confirming deletion.
    
    **Errors:**
    - 404: Branch not found
    - 400: Cannot delete (has associated loan requests)
    """
    # require_permission(current_user, "branch:delete")
    
    branch_service = BranchService(db)
    branch_service.delete_branch(branch_id)
    return MessageResponseSchema(message="Branch deleted successfully") 