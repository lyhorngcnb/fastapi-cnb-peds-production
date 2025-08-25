from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException
from app.domain.loan_request import LoanRequest
from app.domain.customer import Customer
from app.domain.reference_models import Branch, LoanType, RequestType
from app.domain.loan_request_schemas import LoanRequestCreate, LoanRequestUpdate, LoanRequestResponse
import logging

logger = logging.getLogger(__name__)

class LoanRequestService:
    
    @staticmethod
    def create_loan_request(db: Session, loan_request_data: LoanRequestCreate, created_by: int) -> LoanRequest:
        """Create a new loan request."""
        try:
            # Check if customer exists
            customer = db.query(Customer).filter(Customer.id == loan_request_data.customer_id).first()
            if not customer:
                raise HTTPException(
                    status_code=404,
                    detail=f"Customer with ID {loan_request_data.customer_id} not found"
                )
            
            # Check if branch exists
            branch = db.query(Branch).filter(Branch.id == loan_request_data.branch_id).first()
            if not branch:
                raise HTTPException(
                    status_code=404,
                    detail=f"Branch with ID {loan_request_data.branch_id} not found"
                )
            
            # Check if loan type exists
            loan_type = db.query(LoanType).filter(LoanType.id == loan_request_data.loan_type_id).first()
            if not loan_type:
                raise HTTPException(
                    status_code=404,
                    detail=f"Loan type with ID {loan_request_data.loan_type_id} not found"
                )
            
            # Check if request type exists
            request_type = db.query(RequestType).filter(RequestType.id == loan_request_data.request_type_id).first()
            if not request_type:
                raise HTTPException(
                    status_code=404,
                    detail=f"Request type with ID {loan_request_data.request_type_id} not found"
                )
            
            # Create new loan request
            db_loan_request = LoanRequest(
                branch_id=loan_request_data.branch_id,
                submitted_date=loan_request_data.submitted_date,
                customer_id=loan_request_data.customer_id,
                loan_type_id=loan_request_data.loan_type_id,
                request_type_id=loan_request_data.request_type_id,
                request_limit_usd=loan_request_data.request_limit_usd,
                request_limit_khr=loan_request_data.request_limit_khr,
                created_by=created_by
            )
            
            db.add(db_loan_request)
            db.commit()
            db.refresh(db_loan_request)
            
            return db_loan_request
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating loan request: {e}")
            raise HTTPException(status_code=500, detail="Failed to create loan request")

    @staticmethod
    def get_loan_request(db: Session, loan_request_id: int) -> Optional[LoanRequest]:
        """Get a loan request by ID."""
        loan_request = db.query(LoanRequest).filter(LoanRequest.id == loan_request_id).first()
        if not loan_request:
            raise HTTPException(status_code=404, detail="Loan request not found")
        return loan_request

    @staticmethod
    def get_loan_requests(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        branch_name: Optional[str] = None,
        loan_type: Optional[str] = None,
        request_type: Optional[str] = None,
        customer_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[LoanRequest], int]:
        """Get loan requests with pagination and filters."""
        query = db.query(LoanRequest)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(LoanRequest.is_active == is_active)
        
        if branch_name:
            query = query.join(Branch).filter(Branch.name.ilike(f"%{branch_name}%"))
        
        if loan_type:
            query = query.join(LoanType).filter(LoanType.name.ilike(f"%{loan_type}%"))
        
        if request_type:
            query = query.join(RequestType).filter(RequestType.name.ilike(f"%{request_type}%"))
        
        if customer_id:
            query = query.filter(LoanRequest.customer_id == customer_id)
        
        if search:
            # Search in customer name, national ID, or loan request details
            search_filter = or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.national_id.ilike(f"%{search}%"),
                Branch.name.ilike(f"%{search}%"),
                Branch.code.ilike(f"%{search}%"),
                LoanType.name.ilike(f"%{search}%"),
                LoanType.code.ilike(f"%{search}%"),
                RequestType.name.ilike(f"%{search}%"),
                RequestType.code.ilike(f"%{search}%")
            )
            query = query.join(Customer).join(Branch).join(LoanType).join(RequestType).filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        loan_requests = query.offset(skip).limit(limit).all()
        
        return loan_requests, total

    @staticmethod
    def update_loan_request(db: Session, loan_request_id: int, loan_request_data: LoanRequestUpdate) -> LoanRequest:
        """Update a loan request."""
        try:
            loan_request = LoanRequestService.get_loan_request(db, loan_request_id)
            
            # Check if customer exists if customer_id is being updated
            if loan_request_data.customer_id and loan_request_data.customer_id != loan_request.customer_id:
                customer = db.query(Customer).filter(Customer.id == loan_request_data.customer_id).first()
                if not customer:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Customer with ID {loan_request_data.customer_id} not found"
                    )
            
            # Check if branch exists if branch_id is being updated
            if loan_request_data.branch_id and loan_request_data.branch_id != loan_request.branch_id:
                branch = db.query(Branch).filter(Branch.id == loan_request_data.branch_id).first()
                if not branch:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Branch with ID {loan_request_data.branch_id} not found"
                    )
            
            # Check if loan type exists if loan_type_id is being updated
            if loan_request_data.loan_type_id and loan_request_data.loan_type_id != loan_request.loan_type_id:
                loan_type = db.query(LoanType).filter(LoanType.id == loan_request_data.loan_type_id).first()
                if not loan_type:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Loan type with ID {loan_request_data.loan_type_id} not found"
                    )
            
            # Check if request type exists if request_type_id is being updated
            if loan_request_data.request_type_id and loan_request_data.request_type_id != loan_request.request_type_id:
                request_type = db.query(RequestType).filter(RequestType.id == loan_request_data.request_type_id).first()
                if not request_type:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Request type with ID {loan_request_data.request_type_id} not found"
                    )
            
            # Update fields
            update_data = loan_request_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(loan_request, field, value)
            
            db.commit()
            db.refresh(loan_request)
            
            return loan_request
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating loan request: {e}")
            raise HTTPException(status_code=500, detail="Failed to update loan request")

    @staticmethod
    def delete_loan_request(db: Session, loan_request_id: int) -> bool:
        """Soft delete a loan request (set is_active to False)."""
        try:
            loan_request = LoanRequestService.get_loan_request(db, loan_request_id)
            loan_request.is_active = False
            db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting loan request: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete loan request")

    @staticmethod
    def get_loan_request_summary(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        branch_name: Optional[str] = None,
        loan_type: Optional[str] = None,
        request_type: Optional[str] = None
    ) -> tuple[List[dict], int]:
        """Get loan request summary for list view."""
        query = db.query(
            LoanRequest.id,
            Branch.name.label('branch_name'),
            LoanRequest.submitted_date,
            LoanType.name.label('loan_type'),
            RequestType.name.label('request_type'),
            LoanRequest.request_limit_usd,
            LoanRequest.request_limit_khr,
            LoanRequest.created_at,
            func.concat(Customer.first_name, ' ', Customer.last_name).label('customer_name')
        ).join(Customer).join(Branch).join(LoanType).join(RequestType)
        
        # Apply filters
        if branch_name:
            query = query.filter(Branch.name.ilike(f"%{branch_name}%"))
        
        if loan_type:
            query = query.filter(LoanType.name.ilike(f"%{loan_type}%"))
        
        if request_type:
            query = query.filter(RequestType.name.ilike(f"%{request_type}%"))
        
        if search:
            search_filter = or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.national_id.ilike(f"%{search}%"),
                Branch.name.ilike(f"%{search}%"),
                Branch.code.ilike(f"%{search}%"),
                LoanType.name.ilike(f"%{search}%"),
                LoanType.code.ilike(f"%{search}%"),
                RequestType.name.ilike(f"%{search}%"),
                RequestType.code.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        results = query.offset(skip).limit(limit).all()
        
        # Convert to list of dictionaries
        loan_requests = []
        for result in results:
            loan_requests.append({
                'id': result.id,
                'branch_name': result.branch_name,
                'submitted_date': result.submitted_date,
                'customer_name': result.customer_name,
                'loan_type': result.loan_type,
                'request_type': result.request_type,
                'request_limit_usd': float(result.request_limit_usd) if result.request_limit_usd else 0.0,
                'request_limit_khr': float(result.request_limit_khr) if result.request_limit_khr else 0.0,
                'created_at': result.created_at
            })
        
        return loan_requests, total

    @staticmethod
    def get_loan_request_statistics(db: Session) -> dict:
        """Get loan request statistics."""
        try:
            # Total loan requests
            total_requests = db.query(LoanRequest).filter(LoanRequest.is_active == True).count()
            
            # Total by branch
            branch_stats = db.query(
                Branch.name,
                func.count(LoanRequest.id).label('count')
            ).join(LoanRequest).filter(LoanRequest.is_active == True).group_by(Branch.name).all()
            
            # Total by loan type
            loan_type_stats = db.query(
                LoanType.name,
                func.count(LoanRequest.id).label('count')
            ).join(LoanRequest).filter(LoanRequest.is_active == True).group_by(LoanType.name).all()
            
            # Total by request type
            request_type_stats = db.query(
                RequestType.name,
                func.count(LoanRequest.id).label('count')
            ).join(LoanRequest).filter(LoanRequest.is_active == True).group_by(RequestType.name).all()
            
            # Total amounts
            total_usd = db.query(func.sum(LoanRequest.request_limit_usd)).filter(LoanRequest.is_active == True).scalar() or 0
            total_khr = db.query(func.sum(LoanRequest.request_limit_khr)).filter(LoanRequest.is_active == True).scalar() or 0
            
            return {
                'total_requests': total_requests,
                'total_usd': float(total_usd),
                'total_khr': float(total_khr),
                'by_branch': {stat.name: stat.count for stat in branch_stats},
                'by_loan_type': {stat.name: stat.count for stat in loan_type_stats},
                'by_request_type': {stat.name: stat.count for stat in request_type_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting loan request statistics: {e}")
            raise HTTPException(status_code=500, detail="Failed to get statistics") 