from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class BranchBase(BaseModel):
    """Base schema for Branch data."""
    code: str = Field(..., min_length=1, max_length=10, description="Unique branch code")
    name: str = Field(..., min_length=1, max_length=100, description="Branch name")
    description: Optional[str] = Field(None, description="Branch description")
    address: Optional[str] = Field(None, description="Branch address")
    phone: Optional[str] = Field(None, max_length=20, description="Branch phone number")
    email: Optional[str] = Field(None, max_length=150, description="Branch email")
    is_active: bool = Field(True, description="Whether the branch is active")

    @validator('code')
    def validate_code(cls, v):
        """Validate branch code format."""
        if not v.isalnum():
            raise ValueError('Branch code must contain only alphanumeric characters')
        return v.upper()

    @validator('email')
    def validate_email(cls, v):
        """Validate email format if provided."""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class BranchCreate(BranchBase):
    """Schema for creating a new branch."""
    pass

class BranchUpdate(BaseModel):
    """Schema for updating a branch."""
    code: Optional[str] = Field(None, min_length=1, max_length=10, description="Unique branch code")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Branch name")
    description: Optional[str] = Field(None, description="Branch description")
    address: Optional[str] = Field(None, description="Branch address")
    phone: Optional[str] = Field(None, max_length=20, description="Branch phone number")
    email: Optional[str] = Field(None, max_length=150, description="Branch email")
    is_active: Optional[bool] = Field(None, description="Whether the branch is active")

    @validator('code')
    def validate_code(cls, v):
        """Validate branch code format."""
        if v and not v.isalnum():
            raise ValueError('Branch code must contain only alphanumeric characters')
        return v.upper() if v else v

    @validator('email')
    def validate_email(cls, v):
        """Validate email format if provided."""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class BranchResponse(BranchBase):
    """Schema for branch response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BranchListResponse(BaseModel):
    """Schema for branch list response with pagination."""
    items: list[BranchResponse]
    total: int
    page: int
    size: int
    pages: int 