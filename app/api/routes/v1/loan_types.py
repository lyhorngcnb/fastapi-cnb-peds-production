from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.rbac_models import User
from app.domain.loan_type import LoanTypeCreate, LoanTypeUpdate, LoanTypeResponse, LoanTypeListResponse
from app.services.loan_type_service import LoanTypeService
from app.domain.base import MessageResponseSchema

router = APIRouter(prefix="/loan-types", tags=["loan-types"])

@router.post("/", response_model=LoanTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_loan_type(
    loan_type_data: LoanTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new loan type.
    
    This endpoint allows you to create a new loan type with comprehensive financial parameters:
    
    - **code**: Unique loan type code (e.g., SME_LOAN, HOME_LOAN) - required
    - **name**: Loan type name - required
    - **description**: Loan type description - optional
    - **min_amount_usd**: Minimum loan amount in USD - required
    - **max_amount_usd**: Maximum loan amount in USD - required
    - **min_amount_khr**: Minimum loan amount in KHR - required
    - **max_amount_khr**: Maximum loan amount in KHR - required
    - **interest_rate_min**: Minimum interest rate percentage - required
    - **interest_rate_max**: Maximum interest rate percentage - required
    - **term_min_months**: Minimum loan term in months - required
    - **term_max_months**: Maximum loan term in months - required
    - **is_active**: Whether the loan type is active - defaults to True
    
    **Example Request:**
    ```json
    {
        "code": "PERSONAL_LOAN",
        "name": "Personal Loan",
        "description": "Personal loan for individual customers",
        "min_amount_usd": 500,
        "max_amount_usd": 50000,
        "min_amount_khr": 2000000,
        "max_amount_khr": 200000000,
        "interest_rate_min": 10,
        "interest_rate_max": 18,
        "term_min_months": 6,
        "term_max_months": 36,
        "is_active": true
    }
    ```
    
    **Returns:** The created loan type with all details including ID and timestamps.
    """
    # require_permission(current_user, "loan_type:create")
    
    loan_type_service = LoanTypeService(db)
    return loan_type_service.create_loan_type(loan_type_data)

@router.get("/", response_model=LoanTypeListResponse)
async def list_loan_types(
    search: Optional[str] = Query(None, description="Search in code, name, or description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number (minimum: 1)"),
    size: int = Query(10, ge=1, le=100, description="Page size (minimum: 1, maximum: 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List loan types with pagination and filters.
    
    This endpoint returns a paginated list of loan types with optional filtering:
    
    - **search**: Search term for code, name, or description
    - **is_active**: Filter by active status (true/false)
    - **page**: Page number (minimum: 1)
    - **size**: Page size (minimum: 1, maximum: 100)
    
    **Example Queries:**
    - `GET /api/v1/loan-types/` - Get all loan types (first page)
    - `GET /api/v1/loan-types/?page=2&size=5` - Get second page with 5 items
    - `GET /api/v1/loan-types/?search=sme` - Search for loan types with "sme"
    - `GET /api/v1/loan-types/?is_active=true` - Get only active loan types
    
    **Returns:** Paginated list with total count, current page, and loan type details.
    """
    # require_permission(current_user, "loan_type:read")
    
    loan_type_service = LoanTypeService(db)
    return loan_type_service.list_loan_types(
        search=search,
        is_active=is_active,
        page=page,
        size=size
    )

@router.get("/active", response_model=list[LoanTypeResponse])
async def get_active_loan_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active loan types.
    
    This endpoint returns a simple list of all active loan types without pagination.
    Useful for dropdown menus and loan application forms.
    
    **Returns:** List of all active loan types with full details.
    """
    # require_permission(current_user, "loan_type:read")
    
    loan_type_service = LoanTypeService(db)
    return loan_type_service.get_active_loan_types()

@router.get("/{loan_type_id}", response_model=LoanTypeResponse)
async def get_loan_type(
    loan_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a loan type by ID.
    
    This endpoint returns detailed information about a specific loan type.
    
    - **loan_type_id**: Loan type's unique identifier (integer)
    
    **Example:** `GET /api/v1/loan-types/1` - Get loan type with ID 1
    
    **Returns:** Complete loan type details including all financial parameters and timestamps.
    
    **Errors:**
    - 404: Loan type not found
    """
    # require_permission(current_user, "loan_type:read")
    
    loan_type_service = LoanTypeService(db)
    return loan_type_service.get_loan_type(loan_type_id)

@router.get("/code/{code}", response_model=LoanTypeResponse)
async def get_loan_type_by_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a loan type by code.
    
    This endpoint returns detailed information about a specific loan type using its unique code.
    
    - **code**: Loan type's unique code (string, e.g., "SME_LOAN", "HOME_LOAN")
    
    **Example:** `GET /api/v1/loan-types/code/SME_LOAN` - Get loan type with code "SME_LOAN"
    
    **Returns:** Complete loan type details including all financial parameters and timestamps.
    
    **Errors:**
    - 404: Loan type not found
    """
    # require_permission(current_user, "loan_type:read")
    
    loan_type_service = LoanTypeService(db)
    return loan_type_service.get_loan_type_by_code(code)

@router.put("/{loan_type_id}", response_model=LoanTypeResponse)
async def update_loan_type(
    loan_type_id: int,
    loan_type_data: LoanTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a loan type.
    
    This endpoint allows you to update an existing loan type. All fields are optional.
    Only provided fields will be updated.
    
    - **loan_type_id**: Loan type's unique identifier
    - **loan_type_data**: Updated loan type data (all fields optional)
    
    **Example Request:**
    ```json
    {
        "name": "Updated SME Loan",
        "max_amount_usd": 150000,
        "interest_rate_max": 16,
        "term_max_months": 72,
        "is_active": false
    }
    ```
    
    **Returns:** Updated loan type with all current details.
    
    **Errors:**
    - 404: Loan type not found
    - 400: Validation error (e.g., max amount less than min amount)
    """
    # require_permission(current_user, "loan_type:update")
    
    loan_type_service = LoanTypeService(db)
    return loan_type_service.update_loan_type(loan_type_id, loan_type_data)

@router.patch("/{loan_type_id}/toggle-status", response_model=LoanTypeResponse)
async def toggle_loan_type_status(
    loan_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle loan type active status.
    
    This endpoint toggles the active status of a loan type (true ↔ false).
    Useful for quickly enabling/disabling loan types without full update.
    
    - **loan_type_id**: Loan type's unique identifier
    
    **Example:** `PATCH /api/v1/loan-types/1/toggle-status` - Toggle status of loan type ID 1
    
    **Returns:** Updated loan type with toggled status.
    
    **Errors:**
    - 404: Loan type not found
    """
    # require_permission(current_user, "loan_type:update")
    
    loan_type_service = LoanTypeService(db)
    return loan_type_service.toggle_loan_type_status(loan_type_id)

@router.delete("/{loan_type_id}", response_model=MessageResponseSchema)
async def delete_loan_type(
    loan_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a loan type.
    
    This endpoint performs a soft delete of a loan type (sets is_active to false).
    The loan type data is preserved but marked as inactive.
    
    **Note:** Cannot delete loan types that have associated loan requests.
    
    - **loan_type_id**: Loan type's unique identifier
    
    **Example:** `DELETE /api/v1/loan-types/1` - Soft delete loan type ID 1
    
    **Returns:** Success message confirming deletion.
    
    **Errors:**
    - 404: Loan type not found
    - 400: Cannot delete (has associated loan requests)
    """
    # require_permission(current_user, "loan_type:delete")
    
    loan_type_service = LoanTypeService(db)
    loan_type_service.delete_loan_type(loan_type_id)
    return MessageResponseSchema(message="Loan type deleted successfully") 