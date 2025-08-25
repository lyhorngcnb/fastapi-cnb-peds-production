from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Date, Enum, ForeignKey, DECIMAL, BigInteger
from sqlalchemy.orm import relationship
from app.domain.rbac_models import Base
import enum

class OwnershipTitleEnum(enum.Enum):
    YES = "Yes"
    NO = "No"

class TypeOfTitleEnum(enum.Enum):
    HARD_TITLE_OLD = "Hard title old version"
    HARD_TITLE_NEW = "Hard title new version"
    SOFT = "Soft"
    LMAP_RECEIPT = "L-map receipt"
    SPA = "SPA"

class TypeOfPropertyEnum(enum.Enum):
    COMMERCIAL_LAND = "Commercial Land"
    RESIDENTIAL_LAND = "Residential land"
    AGRICULTURE = "Agriculture"

class MeasurementInfoEnum(enum.Enum):
    NOT_YET_ANNOUNCE = "Not yet announce measure"
    ANNOUNCE_MEASURE = "Announce measure already"
    ANNOUNCE_VERIFY = "Announce verify measure already"
    ANNOUNCE_GIVE_HT = "Announce give to HT systematice already"

class SourceTypeEnum(enum.Enum):
    BRANCH = "Branch"
    SME = "SME"
    MEGA = "Mega"
    AGENCY = "Agency"

class FileTypeEnum(enum.Enum):
    PDF = "PDF"
    IMAGE = "Image"
    OTHER = "Other"

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_code = Column(String(10), unique=True, nullable=False, index=True)  # e.g. COL0000001
    property_version = Column(Integer, default=1)
    requester_id = Column(Integer, ForeignKey("loan_requests.id"), nullable=False)
    old_property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    ownership_title = Column(Enum(OwnershipTitleEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    owner_1_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    owner_2_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    type_of_title = Column(Enum(TypeOfTitleEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    title_number = Column(String(100), nullable=True)
    type_of_property = Column(Enum(TypeOfPropertyEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    information_property = Column(Text, nullable=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    commune_id = Column(Integer, ForeignKey("communes.id"), nullable=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=True)
    measurement_info = Column(Enum(MeasurementInfoEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    requester = relationship("LoanRequest", back_populates="properties")
    old_property = relationship("Property", remote_side=[id], back_populates="new_properties")
    new_properties = relationship("Property", back_populates="old_property")
    owner_1 = relationship("Customer", foreign_keys=[owner_1_id], back_populates="owned_properties_1")
    owner_2 = relationship("Customer", foreign_keys=[owner_2_id], back_populates="owned_properties_2")
    creator = relationship("User", back_populates="properties")
    province = relationship("Province", back_populates="properties")
    district = relationship("District", back_populates="properties")
    commune = relationship("Commune", back_populates="properties")
    village = relationship("Village", back_populates="properties")
    
    # Child relationships
    land_details = relationship("LandDetail", back_populates="property_obj", cascade="all, delete-orphan")
    building_details = relationship("BuildingDetail", back_populates="property_obj", cascade="all, delete-orphan")
    google_maps = relationship("GoogleMap", back_populates="property_obj", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="property_obj", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Property {self.property_code} - {self.type_of_property.value if self.type_of_property else 'Unknown'}>"

class LandDetail(Base):
    __tablename__ = "land_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    land_size = Column(DECIMAL(18, 2), nullable=True)
    front = Column(DECIMAL(18, 2), nullable=True)
    back = Column(DECIMAL(18, 2), nullable=True)
    length = Column(DECIMAL(18, 2), nullable=True)
    width = Column(DECIMAL(18, 2), nullable=True)
    flat_unit_type = Column(String(50), nullable=True)
    number_of_lot = Column(Integer, nullable=True)

    # Relationships
    property_obj = relationship("Property", back_populates="land_details")

    def __repr__(self) -> str:
        return f"<LandDetail {self.id} - Property {self.property_id}>"

    @property
    def dimension_land(self) -> Optional[float]:
        """Calculate land dimension (width x length)."""
        if self.width and self.length:
            return float(self.width * self.length)
        return None

class BuildingDetail(Base):
    __tablename__ = "building_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    source_type = Column(Enum(SourceTypeEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    agency_name = Column(String(100), nullable=True)  # if source_type = Agency
    description = Column(String(100), nullable=True)  # e.g. Flat, Villa, Apartment
    total_building_area = Column(DECIMAL(18, 2), nullable=True)
    building_width = Column(DECIMAL(18, 2), nullable=True)
    building_length = Column(DECIMAL(18, 2), nullable=True)
    number_of_floors = Column(Integer, default=1, nullable=True)
    estimated_size = Column(DECIMAL(18, 2), nullable=True)
    remark = Column(Text, nullable=True)

    # Relationships
    property_obj = relationship("Property", back_populates="building_details")

    def __repr__(self) -> str:
        return f"<BuildingDetail {self.id} - {self.source_type.value}>"

    @property
    def dimension_building(self) -> Optional[float]:
        """Calculate building dimension (width x length)."""
        if self.building_width and self.building_length:
            return float(self.building_width * self.building_length)
        return None

class GoogleMap(Base):
    __tablename__ = "google_maps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    map_coordinates = Column(Text, nullable=True)  # geoJSON or coordinate line
    map_color = Column(String(20), nullable=True)  # based on measurement_info (green/yellow/blue/red)

    # Relationships
    property_obj = relationship("Property", back_populates="google_maps")

    def __repr__(self) -> str:
        return f"<GoogleMap {self.id} - Property {self.property_id}>"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    file_url = Column(Text, nullable=False)
    file_type = Column(Enum(FileTypeEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    title = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    property_obj = relationship("Property", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")

    def __repr__(self) -> str:
        return f"<Document {self.id} - {self.title}>" 