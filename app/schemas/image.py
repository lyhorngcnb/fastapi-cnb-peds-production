from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema

class ImageBase(BaseModel):
    filename: str = Field(..., description="Generated filename")
    original_filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="File path on server")
    file_type: str = Field(..., description="File MIME type")
    file_size: int = Field(..., description="File size in bytes")
    entity_type: str = Field(..., description="Entity type (e.g., property, customer)")
    entity_id: int = Field(..., description="Entity ID")

class ImageCreateSchema(ImageBase):
    pass

class ImageUpdateSchema(BaseModel):
    filename: Optional[str] = Field(None, description="Generated filename")
    original_filename: Optional[str] = Field(None, description="Original filename")
    file_path: Optional[str] = Field(None, description="File path on server")
    file_type: Optional[str] = Field(None, description="File MIME type")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    entity_type: Optional[str] = Field(None, description="Entity type")
    entity_id: Optional[int] = Field(None, description="Entity ID")

class ImageResponseSchema(ImageBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

class ImageListSchema(BaseModel):
    images: List[ImageResponseSchema]
    total: int 