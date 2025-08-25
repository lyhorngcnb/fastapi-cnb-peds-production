from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, validator, Field
from decimal import Decimal

class LoanRequestBase(BaseModel):
    branch_id: int
    submitted_date: date
    customer_id: int
    loan_type_id: int
    request_type_id: int
    request_limit_usd: Optional[Decimal] = Field(default=0, ge=0)
    request_limit_khr: Optional[Decimal] = Field(default=0, ge=0)

    @validator('submitted_date')
    def validate_submitted_date(cls, v):
        if v > date.today():
            raise ValueError('Submitted date cannot be in the future')
        return v

    @validator('request_limit_usd', 'request_limit_khr')
    def validate_limits(cls, v):
        if v is not None and v < 0:
            raise ValueError('Request limits cannot be negative')
        return v

class LoanRequestCreate(LoanRequestBase):
    pass

class LoanRequestUpdate(BaseModel):
    branch_id: Optional[int] = None
    submitted_date: Optional[date] = None
    customer_id: Optional[int] = None
    loan_type_id: Optional[int] = None
    request_type_id: Optional[int] = None
    request_limit_usd: Optional[Decimal] = Field(None, ge=0)
    request_limit_khr: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @validator('submitted_date')
    def validate_submitted_date(cls, v):
        if v and v > date.today():
            raise ValueError('Submitted date cannot be in the future')
        return v

    @validator('request_limit_usd', 'request_limit_khr')
    def validate_limits(cls, v):
        if v is not None and v < 0:
            raise ValueError('Request limits cannot be negative')
        return v

class CustomerInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    national_id: str
    full_name: str

    class Config:
        from_attributes = True

class BranchInfo(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class LoanTypeInfo(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RequestTypeInfo(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class LoanRequestInDB(LoanRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

class LoanRequestResponse(LoanRequestInDB):
    customer: CustomerInfo
    branch: BranchInfo
    loan_type: LoanTypeInfo
    request_type: RequestTypeInfo
    total_limit_usd: float
    total_limit_khr: float

    class Config:
        from_attributes = True

class LoanRequestListResponse(BaseModel):
    loan_requests: list[LoanRequestResponse]
    total: int
    page: int
    size: int

class LoanRequestSummary(BaseModel):
    id: int
    branch_name: str
    submitted_date: date
    customer_name: str
    loan_type: str
    request_type: str
    request_limit_usd: float
    request_limit_khr: float
    created_at: datetime

    class Config:
        from_attributes = True

class LoanRequestSummaryList(BaseModel):
    loan_requests: list[LoanRequestSummary]
    total: int
    page: int
    size: int 