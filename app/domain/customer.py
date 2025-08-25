from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.rbac_models import Base
import enum

class GenderEnum(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    national_id = Column(String(30), unique=True, nullable=False, index=True)
    
    # Optional but recommended
    gender = Column(Enum(GenderEnum), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Contact Information
    phone_number = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    address = Column(Text, nullable=True)
    
    # Identification
    photo_url = Column(Text, nullable=True)  # Path to profile image stored in MinIO
    nid_front_url = Column(Text, nullable=True)  # Upload path for NID front
    nid_back_url = Column(Text, nullable=True)   # Upload path for NID back
    
    # System Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    creator = relationship("User", back_populates="customers")
    loan_requests = relationship("LoanRequest", back_populates="customer")
    owned_properties_1 = relationship("Property", foreign_keys="Property.owner_1_id", back_populates="owner_1")
    owned_properties_2 = relationship("Property", foreign_keys="Property.owner_2_id", back_populates="owner_2")
    
    def __repr__(self) -> str:
        return f"<Customer {self.first_name} {self.last_name} - {self.national_id}>"
    
    @property
    def full_name(self) -> str:
        """Get the customer's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def gender_value(self) -> Optional[str]:
        """Get the gender as a string value."""
        return self.gender.value if self.gender else None 