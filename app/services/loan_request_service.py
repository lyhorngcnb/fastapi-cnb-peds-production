from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.services.base import BaseService
from app.domain.loan_request import LoanRequest
from app.schemas.loan_request import LoanRequestCreateSchema, LoanRequestUpdateSchema
from app.core.exceptions import NotFoundException, ValidationException

class LoanRequestService(BaseService[LoanRequest, LoanRequestCreateSchema, LoanRequestUpdateSchema]):
    def __init__(self):
        # Initialize with a repository - for now, we'll handle this differently
        pass
    
    def create_loan_request(self, db: Session, loan_request_data: LoanRequestCreateSchema, user_id: int) -> LoanRequest:
        """Create a new loan request."""
        # This is a placeholder implementation
        raise NotImplementedError("Loan request creation not yet implemented")
    
    def get_loan_request(self, db: Session, loan_request_id: int) -> Optional[LoanRequest]:
        """Get a loan request by ID."""
        return db.query(LoanRequest).filter(LoanRequest.id == loan_request_id).first()
    
    def update_loan_request(self, db: Session, loan_request_id: int, loan_request_data: LoanRequestUpdateSchema) -> Optional[LoanRequest]:
        """Update a loan request."""
        # This is a placeholder implementation
        raise NotImplementedError("Loan request update not yet implemented")
    
    def delete_loan_request(self, db: Session, loan_request_id: int) -> bool:
        """Delete a loan request."""
        loan_request_obj = db.query(LoanRequest).filter(LoanRequest.id == loan_request_id).first()
        if not loan_request_obj:
            return False
        
        db.delete(loan_request_obj)
        db.commit()
        return True
    
    def update_status(self, db: Session, loan_request_id: int, status: str) -> Optional[LoanRequest]:
        """Update loan request status."""
        loan_request_obj = self.get(db, loan_request_id)
        if not loan_request_obj:
            return None
        
        loan_request_obj.status = status
        db.commit()
        db.refresh(loan_request_obj)
        return loan_request_obj
    
    def get_loan_requests_with_filters(
        self, 
        db: Session, 
        page: int, 
        size: int, 
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        loan_type_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get loan requests with pagination and filtering."""
        query = db.query(LoanRequest)
        
        # Apply filters
        if status:
            query = query.filter(LoanRequest.status == status)
        
        if customer_id:
            query = query.filter(LoanRequest.customer_id == customer_id)
        
        if loan_type_id:
            query = query.filter(LoanRequest.loan_type_id == loan_type_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        loan_requests = query.offset((page - 1) * size).limit(size).all()
        
        return {
            "loan_requests": loan_requests,
            "total": total,
            "page": page,
            "size": size
        } 