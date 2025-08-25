from datetime import datetime, date
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.domain.rbac_models import Base

class LoanRequest(Base):
    __tablename__ = "loan_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Branch (FK to branches table)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # Submitted Date
    submitted_date = Column(Date, nullable=False)
    
    # Customer (FK to customer table)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Type of Loan (FK to loan_types table)
    loan_type_id = Column(Integer, ForeignKey("loan_types.id"), nullable=False)
    
    # Request Type (FK to request_types table)
    request_type_id = Column(Integer, ForeignKey("request_types.id"), nullable=False)
    
    # Request Limits
    request_limit_usd = Column(DECIMAL(18, 2), default=0)
    request_limit_khr = Column(DECIMAL(18, 2), default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    branch = relationship("Branch", back_populates="loan_requests")
    customer = relationship("Customer", back_populates="loan_requests")
    loan_type = relationship("LoanType", back_populates="loan_requests")
    request_type = relationship("RequestType", back_populates="loan_requests")
    creator = relationship("User", back_populates="loan_requests")
    properties = relationship("Property", back_populates="requester")
    
    def __repr__(self) -> str:
        return f"<LoanRequest {self.id} - {self.customer_id} - {self.loan_type.name if self.loan_type else 'Unknown'}>"
    
    @property
    def total_limit_usd(self) -> float:
        """Get total limit in USD."""
        return float(self.request_limit_usd) if self.request_limit_usd else 0.0
    
    @property
    def total_limit_khr(self) -> float:
        """Get total limit in KHR."""
        return float(self.request_limit_khr) if self.request_limit_khr else 0.0 