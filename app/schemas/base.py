from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class BaseResponseSchema(BaseSchema):
    """Base response schema with common fields."""
    
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PaginationSchema(BaseSchema):
    """Pagination parameters for list endpoints."""
    
    page: int = 1
    size: int = 20
    total: Optional[int] = None

class PaginatedResponseSchema(BaseSchema):
    """Paginated response wrapper."""
    
    items: list[Any]
    pagination: PaginationSchema

class MessageResponseSchema(BaseSchema):
    """Standard message response."""
    
    message: str
    success: bool = True 