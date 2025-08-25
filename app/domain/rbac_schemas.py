from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# Base schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=150)
    department: Optional[str] = Field(None, max_length=100)

class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None

class PermissionBase(BaseModel):
    action: str = Field(..., min_length=2, max_length=50)
    resource: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None

# Create schemas
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_names: Optional[List[str]] = Field(default_factory=list)

class RoleCreate(RoleBase):
    permission_names: Optional[List[str]] = Field(default_factory=list)

class PermissionCreate(PermissionBase):
    pass

class UserRoleAssign(BaseModel):
    user_id: int
    role_id: int
    assigned_by: Optional[int] = None

class RolePermissionAssign(BaseModel):
    role_id: int
    permission_id: int

# Response schemas
class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    is_active: bool
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True

class UserRoleResponse(BaseModel):
    user_id: int
    role_id: int
    assigned_by: Optional[int]
    assigned_at: datetime
    role: RoleResponse

    class Config:
        from_attributes = True

# Update schemas
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=150)
    department: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None

class PermissionUpdate(BaseModel):
    action: Optional[str] = Field(None, min_length=2, max_length=50)
    resource: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None

# Authentication schemas
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# Permission check schemas
class PermissionCheck(BaseModel):
    action: str
    resource: str

class PermissionCheckResponse(BaseModel):
    has_permission: bool
    user_roles: List[str]
    required_permission: str 