from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    national_id: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None
    address: Optional[str] = None

    @validator('national_id')
    def validate_national_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('National ID cannot be empty')
        return v.strip()

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and len(v.strip()) > 20:
            raise ValueError('Phone number too long')
        return v.strip() if v else None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    national_id: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('national_id')
    def validate_national_id(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('National ID cannot be empty')
        return v.strip() if v else None

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and len(v.strip()) > 20:
            raise ValueError('Phone number too long')
        return v.strip() if v else None

class CustomerInDB(CustomerBase):
    id: int
    photo_url: Optional[str] = None
    nid_front_url: Optional[str] = None
    nid_back_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    national_id: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    nid_front_url: Optional[str] = None
    nid_back_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    is_active: bool
    full_name: str

    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    customers: list[CustomerResponse]
    total: int
    page: int
    size: int

class ImageUploadResponse(BaseModel):
    file_url: str
    file_name: str
    file_size: int
    content_type: str 