from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from app.domain.rbac_models import Base

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # e.g., "OLP", "MRO"
    name = Column(String(100), nullable=False)  # e.g., "Olympic Branch", "Mao Tse Toung Branch"
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    loan_requests = relationship("LoanRequest", back_populates="branch")

    def __repr__(self) -> str:
        return f"<Branch {self.code} - {self.name}>"

class LoanType(Base):
    __tablename__ = "loan_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "SME_LOAN", "HOME_LOAN"
    name = Column(String(100), nullable=False)  # e.g., "SME Loan", "Home Loan"
    description = Column(Text, nullable=True)
    min_amount_usd = Column(Integer, nullable=True)  # Minimum amount in USD
    max_amount_usd = Column(Integer, nullable=True)  # Maximum amount in USD
    min_amount_khr = Column(Integer, nullable=True)  # Minimum amount in KHR
    max_amount_khr = Column(Integer, nullable=True)  # Maximum amount in KHR
    interest_rate_min = Column(Integer, nullable=True)  # Minimum interest rate (percentage)
    interest_rate_max = Column(Integer, nullable=True)  # Maximum interest rate (percentage)
    term_min_months = Column(Integer, nullable=True)  # Minimum term in months
    term_max_months = Column(Integer, nullable=True)  # Maximum term in months
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    loan_requests = relationship("LoanRequest", back_populates="loan_type")

    def __repr__(self) -> str:
        return f"<LoanType {self.code} - {self.name}>"

class RequestType(Base):
    __tablename__ = "request_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "NEW", "RENEW", "EXTEND"
    name = Column(String(100), nullable=False)  # e.g., "New", "Renew", "Extend"
    description = Column(Text, nullable=True)
    requires_collateral = Column(Boolean, default=False, nullable=False)
    requires_guarantor = Column(Boolean, default=False, nullable=False)
    requires_insurance = Column(Boolean, default=False, nullable=False)
    approval_level = Column(Integer, default=1, nullable=False)  # 1=Basic, 2=Manager, 3=Director, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    loan_requests = relationship("LoanRequest", back_populates="request_type")

    def __repr__(self) -> str:
        return f"<RequestType {self.code} - {self.name}>" 