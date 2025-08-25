from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.rbac_models import User
from app.schemas.request_type import RequestTypeCreate, RequestTypeUpdate, RequestTypeResponse, RequestTypeListResponse
from app.services.request_type_service import RequestTypeService
from app.schemas.base import MessageResponseSchema

router = APIRouter(prefix="/request-types", tags=["request-types"])

@router.post("/", response_model=RequestTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_request_type(
    request_type_data: RequestTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new request type.
    
    This endpoint allows you to create a new request type with approval workflow parameters:
    
    - **code**: Unique request type code (e.g., NEW, ADD, RENEW) - required
    - **name**: Request type name - required
    - **description**: Request type description - optional
    - **requires_collateral**: Whether this request type requires collateral - defaults to False
    - **requires_guarantor**: Whether this request type requires guarantor - defaults to False
    - **requires_insurance**: Whether this request type requires insurance - defaults to False
    - **approval_level**: Approval level required (1=Basic, 2=Manager, 3=Director) - required
    - **is_active**: Whether the request type is active - defaults to True
    
    **Approval Levels:**
    - 1: Basic approval (e.g., renewals, extensions)
    - 2: Manager approval (e.g., new loans, additions)
    - 3: Director approval (e.g., restructuring, large amounts)
    
    **Example Request:**
    ```json
    {
        "code": "REFINANCE",
        "name": "Refinance",
        "description": "Loan refinancing request",
        "requires_collateral": true,
        "requires_guarantor": false,
        "requires_insurance": true,
        "approval_level": 2,
        "is_active": true
    }
    ```
    
    **Returns:** The created request type with all details including ID and timestamps.
    """
    # require_permission(current_user, "request_type:create")
    
    request_type_service = RequestTypeService(db)
    return request_type_service.create_request_type(request_type_data)

@router.get("/", response_model=RequestTypeListResponse)
async def list_request_types(
    search: Optional[str] = Query(None, description="Search in code, name, or description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    requires_collateral: Optional[bool] = Query(None, description="Filter by collateral requirement"),
    requires_guarantor: Optional[bool] = Query(None, description="Filter by guarantor requirement"),
    requires_insurance: Optional[bool] = Query(None, description="Filter by insurance requirement"),
    approval_level: Optional[int] = Query(None, ge=1, le=5, description="Filter by approval level (1-5)"),
    page: int = Query(1, ge=1, description="Page number (minimum: 1)"),
    size: int = Query(10, ge=1, le=100, description="Page size (minimum: 1, maximum: 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List request types with pagination and filters.
    
    This endpoint returns a paginated list of request types with comprehensive filtering:
    
    - **search**: Search term for code, name, or description
    - **is_active**: Filter by active status (true/false)
    - **requires_collateral**: Filter by collateral requirement (true/false)
    - **requires_guarantor**: Filter by guarantor requirement (true/false)
    - **requires_insurance**: Filter by insurance requirement (true/false)
    - **approval_level**: Filter by approval level (1-5)
    - **page**: Page number (minimum: 1)
    - **size**: Page size (minimum: 1, maximum: 100)
    
    **Example Queries:**
    - `GET /api/v1/request-types/` - Get all request types (first page)
    - `GET /api/v1/request-types/?page=2&size=5` - Get second page with 5 items
    - `GET /api/v1/request-types/?search=new` - Search for request types with "new"
    - `GET /api/v1/request-types/?requires_collateral=true` - Get types requiring collateral
    - `GET /api/v1/request-types/?approval_level=2` - Get types requiring manager approval
    - `GET /api/v1/request-types/?is_active=true&approval_level=1` - Get active basic approval types
    
    **Returns:** Paginated list with total count, current page, and request type details.
    """
    # require_permission(current_user, "request_type:read")
    
    request_type_service = RequestTypeService(db)
    return request_type_service.list_request_types(
        search=search,
        is_active=is_active,
        requires_collateral=requires_collateral,
        requires_guarantor=requires_guarantor,
        requires_insurance=requires_insurance,
        approval_level=approval_level,
        page=page,
        size=size
    )

@router.get("/active", response_model=list[RequestTypeResponse])
async def get_active_request_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active request types.
    
    This endpoint returns a simple list of all active request types without pagination.
    Useful for dropdown menus and loan application forms.
    
    **Returns:** List of all active request types with full details.
    """
    # require_permission(current_user, "request_type:read")
    
    request_type_service = RequestTypeService(db)
    return request_type_service.get_active_request_types()

@router.get("/{request_type_id}", response_model=RequestTypeResponse)
async def get_request_type(
    request_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a request type by ID.
    
    This endpoint returns detailed information about a specific request type.
    
    - **request_type_id**: Request type's unique identifier (integer)
    
    **Example:** `GET /api/v1/request-types/1` - Get request type with ID 1
    
    **Returns:** Complete request type details including all workflow parameters and timestamps.
    
    **Errors:**
    - 404: Request type not found
    """
    # require_permission(current_user, "request_type:read")
    
    request_type_service = RequestTypeService(db)
    return request_type_service.get_request_type(request_type_id)

@router.get("/code/{code}", response_model=RequestTypeResponse)
async def get_request_type_by_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a request type by code.
    
    This endpoint returns detailed information about a specific request type using its unique code.
    
    - **code**: Request type's unique code (string, e.g., "NEW", "ADD", "RENEW")
    
    **Example:** `GET /api/v1/request-types/code/NEW` - Get request type with code "NEW"
    
    **Returns:** Complete request type details including all workflow parameters and timestamps.
    
    **Errors:**
    - 404: Request type not found
    """
    # require_permission(current_user, "request_type:read")
    
    request_type_service = RequestTypeService(db)
    return request_type_service.get_request_type_by_code(code)

@router.put("/{request_type_id}", response_model=RequestTypeResponse)
async def update_request_type(
    request_type_id: int,
    request_type_data: RequestTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a request type.
    
    This endpoint allows you to update an existing request type. All fields are optional.
    Only provided fields will be updated.
    
    - **request_type_id**: Request type's unique identifier
    - **request_type_data**: Updated request type data (all fields optional)
    
    **Example Request:**
    ```json
    {
        "name": "Updated New Loan Request",
        "requires_guarantor": false,
        "approval_level": 1,
        "is_active": false
    }
    ```
    
    **Returns:** Updated request type with all current details.
    
    **Errors:**
    - 404: Request type not found
    - 400: Validation error (e.g., invalid approval level)
    """
    # require_permission(current_user, "request_type:update")
    
    request_type_service = RequestTypeService(db)
    return request_type_service.update_request_type(request_type_id, request_type_data)

@router.patch("/{request_type_id}/toggle-status", response_model=RequestTypeResponse)
async def toggle_request_type_status(
    request_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle request type active status.
    
    This endpoint toggles the active status of a request type (true ↔ false).
    Useful for quickly enabling/disabling request types without full update.
    
    - **request_type_id**: Request type's unique identifier
    
    **Example:** `PATCH /api/v1/request-types/1/toggle-status` - Toggle status of request type ID 1
    
    **Returns:** Updated request type with toggled status.
    
    **Errors:**
    - 404: Request type not found
    """
    # require_permission(current_user, "request_type:update")
    
    request_type_service = RequestTypeService(db)
    return request_type_service.toggle_request_type_status(request_type_id)

@router.delete("/{request_type_id}", response_model=MessageResponseSchema)
async def delete_request_type(
    request_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a request type.
    
    This endpoint performs a soft delete of a request type (sets is_active to false).
    The request type data is preserved but marked as inactive.
    
    **Note:** Cannot delete request types that have associated loan requests.
    
    - **request_type_id**: Request type's unique identifier
    
    **Example:** `DELETE /api/v1/request-types/1` - Soft delete request type ID 1
    
    **Returns:** Success message confirming deletion.
    
    **Errors:**
    - 404: Request type not found
    - 400: Cannot delete (has associated loan requests)
    """
    # require_permission(current_user, "request_type:delete")
    
    request_type_service = RequestTypeService(db)
    request_type_service.delete_request_type(request_type_id)
    return MessageResponseSchema(message="Request type deleted successfully") 