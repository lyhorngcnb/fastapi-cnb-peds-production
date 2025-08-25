from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.base import BaseSchema

class UserLoginSchema(BaseModel):
    """User login request schema."""
    
    email: EmailStr
    password: str

class UserRegisterSchema(BaseModel):
    """User registration request schema."""
    
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class TokenSchema(BaseSchema):
    """JWT token response schema."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponseSchema(BaseSchema):
    """User response schema."""
    
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None

class PasswordChangeSchema(BaseModel):
    """Password change request schema."""
    
    current_password: str
    new_password: str 