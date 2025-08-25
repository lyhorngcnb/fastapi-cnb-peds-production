from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.rbac_models import Base

class Province(Base):
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_kh = Column(String(100), nullable=True)  # Khmer name
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    districts = relationship("District", back_populates="province", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="province")

    def __repr__(self) -> str:
        return f"<Province {self.code} - {self.name}>"

class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_kh = Column(String(100), nullable=True)  # Khmer name
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    province = relationship("Province", back_populates="districts")
    communes = relationship("Commune", back_populates="district", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="district")

    def __repr__(self) -> str:
        return f"<District {self.code} - {self.name}>"

class Commune(Base):
    __tablename__ = "communes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_kh = Column(String(100), nullable=True)  # Khmer name
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    district = relationship("District", back_populates="communes")
    villages = relationship("Village", back_populates="commune", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="commune")

    def __repr__(self) -> str:
        return f"<Commune {self.code} - {self.name}>"

class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    commune_id = Column(Integer, ForeignKey("communes.id"), nullable=False)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_kh = Column(String(100), nullable=True)  # Khmer name
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    commune = relationship("Commune", back_populates="villages")
    properties = relationship("Property", back_populates="village")

    def __repr__(self) -> str:
        return f"<Village {self.code} - {self.name}>"

class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Agency {self.code} - {self.name}>" 