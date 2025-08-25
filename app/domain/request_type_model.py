from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class RequestTypeBase(BaseModel):
    """Base schema for RequestType data."""
    code: str = Field(..., min_length=1, max_length=20, description="Unique request type code")
    name: str = Field(..., min_length=1, max_length=100, description="Request type name")
    description: Optional[str] = Field(None, description="Request type description")
    requires_collateral: bool = Field(False, description="Whether this request type requires collateral")
    requires_guarantor: bool = Field(False, description="Whether this request type requires guarantor")
    requires_insurance: bool = Field(False, description="Whether this request type requires insurance")
    approval_level: int = Field(1, ge=1, le=5, description="Approval level required (1=Basic, 2=Manager, 3=Director, etc.)")
    is_active: bool = Field(True, description="Whether the request type is active")

    @validator('code')
    def validate_code(cls, v):
        """Validate request type code format."""
        if not v.replace('_', '').isalnum():
            raise ValueError('Request type code must contain only alphanumeric characters and underscores')
        return v.upper()

class RequestTypeCreate(RequestTypeBase):
    """Schema for creating a new request type."""
    pass

class RequestTypeUpdate(BaseModel):
    """Schema for updating a request type."""
    code: Optional[str] = Field(None, min_length=1, max_length=20, description="Unique request type code")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Request type name")
    description: Optional[str] = Field(None, description="Request type description")
    requires_collateral: Optional[bool] = Field(None, description="Whether this request type requires collateral")
    requires_guarantor: Optional[bool] = Field(None, description="Whether this request type requires guarantor")
    requires_insurance: Optional[bool] = Field(None, description="Whether this request type requires insurance")
    approval_level: Optional[int] = Field(None, ge=1, le=5, description="Approval level required (1=Basic, 2=Manager, 3=Director, etc.)")
    is_active: Optional[bool] = Field(None, description="Whether the request type is active")

    @validator('code')
    def validate_code(cls, v):
        """Validate request type code format."""
        if v and not v.replace('_', '').isalnum():
            raise ValueError('Request type code must contain only alphanumeric characters and underscores')
        return v.upper() if v else v

class RequestTypeResponse(RequestTypeBase):
    """Schema for request type response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RequestTypeListResponse(BaseModel):
    """Schema for request type list response with pagination."""
    items: list[RequestTypeResponse]
    total: int
    page: int
    size: int
    pages: int 