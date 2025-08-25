from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.services.collateral_service import CollateralService
from app.schemas.collateral import (
    CollateralCreateSchema,
    CollateralUpdateSchema,
    CollateralResponseSchema,
    CollateralListSchema
)
from app.core.dependencies import get_current_active_user, require_permission
from app.core.exceptions import NotFoundException, ValidationException
from app.domain.rbac_models import User

router = APIRouter(prefix="/collaterals", tags=["collaterals"])

@router.post("/", response_model=CollateralResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_collateral(
    collateral_data: CollateralCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("collateral:create"))
):
    """Create a new collateral."""
    try:
        collateral_service = CollateralService()
        collateral = collateral_service.create_collateral(db, collateral_data, current_user.id)
        return collateral
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=CollateralListSchema)
async def get_collaterals(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    collateral_type: Optional[str] = Query(None, description="Filter by collateral type"),
    loan_request_id: Optional[int] = Query(None, description="Filter by loan request ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("collateral:read"))
):
    """Get collaterals with pagination and filtering."""
    try:
        collateral_service = CollateralService()
        result = collateral_service.get_collaterals_with_filters(
            db, page, size, collateral_type, loan_request_id
        )
        return CollateralListSchema(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{collateral_id}", response_model=CollateralResponseSchema)
async def get_collateral(
    collateral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("collateral:read"))
):
    """Get a specific collateral by ID."""
    try:
        collateral_service = CollateralService()
        collateral = collateral_service.get_collateral(db, collateral_id)
        if not collateral:
            raise NotFoundException("Collateral", collateral_id)
        return collateral
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{collateral_id}", response_model=CollateralResponseSchema)
async def update_collateral(
    collateral_id: int,
    collateral_data: CollateralUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("collateral:update"))
):
    """Update a collateral."""
    try:
        collateral_service = CollateralService()
        collateral = collateral_service.update_collateral(db, collateral_id, collateral_data)
        if not collateral:
            raise NotFoundException("Collateral", collateral_id)
        return collateral
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{collateral_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collateral(
    collateral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("collateral:delete"))
):
    """Delete a collateral."""
    try:
        collateral_service = CollateralService()
        success = collateral_service.delete_collateral(db, collateral_id)
        if not success:
            raise NotFoundException("Collateral", collateral_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/loan-request/{loan_request_id}", response_model=List[CollateralResponseSchema])
async def get_collaterals_by_loan_request(
    loan_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("collateral:read"))
):
    """Get all collaterals for a specific loan request."""
    try:
        collateral_service = CollateralService()
        collaterals = collateral_service.get_collaterals_by_loan_request(db, loan_request_id)
        return collaterals
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 