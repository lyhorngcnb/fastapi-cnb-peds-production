from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.schemas.base import BaseSchema, BaseResponseSchema

class PropertyCreateSchema(BaseModel):
    """Property creation request schema."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Property title")
    description: Optional[str] = Field(None, max_length=1000, description="Property description")
    property_type: str = Field(..., description="Type of property (house, apartment, land, etc.)")
    address: str = Field(..., min_length=1, max_length=500, description="Property address")
    province_id: int = Field(..., description="Province ID")
    district_id: int = Field(..., description="District ID")
    commune_id: Optional[int] = Field(None, description="Commune ID")
    village_id: Optional[int] = Field(None, description="Village ID")
    area: Decimal = Field(..., gt=0, description="Property area in square meters")
    price: Optional[Decimal] = Field(None, gt=0, description="Property price")
    currency: str = Field(default="USD", description="Price currency")
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms")
    floors: Optional[int] = Field(None, ge=0, description="Number of floors")
    year_built: Optional[int] = Field(None, ge=1800, le=datetime.now().year, description="Year built")
    condition: Optional[str] = Field(None, description="Property condition (new, good, needs_repair, etc.)")

class PropertyUpdateSchema(BaseModel):
    """Property update request schema."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    property_type: Optional[str] = None
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    commune_id: Optional[int] = None
    village_id: Optional[int] = None
    area: Optional[Decimal] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = None
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    floors: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=datetime.now().year)
    condition: Optional[str] = None

class PropertyResponseSchema(BaseResponseSchema):
    """Property response schema."""
    
    title: str
    description: Optional[str] = None
    property_type: str
    address: str
    province_id: int
    district_id: int
    commune_id: Optional[int] = None
    village_id: Optional[int] = None
    area: Decimal
    price: Optional[Decimal] = None
    currency: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floors: Optional[int] = None
    year_built: Optional[int] = None
    condition: Optional[str] = None
    owner_id: Optional[int] = None
    status: str = "active"

class PropertyListSchema(BaseSchema):
    """Property list response schema."""
    
    properties: List[PropertyResponseSchema]
    total: int
    page: int
    size: int

class PropertySearchSchema(BaseModel):
    """Property search parameters."""
    
    search: Optional[str] = Field(None, description="Search in title, description, or address")
    property_type: Optional[str] = Field(None, description="Filter by property type")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    min_area: Optional[Decimal] = Field(None, ge=0, description="Minimum area")
    max_area: Optional[Decimal] = Field(None, ge=0, description="Maximum area")
    bedrooms: Optional[int] = Field(None, ge=0, description="Minimum number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Minimum number of bathrooms")
    province_id: Optional[int] = Field(None, description="Filter by province")
    district_id: Optional[int] = Field(None, description="Filter by district")
    condition: Optional[str] = Field(None, description="Filter by condition") 