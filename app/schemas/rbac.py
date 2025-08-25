from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema

# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    is_active: bool = Field(default=True, description="Role active status")

class RoleCreateSchema(RoleBase):
    pass

class RoleUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    is_active: Optional[bool] = Field(None, description="Role active status")

class RoleResponseSchema(RoleBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

# Permission schemas
class PermissionBase(BaseModel):
    name: str = Field(..., description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")
    is_active: bool = Field(default=True, description="Permission active status")

class PermissionCreateSchema(PermissionBase):
    pass

class PermissionUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    resource: Optional[str] = Field(None, description="Resource name")
    action: Optional[str] = Field(None, description="Action name")
    is_active: Optional[bool] = Field(None, description="Permission active status")

class PermissionResponseSchema(PermissionBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

# User Role schemas
class UserRoleBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    role_id: int = Field(..., description="Role ID")
    is_active: bool = Field(default=True, description="User role active status")

class UserRoleCreateSchema(UserRoleBase):
    pass

class UserRoleUpdateSchema(BaseModel):
    user_id: Optional[int] = Field(None, description="User ID")
    role_id: Optional[int] = Field(None, description="Role ID")
    is_active: Optional[bool] = Field(None, description="User role active status")

class UserRoleResponseSchema(UserRoleBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int 