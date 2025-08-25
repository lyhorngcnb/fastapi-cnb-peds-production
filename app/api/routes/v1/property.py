from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.core.auth import get_current_user
from app.domain.rbac_models import User
from app.domain.property_schemas import (
    PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListResponse,
    LandDetailCreate, LandDetailUpdate, LandDetailResponse,
    BuildingDetailCreate, BuildingDetailUpdate, BuildingDetailResponse,
    GoogleMapCreate, GoogleMapUpdate, GoogleMapResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse
)
from app.core.property_service import PropertyService
from app.core.minio_service import MinioService
from app.domain.property_models import Document
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/properties", tags=["Properties"])

# Property CRUD endpoints
@router.post("/", response_model=PropertyResponse)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new property evaluation."""
    try:
        property_obj = PropertyService.create_property(db, property_data, current_user.id)
        return property_obj
    except Exception as e:
        logger.error(f"Error creating property: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PropertyListResponse)
def get_properties(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in property code, title number, or owner names"),
    property_code: Optional[str] = Query(None, description="Filter by property code"),
    type_of_property: Optional[str] = Query(None, description="Filter by property type"),
    ownership_title: Optional[str] = Query(None, description="Filter by ownership title"),
    requester_id: Optional[int] = Query(None, description="Filter by loan request ID"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    province_id: Optional[int] = Query(None, description="Filter by province ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get properties with pagination and filters."""
    try:
        properties, total = PropertyService.get_properties(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            property_code=property_code,
            type_of_property=type_of_property,
            ownership_title=ownership_title,
            requester_id=requester_id,
            owner_id=owner_id,
            province_id=province_id,
            is_active=is_active
        )
        
        return PropertyListResponse(
            properties=properties,
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        logger.error(f"Error getting properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific property by ID."""
    try:
        property_obj = PropertyService.get_property(db, property_id)
        return property_obj
    except Exception as e:
        logger.error(f"Error getting property {property_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a property."""
    try:
        property_obj = PropertyService.update_property(db, property_id, property_data)
        return property_obj
    except Exception as e:
        logger.error(f"Error updating property {property_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a property."""
    try:
        PropertyService.delete_property(db, property_id)
        return {"message": "Property deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting property {property_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/")
def get_property_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get property evaluation statistics."""
    try:
        stats = PropertyService.get_property_statistics(db)
        return stats
    except Exception as e:
        logger.error(f"Error getting property statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Land Detail endpoints
@router.post("/{property_id}/land-details", response_model=LandDetailResponse)
def create_land_detail(
    property_id: int,
    land_detail_data: LandDetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add land detail to a property."""
    try:
        land_detail = PropertyService.create_land_detail(db, property_id, land_detail_data)
        return land_detail
    except Exception as e:
        logger.error(f"Error creating land detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/land-details/{land_detail_id}", response_model=LandDetailResponse)
def update_land_detail(
    land_detail_id: int,
    land_detail_data: LandDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a land detail."""
    try:
        land_detail = PropertyService.update_land_detail(db, land_detail_id, land_detail_data)
        return land_detail
    except Exception as e:
        logger.error(f"Error updating land detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Building Detail endpoints
@router.post("/{property_id}/buildings", response_model=BuildingDetailResponse)
def create_building_detail(
    property_id: int,
    building_detail_data: BuildingDetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add building detail to a property."""
    try:
        building_detail = PropertyService.create_building_detail(db, property_id, building_detail_data)
        return building_detail
    except Exception as e:
        logger.error(f"Error creating building detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/building-details/{building_detail_id}", response_model=BuildingDetailResponse)
def update_building_detail(
    building_detail_id: int,
    building_detail_data: BuildingDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a building detail."""
    try:
        building_detail = PropertyService.update_building_detail(db, building_detail_id, building_detail_data)
        return building_detail
    except Exception as e:
        logger.error(f"Error updating building detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Document endpoints
@router.post("/{property_id}/documents", response_model=DocumentResponse)
def upload_document(
    property_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    file_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for a property."""
    try:
        # Validate file type
        if file_type not in ["PDF", "Image", "Other"]:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Upload to MinIO
        minio_service = MinioService()
        file_url = minio_service.upload_file(file)
        
        # Create document record
        document_data = DocumentCreate(
            file_url=file_url,
            file_type=file_type,
            title=title or file.filename
        )
        
        document = PropertyService.create_document(db, property_id, document_data, current_user.id)
        return document
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a document."""
    try:
        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file from MinIO
        minio_service = MinioService()
        file_data = minio_service.get_file(document.file_url)
        
        return {
            "file_url": document.file_url,
            "file_type": document.file_type,
            "title": document.title
        }
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enum endpoints for frontend dropdowns
@router.get("/enums/ownership-titles")
def get_ownership_title_enums():
    """Get ownership title enum values."""
    from app.domain.property_models import OwnershipTitleEnum
    return [{"value": enum.value, "label": enum.value} for enum in OwnershipTitleEnum]

@router.get("/enums/property-types")
def get_property_type_enums():
    """Get property type enum values."""
    from app.domain.property_models import TypeOfPropertyEnum
    return [{"value": enum.value, "label": enum.value} for enum in TypeOfPropertyEnum]

@router.get("/enums/title-types")
def get_title_type_enums():
    """Get title type enum values."""
    from app.domain.property_models import TypeOfTitleEnum
    return [{"value": enum.value, "label": enum.value} for enum in TypeOfTitleEnum]

@router.get("/enums/measurement-info")
def get_measurement_info_enums():
    """Get measurement info enum values."""
    from app.domain.property_models import MeasurementInfoEnum
    return [{"value": enum.value, "label": enum.value} for enum in MeasurementInfoEnum]

@router.get("/enums/source-types")
def get_source_type_enums():
    """Get source type enum values."""
    from app.domain.property_models import SourceTypeEnum
    return [{"value": enum.value, "label": enum.value} for enum in SourceTypeEnum]

@router.get("/enums/file-types")
def get_file_type_enums():
    """Get file type enum values."""
    from app.domain.property_models import FileTypeEnum
    return [{"value": enum.value, "label": enum.value} for enum in FileTypeEnum] 