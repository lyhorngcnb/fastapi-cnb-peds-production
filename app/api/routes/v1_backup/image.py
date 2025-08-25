from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.services.image_service import ImageService
from app.schemas.image import ImageResponseSchema, ImageListSchema
from app.core.dependencies import get_current_active_user, require_permission
from app.core.exceptions import NotFoundException, ValidationException
from app.domain.rbac_models import User

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload", response_model=ImageResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    entity_type: str = None,
    entity_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("image:create"))
):
    """Upload an image file."""
    try:
        image_service = ImageService()
        image = image_service.upload_image(db, file, entity_type, entity_id, current_user.id)
        return image
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=ImageListSchema)
async def get_images(
    entity_type: str = None,
    entity_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("image:read"))
):
    """Get images with optional filtering by entity."""
    try:
        image_service = ImageService()
        images = image_service.get_images(db, entity_type, entity_id)
        return ImageListSchema(images=images, total=len(images))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{image_id}", response_model=ImageResponseSchema)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("image:read"))
):
    """Get a specific image by ID."""
    try:
        image_service = ImageService()
        image = image_service.get_image(db, image_id)
        if not image:
            raise NotFoundException("Image", image_id)
        return image
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("image:delete"))
):
    """Delete an image."""
    try:
        image_service = ImageService()
        success = image_service.delete_image(db, image_id)
        if not success:
            raise NotFoundException("Image", image_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/entity/{entity_type}/{entity_id}", response_model=List[ImageResponseSchema])
async def get_images_by_entity(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("image:read"))
):
    """Get all images for a specific entity."""
    try:
        image_service = ImageService()
        images = image_service.get_images_by_entity(db, entity_type, entity_id)
        return images
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 