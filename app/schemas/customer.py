from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from app.schemas.base import BaseSchema, BaseResponseSchema

class CustomerCreateSchema(BaseModel):
    """Customer creation request schema."""
    
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: str
    date_of_birth: Optional[date] = None
    national_id: Optional[str] = None
    address: Optional[str] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    commune_id: Optional[int] = None
    village_id: Optional[int] = None

class CustomerUpdateSchema(BaseModel):
    """Customer update request schema."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    national_id: Optional[str] = None
    address: Optional[str] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    commune_id: Optional[int] = None
    village_id: Optional[int] = None

class CustomerResponseSchema(BaseResponseSchema):
    """Customer response schema."""
    
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: str
    date_of_birth: Optional[str] = None
    national_id: Optional[str] = None
    address: Optional[str] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    commune_id: Optional[int] = None
    village_id: Optional[int] = None
    full_name: Optional[str] = None

class CustomerListSchema(BaseSchema):
    """Customer list response schema."""
    
    customers: List[CustomerResponseSchema]
    total: int
    page: int
    size: int 