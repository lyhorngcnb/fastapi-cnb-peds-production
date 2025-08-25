from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.services.loan_request_service import LoanRequestService
from app.schemas.loan_request import (
    LoanRequestCreateSchema,
    LoanRequestUpdateSchema,
    LoanRequestResponseSchema,
    LoanRequestListSchema
)
from app.core.dependencies import get_current_active_user, require_permission
from app.core.exceptions import NotFoundException, ValidationException
from app.domain.rbac_models import User

router = APIRouter(prefix="/loan-requests", tags=["loan-requests"])

@router.post("/", response_model=LoanRequestResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_loan_request(
    loan_request_data: LoanRequestCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("loan_request:create"))
):
    """Create a new loan request."""
    try:
        loan_request_service = LoanRequestService()
        loan_request = loan_request_service.create_loan_request(db, loan_request_data, current_user.id)
        return loan_request
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=LoanRequestListSchema)
async def get_loan_requests(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by loan request status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    loan_type_id: Optional[int] = Query(None, description="Filter by loan type ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("loan_request:read"))
):
    """Get loan requests with pagination and filtering."""
    try:
        loan_request_service = LoanRequestService()
        result = loan_request_service.get_loan_requests_with_filters(
            db, page, size, status, customer_id, loan_type_id
        )
        return LoanRequestListSchema(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{loan_request_id}", response_model=LoanRequestResponseSchema)
async def get_loan_request(
    loan_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("loan_request:read"))
):
    """Get a specific loan request by ID."""
    try:
        loan_request_service = LoanRequestService()
        loan_request = loan_request_service.get_loan_request(db, loan_request_id)
        if not loan_request:
            raise NotFoundException("Loan Request", loan_request_id)
        return loan_request
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{loan_request_id}", response_model=LoanRequestResponseSchema)
async def update_loan_request(
    loan_request_id: int,
    loan_request_data: LoanRequestUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("loan_request:update"))
):
    """Update a loan request."""
    try:
        loan_request_service = LoanRequestService()
        loan_request = loan_request_service.update_loan_request(db, loan_request_id, loan_request_data)
        if not loan_request:
            raise NotFoundException("Loan Request", loan_request_id)
        return loan_request
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{loan_request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan_request(
    loan_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("loan_request:delete"))
):
    """Delete a loan request."""
    try:
        loan_request_service = LoanRequestService()
        success = loan_request_service.delete_loan_request(db, loan_request_id)
        if not success:
            raise NotFoundException("Loan Request", loan_request_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{loan_request_id}/status", response_model=LoanRequestResponseSchema)
async def update_loan_request_status(
    loan_request_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("loan_request:update"))
):
    """Update loan request status."""
    try:
        loan_request_service = LoanRequestService()
        loan_request = loan_request_service.update_status(db, loan_request_id, status)
        if not loan_request:
            raise NotFoundException("Loan Request", loan_request_id)
        return loan_request
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 