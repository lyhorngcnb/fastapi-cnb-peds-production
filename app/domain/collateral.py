from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.domain.rbac_models import Base

class Collateral(Base):
    __tablename__ = "collaterals"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_request_id = Column(Integer, ForeignKey("loan_requests.id"), nullable=False)
    collateral_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    estimated_value = Column(Numeric(15, 2), nullable=False)
    location = Column(String(255), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    loan_request = relationship("LoanRequest", back_populates="collaterals")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<Collateral(id={self.id}, type={self.collateral_type}, value={self.estimated_value})>" 