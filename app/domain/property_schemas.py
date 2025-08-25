from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, validator, Field
from decimal import Decimal
from enum import Enum

# Enums for schemas
class OwnershipTitleEnum(str, Enum):
    YES = "Yes"
    NO = "No"

class TypeOfTitleEnum(str, Enum):
    HARD_TITLE_OLD = "Hard title old version"
    HARD_TITLE_NEW = "Hard title new version"
    SOFT = "Soft"
    LMAP_RECEIPT = "L-map receipt"
    SPA = "SPA"

class TypeOfPropertyEnum(str, Enum):
    COMMERCIAL_LAND = "Commercial Land"
    RESIDENTIAL_LAND = "Residential land"
    AGRICULTURE = "Agriculture"

class MeasurementInfoEnum(str, Enum):
    NOT_YET_ANNOUNCE = "Not yet announce measure"
    ANNOUNCE_MEASURE = "Announce measure already"
    ANNOUNCE_VERIFY = "Announce verify measure already"
    ANNOUNCE_GIVE_HT = "Announce give to HT systematice already"

class SourceTypeEnum(str, Enum):
    BRANCH = "Branch"
    SME = "SME"
    MEGA = "Mega"
    AGENCY = "Agency"

class FileTypeEnum(str, Enum):
    PDF = "PDF"
    IMAGE = "Image"
    OTHER = "Other"

# Base schemas
class LandDetailBase(BaseModel):
    land_size: Optional[Decimal] = Field(None, ge=0)
    front: Optional[Decimal] = Field(None, ge=0)
    back: Optional[Decimal] = Field(None, ge=0)
    length: Optional[Decimal] = Field(None, ge=0)
    width: Optional[Decimal] = Field(None, ge=0)
    flat_unit_type: Optional[str] = None
    number_of_lot: Optional[int] = Field(None, ge=0)

class BuildingDetailBase(BaseModel):
    source_type: SourceTypeEnum
    agency_name: Optional[str] = None
    description: Optional[str] = None
    total_building_area: Optional[Decimal] = Field(None, ge=0)
    building_width: Optional[Decimal] = Field(None, ge=0)
    building_length: Optional[Decimal] = Field(None, ge=0)
    number_of_floors: Optional[int] = Field(None, ge=1)
    estimated_size: Optional[Decimal] = Field(None, ge=0)
    remark: Optional[str] = None

class GoogleMapBase(BaseModel):
    map_coordinates: Optional[str] = None
    map_color: Optional[str] = None

class DocumentBase(BaseModel):
    file_url: str
    file_type: FileTypeEnum
    title: Optional[str] = None

class PropertyBase(BaseModel):
    requester_id: int
    old_property_id: Optional[int] = None
    ownership_title: OwnershipTitleEnum
    owner_1_id: int
    owner_2_id: Optional[int] = None
    type_of_title: Optional[TypeOfTitleEnum] = None
    title_number: Optional[str] = None
    type_of_property: Optional[TypeOfPropertyEnum] = None
    information_property: Optional[str] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    commune_id: Optional[int] = None
    village_id: Optional[int] = None
    measurement_info: Optional[MeasurementInfoEnum] = None
    remark: Optional[str] = None

    @validator('title_number')
    def validate_title_number(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Title number cannot be empty if provided')
        return v.strip() if v else None

# Create schemas
class LandDetailCreate(LandDetailBase):
    pass

class BuildingDetailCreate(BuildingDetailBase):
    pass

class GoogleMapCreate(GoogleMapBase):
    pass

class DocumentCreate(DocumentBase):
    pass

class PropertyCreate(PropertyBase):
    land_details: Optional[List[LandDetailCreate]] = []
    building_details: Optional[List[BuildingDetailCreate]] = []
    google_maps: Optional[List[GoogleMapCreate]] = []
    documents: Optional[List[DocumentCreate]] = []

# Update schemas
class LandDetailUpdate(BaseModel):
    land_size: Optional[Decimal] = Field(None, ge=0)
    front: Optional[Decimal] = Field(None, ge=0)
    back: Optional[Decimal] = Field(None, ge=0)
    length: Optional[Decimal] = Field(None, ge=0)
    width: Optional[Decimal] = Field(None, ge=0)
    flat_unit_type: Optional[str] = None
    number_of_lot: Optional[int] = Field(None, ge=0)

class BuildingDetailUpdate(BaseModel):
    source_type: Optional[SourceTypeEnum] = None
    agency_name: Optional[str] = None
    description: Optional[str] = None
    total_building_area: Optional[Decimal] = Field(None, ge=0)
    building_width: Optional[Decimal] = Field(None, ge=0)
    building_length: Optional[Decimal] = Field(None, ge=0)
    number_of_floors: Optional[int] = Field(None, ge=1)
    estimated_size: Optional[Decimal] = Field(None, ge=0)
    remark: Optional[str] = None

class GoogleMapUpdate(BaseModel):
    map_coordinates: Optional[str] = None
    map_color: Optional[str] = None

class DocumentUpdate(BaseModel):
    file_url: Optional[str] = None
    file_type: Optional[FileTypeEnum] = None
    title: Optional[str] = None

class PropertyUpdate(BaseModel):
    old_property_id: Optional[int] = None
    ownership_title: Optional[OwnershipTitleEnum] = None
    owner_1_id: Optional[int] = None
    owner_2_id: Optional[int] = None
    type_of_title: Optional[TypeOfTitleEnum] = None
    title_number: Optional[str] = None
    type_of_property: Optional[TypeOfPropertyEnum] = None
    information_property: Optional[str] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    commune_id: Optional[int] = None
    village_id: Optional[int] = None
    measurement_info: Optional[MeasurementInfoEnum] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = None

# Response schemas
class LandDetailResponse(LandDetailBase):
    id: int
    property_id: int
    dimension_land: Optional[float] = None

    class Config:
        from_attributes = True

class BuildingDetailResponse(BuildingDetailBase):
    id: int
    property_id: int
    dimension_building: Optional[float] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Convert enum objects to strings for response
        if hasattr(obj, 'source_type') and obj.source_type:
            obj.source_type = obj.source_type.value
        return super().from_orm(obj)

class GoogleMapResponse(GoogleMapBase):
    id: int
    property_id: int

    class Config:
        from_attributes = True

class DocumentResponse(DocumentBase):
    id: int
    property_id: int
    uploaded_at: datetime
    uploaded_by: Optional[int] = None

    class Config:
        from_attributes = True

class LocationInfo(BaseModel):
    id: int
    code: str
    name: str
    name_kh: Optional[str] = None

    class Config:
        from_attributes = True

class CustomerInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    national_id: str
    full_name: str

    class Config:
        from_attributes = True

class LoanRequestInfo(BaseModel):
    id: int
    branch: dict
    loan_type: dict
    request_type: dict
    request_limit_usd: float
    request_limit_khr: float

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Convert relationship objects to dictionaries
        if hasattr(obj, 'branch') and obj.branch:
            obj.branch = {
                'id': obj.branch.id,
                'code': obj.branch.code,
                'name': obj.branch.name
            }
        if hasattr(obj, 'loan_type') and obj.loan_type:
            obj.loan_type = {
                'id': obj.loan_type.id,
                'code': obj.loan_type.code,
                'name': obj.loan_type.name
            }
        if hasattr(obj, 'request_type') and obj.request_type:
            obj.request_type = {
                'id': obj.request_type.id,
                'code': obj.request_type.code,
                'name': obj.request_type.name
            }
        return super().from_orm(obj)

class PropertyResponse(PropertyBase):
    id: int
    property_code: str
    property_version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    # Relationships
    requester: LoanRequestInfo
    owner_1: CustomerInfo
    owner_2: Optional[CustomerInfo] = None
    province: Optional[LocationInfo] = None
    district: Optional[LocationInfo] = None
    commune: Optional[LocationInfo] = None
    village: Optional[LocationInfo] = None
    
    # Child relationships
    land_details: List[LandDetailResponse] = []
    building_details: List[BuildingDetailResponse] = []
    google_maps: List[GoogleMapResponse] = []
    documents: List[DocumentResponse] = []

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Convert enum objects to strings for response
        if hasattr(obj, 'ownership_title') and obj.ownership_title:
            obj.ownership_title = obj.ownership_title.value
        if hasattr(obj, 'type_of_property') and obj.type_of_property:
            obj.type_of_property = obj.type_of_property.value
        if hasattr(obj, 'type_of_title') and obj.type_of_title:
            obj.type_of_title = obj.type_of_title.value
        if hasattr(obj, 'measurement_info') and obj.measurement_info:
            obj.measurement_info = obj.measurement_info.value
            
        # Convert building details enums
        for building in obj.building_details:
            if building.source_type:
                building.source_type = building.source_type.value
                
        return super().from_orm(obj)

class PropertyListResponse(BaseModel):
    properties: List[PropertyResponse]
    total: int
    page: int
    size: int

# Location schemas
class ProvinceBase(BaseModel):
    code: str
    name: str
    name_kh: Optional[str] = None
    description: Optional[str] = None

class ProvinceCreate(ProvinceBase):
    pass

class ProvinceUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    name_kh: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ProvinceResponse(ProvinceBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DistrictBase(BaseModel):
    province_id: int
    code: str
    name: str
    name_kh: Optional[str] = None
    description: Optional[str] = None

class DistrictCreate(DistrictBase):
    pass

class DistrictUpdate(BaseModel):
    province_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    name_kh: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DistrictResponse(DistrictBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    province: ProvinceResponse

    class Config:
        from_attributes = True

class CommuneBase(BaseModel):
    district_id: int
    code: str
    name: str
    name_kh: Optional[str] = None
    description: Optional[str] = None

class CommuneCreate(CommuneBase):
    pass

class CommuneUpdate(BaseModel):
    district_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    name_kh: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CommuneResponse(CommuneBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    district: DistrictResponse

    class Config:
        from_attributes = True

class VillageBase(BaseModel):
    commune_id: int
    code: str
    name: str
    name_kh: Optional[str] = None
    description: Optional[str] = None

class VillageCreate(VillageBase):
    pass

class VillageUpdate(BaseModel):
    commune_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    name_kh: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class VillageResponse(VillageBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    commune: CommuneResponse

    class Config:
        from_attributes = True

# Agency schemas
class AgencyBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class AgencyCreate(AgencyBase):
    pass

class AgencyUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class AgencyResponse(AgencyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 