from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.loan_request_service import LoanRequestService
from app.domain.loan_request_schemas import (
    LoanRequestCreate, 
    LoanRequestUpdate, 
    LoanRequestResponse, 
    LoanRequestListResponse,
    LoanRequestSummaryList
)
from app.core.auth import get_current_user
from app.domain.rbac_models import User

router = APIRouter(prefix="/loan-requests", tags=["loan-requests"])

@router.post("/", response_model=LoanRequestResponse, status_code=201)
def create_loan_request(
    loan_request_data: LoanRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new loan request.
    
    - **branch_name**: Branch name (OLP, MRO, BBB, CLB, Other)
    - **submitted_date**: Date when the request was submitted
    - **customer_id**: ID of the customer making the request
    - **loan_type**: Type of loan (SME Loan, Home Loan, OD, BRD, BRP)
    - **request_type**: Type of request (New, Add, Renew, Extend, Restructure, Grace Period)
    - **request_limit_usd**: Request limit in USD (optional)
    - **request_limit_khr**: Request limit in KHR (optional)
    """
    loan_request = LoanRequestService.create_loan_request(db, loan_request_data, current_user.id)
    return loan_request

@router.get("/", response_model=LoanRequestListResponse)
def get_loan_requests(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for customer name, national ID, or loan details"),
    branch_name: Optional[str] = Query(None, description="Filter by branch name"),
    loan_type: Optional[str] = Query(None, description="Filter by loan type"),
    request_type: Optional[str] = Query(None, description="Filter by request type"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get loan requests with pagination and filters.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Number of records to return (max 1000)
    - **search**: Search term for customer name, national ID, or loan details
    - **branch_name**: Filter by branch name
    - **loan_type**: Filter by loan type
    - **request_type**: Filter by request type
    - **customer_id**: Filter by customer ID
    - **is_active**: Filter by active status
    """
    loan_requests, total = LoanRequestService.get_loan_requests(
        db, skip=skip, limit=limit, search=search, 
        branch_name=branch_name, loan_type=loan_type, request_type=request_type,
        customer_id=customer_id, is_active=is_active
    )
    
    return LoanRequestListResponse(
        loan_requests=loan_requests,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/summary", response_model=LoanRequestSummaryList)
def get_loan_request_summary(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for customer name, national ID, or loan details"),
    branch_name: Optional[str] = Query(None, description="Filter by branch name"),
    loan_type: Optional[str] = Query(None, description="Filter by loan type"),
    request_type: Optional[str] = Query(None, description="Filter by request type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get loan request summary for list view.
    
    Returns a simplified view with customer name and key details.
    """
    loan_requests, total = LoanRequestService.get_loan_request_summary(
        db, skip=skip, limit=limit, search=search,
        branch_name=branch_name, loan_type=loan_type, request_type=request_type
    )
    
    return LoanRequestSummaryList(
        loan_requests=loan_requests,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{loan_request_id}", response_model=LoanRequestResponse)
def get_loan_request(
    loan_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a loan request by ID.
    
    - **loan_request_id**: Loan request's unique identifier
    """
    loan_request = LoanRequestService.get_loan_request(db, loan_request_id)
    return loan_request

@router.put("/{loan_request_id}", response_model=LoanRequestResponse)
def update_loan_request(
    loan_request_id: int,
    loan_request_data: LoanRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a loan request.
    
    - **loan_request_id**: Loan request's unique identifier
    - **loan_request_data**: Loan request data to update (all fields optional)
    """
    loan_request = LoanRequestService.update_loan_request(db, loan_request_id, loan_request_data)
    return loan_request

@router.delete("/{loan_request_id}", status_code=204)
def delete_loan_request(
    loan_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a loan request (set is_active to False).
    
    - **loan_request_id**: Loan request's unique identifier
    """
    LoanRequestService.delete_loan_request(db, loan_request_id)
    return {"message": "Loan request deleted successfully"}

@router.get("/customer/{customer_id}", response_model=LoanRequestListResponse)
def get_loan_requests_by_customer(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all loan requests for a specific customer.
    
    - **customer_id**: Customer's unique identifier
    """
    loan_requests, total = LoanRequestService.get_loan_requests(
        db, skip=skip, limit=limit, customer_id=customer_id
    )
    
    return LoanRequestListResponse(
        loan_requests=loan_requests,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/statistics/summary")
def get_loan_request_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get loan request statistics.
    
    Returns summary statistics including:
    - Total requests
    - Total amounts in USD and KHR
    - Breakdown by branch, loan type, and request type
    """
    return LoanRequestService.get_loan_request_statistics(db)

@router.get("/enums/branches")
def get_branch_enums(db: Session = Depends(get_db)):
    """
    Get available branch options.
    """
    from app.domain.reference_models import Branch
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    return [{"id": branch.id, "code": branch.code, "name": branch.name, "description": branch.description} for branch in branches]

@router.get("/enums/loan-types")
def get_loan_type_enums(db: Session = Depends(get_db)):
    """
    Get available loan type options.
    """
    from app.domain.reference_models import LoanType
    loan_types = db.query(LoanType).filter(LoanType.is_active == True).all()
    return [{"id": loan_type.id, "code": loan_type.code, "name": loan_type.name, "description": loan_type.description} for loan_type in loan_types]

@router.get("/enums/request-types")
def get_request_type_enums(db: Session = Depends(get_db)):
    """
    Get available request type options.
    """
    from app.domain.reference_models import RequestType
    request_types = db.query(RequestType).filter(RequestType.is_active == True).all()
    return [{"id": request_type.id, "code": request_type.code, "name": request_type.name, "description": request_type.description} for request_type in request_types] 