from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import Body
from app.services.rbac_middleware import (
    require_read_collateral, require_edit_collateral, 
    require_clear_collateral, require_authorize_collateral,
    require_comment_collateral, require_collateral_access
)
from app.domain.rbac_models import User
from app.infrastructure.database import get_db

router = APIRouter(prefix="/collateral", tags=["Property Evaluation"])

# Sample data model for collateral evaluation
class CollateralEvaluation(BaseModel):
    id: Optional[int] = None
    property_address: str = Field(..., description="Property address")
    property_type: str = Field(..., description="Type of property (residential, commercial, etc.)")
    estimated_value: float = Field(..., description="Estimated property value")
    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    evaluator_id: Optional[int] = None
    evaluator_name: Optional[str] = None
    status: str = Field(default="pending", description="Status: pending, approved, rejected")
    comments: Optional[str] = None
    authorized_by: Optional[int] = None
    authorized_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CollateralCreate(BaseModel):
    property_address: str
    property_type: str
    estimated_value: float
    comments: Optional[str] = None

class CollateralUpdate(BaseModel):
    property_address: Optional[str] = None
    property_type: Optional[str] = None
    estimated_value: Optional[float] = None
    comments: Optional[str] = None

class CollateralAuthorization(BaseModel):
    status: str = Field(..., description="Status: approved, rejected")
    comments: Optional[str] = None

# In-memory storage for demo purposes (replace with database in production)
collateral_evaluations = []
next_id = 1

@router.get("/", response_model=List[CollateralEvaluation])
def get_collateral_evaluations(
    current_user: User = Depends(require_read_collateral),
    db: Session = Depends(get_db)
):
    """Get all collateral evaluations (Viewer, Inputter, Authorizer, Admin can access)."""
    return collateral_evaluations

@router.get("/{evaluation_id}", response_model=CollateralEvaluation)
def get_collateral_evaluation(
    evaluation_id: int,
    current_user: User = Depends(require_read_collateral),
    db: Session = Depends(get_db)
):
    """Get a specific collateral evaluation by ID."""
    for evaluation in collateral_evaluations:
        if evaluation.id == evaluation_id:
            return evaluation
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Collateral evaluation not found"
    )

@router.post("/", response_model=CollateralEvaluation)
def create_collateral_evaluation(
    evaluation_data: CollateralCreate,
    current_user: User = Depends(require_edit_collateral),
    db: Session = Depends(get_db)
):
    """Create a new collateral evaluation (Inputter, Authorizer, Admin can create)."""
    global next_id
    
    evaluation = CollateralEvaluation(
        id=next_id,
        property_address=evaluation_data.property_address,
        property_type=evaluation_data.property_type,
        estimated_value=evaluation_data.estimated_value,
        evaluator_id=current_user.id,
        evaluator_name=current_user.full_name or current_user.username,
        comments=evaluation_data.comments,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    collateral_evaluations.append(evaluation)
    next_id += 1
    
    return evaluation

@router.put("/{evaluation_id}", response_model=CollateralEvaluation)
def update_collateral_evaluation(
    evaluation_id: int,
    evaluation_data: CollateralUpdate,
    current_user: User = Depends(require_edit_collateral),
    db: Session = Depends(get_db)
):
    """Update a collateral evaluation (Inputter, Authorizer, Admin can edit)."""
    for evaluation in collateral_evaluations:
        if evaluation.id == evaluation_id:
            # Update fields
            if evaluation_data.property_address is not None:
                evaluation.property_address = evaluation_data.property_address
            if evaluation_data.property_type is not None:
                evaluation.property_type = evaluation_data.property_type
            if evaluation_data.estimated_value is not None:
                evaluation.estimated_value = evaluation_data.estimated_value
            if evaluation_data.comments is not None:
                evaluation.comments = evaluation_data.comments
            
            evaluation.updated_at = datetime.utcnow()
            return evaluation
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Collateral evaluation not found"
    )

@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_collateral_evaluation(
    evaluation_id: int,
    current_user: User = Depends(require_clear_collateral),
    db: Session = Depends(get_db)
):
    """Clear/delete a collateral evaluation (Inputter, Authorizer, Admin can clear)."""
    global collateral_evaluations
    
    for i, evaluation in enumerate(collateral_evaluations):
        if evaluation.id == evaluation_id:
            del collateral_evaluations[i]
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Collateral evaluation not found"
    )

@router.post("/{evaluation_id}/authorize", response_model=CollateralEvaluation)
def authorize_collateral_evaluation(
    evaluation_id: int,
    authorization_data: CollateralAuthorization,
    current_user: User = Depends(require_authorize_collateral),
    db: Session = Depends(get_db)
):
    """Authorize a collateral evaluation (Authorizer, Admin can authorize)."""
    for evaluation in collateral_evaluations:
        if evaluation.id == evaluation_id:
            evaluation.status = authorization_data.status
            evaluation.authorized_by = current_user.id
            evaluation.authorized_at = datetime.utcnow()
            evaluation.updated_at = datetime.utcnow()
            
            # Add authorization comment
            if authorization_data.comments:
                existing_comments = evaluation.comments or ""
                evaluation.comments = f"{existing_comments}\n[Authorization by {current_user.full_name or current_user.username}]: {authorization_data.comments}"
            
            return evaluation
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Collateral evaluation not found"
    )

@router.post("/{evaluation_id}/comment", response_model=CollateralEvaluation)
def add_comment_to_evaluation(
    evaluation_id: int,
    comment: str = Body(..., description="Comment to add"),
    current_user: User = Depends(require_comment_collateral),
    db: Session = Depends(get_db)
):
    """Add a comment to a collateral evaluation (Authorizer, Admin can comment)."""
    for evaluation in collateral_evaluations:
        if evaluation.id == evaluation_id:
            existing_comments = evaluation.comments or ""
            new_comment = f"[{current_user.full_name or current_user.username} at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}]: {comment}"
            evaluation.comments = f"{existing_comments}\n{new_comment}" if existing_comments else new_comment
            evaluation.updated_at = datetime.utcnow()
            return evaluation
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Collateral evaluation not found"
    )

@router.get("/my-evaluations", response_model=List[CollateralEvaluation])
def get_my_evaluations(
    current_user: User = Depends(require_read_collateral),
    db: Session = Depends(get_db)
):
    """Get evaluations created by the current user."""
    return [
        evaluation for evaluation in collateral_evaluations 
        if evaluation.evaluator_id == current_user.id
    ]

@router.get("/pending-authorization", response_model=List[CollateralEvaluation])
def get_pending_authorizations(
    current_user: User = Depends(require_authorize_collateral),
    db: Session = Depends(get_db)
):
    """Get evaluations pending authorization (Authorizer, Admin can see)."""
    return [
        evaluation for evaluation in collateral_evaluations 
        if evaluation.status == "pending"
    ]

@router.get("/stats/summary", response_model=dict)
def get_evaluation_stats(
    current_user: User = Depends(require_read_collateral),
    db: Session = Depends(get_db)
):
    """Get evaluation statistics."""
    total_evaluations = len(collateral_evaluations)
    pending_count = len([e for e in collateral_evaluations if e.status == "pending"])
    approved_count = len([e for e in collateral_evaluations if e.status == "approved"])
    rejected_count = len([e for e in collateral_evaluations if e.status == "rejected"])
    
    total_value = sum(e.estimated_value for e in collateral_evaluations if e.status == "approved")
    
    return {
        "total_evaluations": total_evaluations,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "total_approved_value": total_value,
        "average_value": total_value / approved_count if approved_count > 0 else 0
    } 