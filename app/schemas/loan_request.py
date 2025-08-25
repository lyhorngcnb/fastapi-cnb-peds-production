from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

from app.schemas.base import BaseSchema

class LoanRequestBase(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    loan_type_id: int = Field(..., description="Loan type ID")
    request_type_id: int = Field(..., description="Request type ID")
    amount: Decimal = Field(..., description="Loan amount")
    term_months: int = Field(..., description="Loan term in months")
    purpose: str = Field(..., description="Loan purpose")
    status: str = Field(default="pending", description="Loan request status")
    notes: Optional[str] = Field(None, description="Additional notes")

class LoanRequestCreateSchema(LoanRequestBase):
    pass

class LoanRequestUpdateSchema(BaseModel):
    customer_id: Optional[int] = Field(None, description="Customer ID")
    loan_type_id: Optional[int] = Field(None, description="Loan type ID")
    request_type_id: Optional[int] = Field(None, description="Request type ID")
    amount: Optional[Decimal] = Field(None, description="Loan amount")
    term_months: Optional[int] = Field(None, description="Loan term in months")
    purpose: Optional[str] = Field(None, description="Loan purpose")
    status: Optional[str] = Field(None, description="Loan request status")
    notes: Optional[str] = Field(None, description="Additional notes")

class LoanRequestResponseSchema(LoanRequestBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

class LoanRequestListSchema(BaseModel):
    loan_requests: List[LoanRequestResponseSchema]
    total: int
    page: int
    size: int 