from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.services.rbac_service import RBACService
from app.services.rbac_middleware import (
    require_admin, require_edit_users, require_read_users,
    require_edit_roles, require_read_roles,
    get_current_user_with_permissions
)
from app.domain.rbac_models import User
from app.domain.rbac_schemas import (
    UserCreate, UserResponse, UserUpdate, UserRoleAssign,
    RoleCreate, RoleResponse, RoleUpdate, RolePermissionAssign,
    PermissionCreate, PermissionResponse, PermissionUpdate,
    PermissionCheck, PermissionCheckResponse
)
from app.core.database import get_db

router = APIRouter(prefix="/rbac", tags=["RBAC Management"])

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_edit_users),
    db: Session = Depends(get_db)
):
    """Create a new user with optional role assignments."""
    rbac_service = RBACService(db)
    return rbac_service.create_user(user_data, created_by=current_user.id)

@router.get("/users", response_model=List[UserResponse])
def get_users(
    current_user: User = Depends(require_read_users),
    db: Session = Depends(get_db)
):
    """Get all users with their roles."""
    rbac_service = RBACService(db)
    return rbac_service.get_all_users()

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_read_users),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID."""
    rbac_service = RBACService(db)
    user = rbac_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_edit_users),
    db: Session = Depends(get_db)
):
    """Update a user's information."""
    rbac_service = RBACService(db)
    return rbac_service.update_user(user_id, user_data.dict(exclude_unset=True))

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_edit_users),
    db: Session = Depends(get_db)
):
    """Delete a user."""
    rbac_service = RBACService(db)
    rbac_service.delete_user(user_id)

@router.post("/users/{user_id}/roles", response_model=dict)
def assign_role_to_user(
    user_id: int,
    assignment: UserRoleAssign,
    current_user: User = Depends(require_edit_users),
    db: Session = Depends(get_db)
):
    """Assign a role to a user."""
    rbac_service = RBACService(db)
    user_role = rbac_service.assign_role_to_user(assignment)
    return {"message": "Role assigned successfully", "user_role": user_role}

@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_edit_users),
    db: Session = Depends(get_db)
):
    """Remove a role from a user."""
    rbac_service = RBACService(db)
    rbac_service.remove_role_from_user(user_id, role_id)

# ============================================================================
# ROLE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/roles", response_model=RoleResponse)
def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_edit_roles),
    db: Session = Depends(get_db)
):
    """Create a new role with optional permission assignments."""
    rbac_service = RBACService(db)
    return rbac_service.create_role(role_data)

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(
    current_user: User = Depends(require_read_roles),
    db: Session = Depends(get_db)
):
    """Get all roles with their permissions."""
    rbac_service = RBACService(db)
    return rbac_service.get_all_roles()

@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    current_user: User = Depends(require_read_roles),
    db: Session = Depends(get_db)
):
    """Get a specific role by ID."""
    rbac_service = RBACService(db)
    role = rbac_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_edit_roles),
    db: Session = Depends(get_db)
):
    """Update a role's information."""
    rbac_service = RBACService(db)
    return rbac_service.update_role(role_id, role_data.dict(exclude_unset=True))

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    current_user: User = Depends(require_edit_roles),
    db: Session = Depends(get_db)
):
    """Delete a role."""
    rbac_service = RBACService(db)
    rbac_service.delete_role(role_id)

@router.post("/roles/{role_id}/permissions", response_model=dict)
def assign_permission_to_role(
    role_id: int,
    assignment: RolePermissionAssign,
    current_user: User = Depends(require_edit_roles),
    db: Session = Depends(get_db)
):
    """Assign a permission to a role."""
    rbac_service = RBACService(db)
    rbac_service.assign_permission_to_role(assignment)
    return {"message": "Permission assigned successfully"}

@router.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(require_edit_roles),
    db: Session = Depends(get_db)
):
    """Remove a permission from a role."""
    rbac_service = RBACService(db)
    rbac_service.remove_permission_from_role(role_id, permission_id)

# ============================================================================
# PERMISSION MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/permissions", response_model=PermissionResponse)
def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_edit_roles),
    db: Session = Depends(get_db)
):
    """Create a new permission."""
    rbac_service = RBACService(db)
    return rbac_service.create_permission(permission_data)

@router.get("/permissions", response_model=List[PermissionResponse])
def get_permissions(
    current_user: User = Depends(require_read_roles),
    db: Session = Depends(get_db)
):
    """Get all permissions."""
    rbac_service = RBACService(db)
    return rbac_service.get_all_permissions()

@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    current_user: User = Depends(require_read_roles),
    db: Session = Depends(get_db)
):
    """Get a specific permission by ID."""
    rbac_service = RBACService(db)
    permission = rbac_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission

@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    current_user: User = Depends(require_edit_roles),
    db: Session = Depends(get_db)
):
    """Update a permission's information."""
    rbac_service = RBACService(db)
    permission = rbac_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    for field, value in permission_data.dict(exclude_unset=True).items():
        if hasattr(permission, field):
            setattr(permission, field, value)
    
    db.commit()
    db.refresh(permission)
    return permission

# ============================================================================
# PERMISSION CHECKING ENDPOINTS
# ============================================================================

@router.post("/check-permission", response_model=PermissionCheckResponse)
def check_permission(
    permission_check: PermissionCheck,
    current_user: User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Check if the current user has a specific permission."""
    rbac_service = RBACService(db)
    has_permission = rbac_service.check_user_permission(
        current_user["user"].id, 
        permission_check.action, 
        permission_check.resource
    )
    
    return PermissionCheckResponse(
        has_permission=has_permission,
        user_roles=current_user["roles"],
        required_permission=f"{permission_check.action}:{permission_check.resource}"
    )

@router.get("/my-permissions", response_model=dict)
def get_my_permissions(
    current_user: User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Get current user's permissions and roles."""
    return {
        "user": {
            "id": current_user["user"].id,
            "username": current_user["user"].username,
            "email": current_user["user"].email,
            "full_name": current_user["user"].full_name,
            "department": current_user["user"].department
        },
        "roles": current_user["roles"],
        "permissions": current_user["permissions"]
    }

# ============================================================================
# SYSTEM INITIALIZATION ENDPOINTS
# ============================================================================

@router.post("/initialize", response_model=dict)
def initialize_rbac_system(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Initialize the RBAC system with default roles and permissions."""
    rbac_service = RBACService(db)
    rbac_service.initialize_default_data()
    return {"message": "RBAC system initialized successfully"}

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/health", response_model=dict)
def rbac_health_check(db: Session = Depends(get_db)):
    """Health check for RBAC system."""
    rbac_service = RBACService(db)
    
    # Count basic entities
    user_count = len(rbac_service.get_all_users())
    role_count = len(rbac_service.get_all_roles())
    permission_count = len(rbac_service.get_all_permissions())
    
    return {
        "status": "healthy",
        "user_count": user_count,
        "role_count": role_count,
        "permission_count": permission_count
    } 