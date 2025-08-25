from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.services.property_service import PropertyService
from app.schemas.property import (
    PropertyCreateSchema,
    PropertyUpdateSchema,
    PropertyResponseSchema,
    PropertyListSchema
)
from app.core.dependencies import get_current_active_user, require_permission
from app.core.exceptions import NotFoundException, ValidationException
from app.domain.rbac_models import User

router = APIRouter(prefix="/properties", tags=["properties"])

@router.post("/", response_model=PropertyResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create"))
):
    """Create a new property."""
    try:
        property_service = PropertyService()
        property_obj = property_service.create_property(db, property_data, current_user.id)
        return property_obj
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=PropertyListSchema)
async def get_properties(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term for property address or description"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    province_id: Optional[int] = Query(None, description="Filter by province ID"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:read"))
):
    """Get properties with pagination and filtering."""
    try:
        property_service = PropertyService()
        result = property_service.get_properties_with_filters(
            db, page, size, search, property_type, province_id, district_id
        )
        return PropertyListSchema(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{property_id}", response_model=PropertyResponseSchema)
async def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:read"))
):
    """Get a specific property by ID."""
    try:
        property_service = PropertyService()
        property_obj = property_service.get_property(db, property_id)
        if not property_obj:
            raise NotFoundException("Property", property_id)
        return property_obj
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{property_id}", response_model=PropertyResponseSchema)
async def update_property(
    property_id: int,
    property_data: PropertyUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update"))
):
    """Update a property."""
    try:
        property_service = PropertyService()
        property_obj = property_service.update_property(db, property_id, property_data)
        if not property_obj:
            raise NotFoundException("Property", property_id)
        return property_obj
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete"))
):
    """Delete a property."""
    try:
        property_service = PropertyService()
        success = property_service.delete_property(db, property_id)
        if not success:
            raise NotFoundException("Property", property_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 