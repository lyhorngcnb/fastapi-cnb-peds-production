from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.services.customer_service import CustomerService
from app.schemas.customer import (
    CustomerCreateSchema, 
    CustomerUpdateSchema, 
    CustomerResponseSchema,
    CustomerListSchema
)
from app.core.dependencies import get_current_active_user, require_permission
from app.core.exceptions import NotFoundException, ValidationException, ConflictException
from app.domain.rbac_models import User

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer:create"))
):
    """Create a new customer."""
    try:
        customer_service = CustomerService()
        customer = customer_service.create_customer(db, customer_data)
        return customer
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=CustomerListSchema)
async def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for name, email, phone, or national ID"),
    province_id: Optional[int] = Query(None, description="Filter by province ID"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    commune_id: Optional[int] = Query(None, description="Filter by commune ID"),
    village_id: Optional[int] = Query(None, description="Filter by village ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer:read"))
):
    """Get customers with pagination and filtering."""
    try:
        customer_service = CustomerService()
        
        if search:
            result = customer_service.search_customers(db, search, page, size)
        elif any([province_id, district_id, commune_id, village_id]):
            result = customer_service.get_customers_by_location(
                db, province_id, district_id, commune_id, village_id, page, size
            )
        else:
            result = customer_service.get_multi(db, skip=(page-1)*size, limit=size)
            total = customer_service.count(db)
            result = {
                "customers": result,
                "total": total,
                "page": page,
                "size": size
            }
        
        return CustomerListSchema(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{customer_id}", response_model=CustomerResponseSchema)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer:read"))
):
    """Get a specific customer by ID."""
    try:
        customer_service = CustomerService()
        customer = customer_service.get(db, customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)
        return customer
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{customer_id}", response_model=CustomerResponseSchema)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer:update"))
):
    """Update a customer."""
    try:
        customer_service = CustomerService()
        customer = customer_service.update_customer(db, customer_id, customer_data)
        if not customer:
            raise NotFoundException("Customer", customer_id)
        return customer
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer:delete"))
):
    """Delete a customer."""
    try:
        customer_service = CustomerService()
        success = customer_service.delete(db, customer_id)
        if not success:
            raise NotFoundException("Customer", customer_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{customer_id}/loan-requests")
async def get_customer_loan_requests(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer:read"))
):
    """Get loan requests for a specific customer."""
    try:
        # This would be implemented in a loan request service
        # For now, return a placeholder
        return {"message": "Loan requests endpoint - to be implemented"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 