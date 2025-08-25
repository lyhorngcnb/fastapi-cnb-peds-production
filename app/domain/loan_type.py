from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class LoanTypeBase(BaseModel):
    """Base schema for LoanType data."""
    code: str = Field(..., min_length=1, max_length=20, description="Unique loan type code")
    name: str = Field(..., min_length=1, max_length=100, description="Loan type name")
    description: Optional[str] = Field(None, description="Loan type description")
    min_amount_usd: Optional[int] = Field(None, ge=0, description="Minimum amount in USD")
    max_amount_usd: Optional[int] = Field(None, ge=0, description="Maximum amount in USD")
    min_amount_khr: Optional[int] = Field(None, ge=0, description="Minimum amount in KHR")
    max_amount_khr: Optional[int] = Field(None, ge=0, description="Maximum amount in KHR")
    interest_rate_min: Optional[int] = Field(None, ge=0, le=100, description="Minimum interest rate (percentage)")
    interest_rate_max: Optional[int] = Field(None, ge=0, le=100, description="Maximum interest rate (percentage)")
    term_min_months: Optional[int] = Field(None, ge=1, description="Minimum term in months")
    term_max_months: Optional[int] = Field(None, ge=1, description="Maximum term in months")
    is_active: bool = Field(True, description="Whether the loan type is active")

    @validator('code')
    def validate_code(cls, v):
        """Validate loan type code format."""
        if not v.replace('_', '').isalnum():
            raise ValueError('Loan type code must contain only alphanumeric characters and underscores')
        return v.upper()

    @validator('max_amount_usd')
    def validate_max_amount_usd(cls, v, values):
        """Validate max amount is greater than min amount."""
        if v and 'min_amount_usd' in values and values['min_amount_usd']:
            if v <= values['min_amount_usd']:
                raise ValueError('Maximum USD amount must be greater than minimum USD amount')
        return v

    @validator('max_amount_khr')
    def validate_max_amount_khr(cls, v, values):
        """Validate max amount is greater than min amount."""
        if v and 'min_amount_khr' in values and values['min_amount_khr']:
            if v <= values['min_amount_khr']:
                raise ValueError('Maximum KHR amount must be greater than minimum KHR amount')
        return v

    @validator('interest_rate_max')
    def validate_interest_rate_max(cls, v, values):
        """Validate max interest rate is greater than min interest rate."""
        if v and 'interest_rate_min' in values and values['interest_rate_min']:
            if v <= values['interest_rate_min']:
                raise ValueError('Maximum interest rate must be greater than minimum interest rate')
        return v

    @validator('term_max_months')
    def validate_term_max_months(cls, v, values):
        """Validate max term is greater than min term."""
        if v and 'term_min_months' in values and values['term_min_months']:
            if v <= values['term_min_months']:
                raise ValueError('Maximum term must be greater than minimum term')
        return v

class LoanTypeCreate(LoanTypeBase):
    """Schema for creating a new loan type."""
    pass

class LoanTypeUpdate(BaseModel):
    """Schema for updating a loan type."""
    code: Optional[str] = Field(None, min_length=1, max_length=20, description="Unique loan type code")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Loan type name")
    description: Optional[str] = Field(None, description="Loan type description")
    min_amount_usd: Optional[int] = Field(None, ge=0, description="Minimum amount in USD")
    max_amount_usd: Optional[int] = Field(None, ge=0, description="Maximum amount in USD")
    min_amount_khr: Optional[int] = Field(None, ge=0, description="Minimum amount in KHR")
    max_amount_khr: Optional[int] = Field(None, ge=0, description="Maximum amount in KHR")
    interest_rate_min: Optional[int] = Field(None, ge=0, le=100, description="Minimum interest rate (percentage)")
    interest_rate_max: Optional[int] = Field(None, ge=0, le=100, description="Maximum interest rate (percentage)")
    term_min_months: Optional[int] = Field(None, ge=1, description="Minimum term in months")
    term_max_months: Optional[int] = Field(None, ge=1, description="Maximum term in months")
    is_active: Optional[bool] = Field(None, description="Whether the loan type is active")

    @validator('code')
    def validate_code(cls, v):
        """Validate loan type code format."""
        if v and not v.replace('_', '').isalnum():
            raise ValueError('Loan type code must contain only alphanumeric characters and underscores')
        return v.upper() if v else v

class LoanTypeResponse(LoanTypeBase):
    """Schema for loan type response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoanTypeListResponse(BaseModel):
    """Schema for loan type list response with pagination."""
    items: list[LoanTypeResponse]
    total: int
    page: int
    size: int
    pages: int 