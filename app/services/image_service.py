import os
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.services.base import BaseService
from app.domain.property_models import Document
from app.core.exceptions import NotFoundException, ValidationException

class ImageService(BaseService[Document, dict, dict]):
    def __init__(self):
        # Initialize with a repository - for now, we'll handle this differently
        pass
    
    def upload_image(self, db: Session, file: UploadFile, entity_type: str, entity_id: int, user_id: int) -> Document:
        """Upload an image file."""
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise ValidationException("File must be an image")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file to disk (you might want to use cloud storage in production)
        upload_dir = "uploads/images"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Create document record
        document_data = {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_type": file.content_type,
            "file_size": len(content),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "created_by": user_id,
            "updated_by": user_id
        }
        
        # Create document record directly
        document = Document(**document_data)
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    def get_image(self, db: Session, image_id: int) -> Optional[Document]:
        """Get an image by ID."""
        return db.query(Document).filter(Document.id == image_id).first()
    
    def delete_image(self, db: Session, image_id: int) -> bool:
        """Delete an image."""
        image_obj = db.query(Document).filter(Document.id == image_id).first()
        if not image_obj:
            return False
        
        # Delete file from disk
        if os.path.exists(image_obj.file_path):
            os.remove(image_obj.file_path)
        
        db.delete(image_obj)
        db.commit()
        return True
    
    def get_images(self, db: Session, entity_type: Optional[str] = None, entity_id: Optional[int] = None) -> List[Document]:
        """Get images with optional filtering."""
        query = db.query(Document)
        
        if entity_type:
            query = query.filter(Document.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(Document.entity_id == entity_id)
        
        return query.all()
    
    def get_images_by_entity(self, db: Session, entity_type: str, entity_id: int) -> List[Document]:
        """Get all images for a specific entity."""
        return db.query(Document).filter(
            Document.entity_type == entity_type,
            Document.entity_id == entity_id
        ).all() 