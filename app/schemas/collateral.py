from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

from app.schemas.base import BaseSchema

class CollateralBase(BaseModel):
    loan_request_id: int = Field(..., description="Loan request ID")
    collateral_type: str = Field(..., description="Type of collateral")
    description: str = Field(..., description="Collateral description")
    estimated_value: Decimal = Field(..., description="Estimated value of collateral")
    location: Optional[str] = Field(None, description="Collateral location")
    status: str = Field(default="active", description="Collateral status")

class CollateralCreateSchema(CollateralBase):
    pass

class CollateralUpdateSchema(BaseModel):
    loan_request_id: Optional[int] = Field(None, description="Loan request ID")
    collateral_type: Optional[str] = Field(None, description="Type of collateral")
    description: Optional[str] = Field(None, description="Collateral description")
    estimated_value: Optional[Decimal] = Field(None, description="Estimated value of collateral")
    location: Optional[str] = Field(None, description="Collateral location")
    status: Optional[str] = Field(None, description="Collateral status")

class CollateralResponseSchema(CollateralBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

class CollateralListSchema(BaseModel):
    collaterals: List[CollateralResponseSchema]
    total: int
    page: int
    size: int 