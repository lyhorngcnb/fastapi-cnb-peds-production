from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.core.rbac_service import RBACService
from app.schemas.rbac import (
    RoleCreateSchema,
    RoleUpdateSchema,
    RoleResponseSchema,
    PermissionCreateSchema,
    PermissionUpdateSchema,
    PermissionResponseSchema,
    UserRoleCreateSchema,
    UserRoleResponseSchema
)
from app.core.dependencies import get_current_active_user, require_permission
from app.core.exceptions import NotFoundException, ValidationException, ConflictException
from app.domain.rbac_models import User

router = APIRouter(prefix="/rbac", tags=["rbac"])

# Role management endpoints
@router.post("/roles", response_model=RoleResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:role:create"))
):
    """Create a new role."""
    try:
        rbac_service = RBACService(db)
        role = rbac_service.create_role(role_data)
        return role
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/roles", response_model=List[RoleResponseSchema])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:role:read"))
):
    """Get all roles."""
    try:
        rbac_service = RBACService(db)
        roles = rbac_service.get_all_roles()
        return roles
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/roles/{role_id}", response_model=RoleResponseSchema)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:role:read"))
):
    """Get a specific role by ID."""
    try:
        rbac_service = RBACService(db)
        role = rbac_service.get_role(role_id)
        if not role:
            raise NotFoundException("Role", role_id)
        return role
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/roles/{role_id}", response_model=RoleResponseSchema)
async def update_role(
    role_id: int,
    role_data: RoleUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:role:update"))
):
    """Update a role."""
    try:
        rbac_service = RBACService(db)
        role = rbac_service.update_role(role_id, role_data)
        if not role:
            raise NotFoundException("Role", role_id)
        return role
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:role:delete"))
):
    """Delete a role."""
    try:
        rbac_service = RBACService(db)
        success = rbac_service.delete_role(role_id)
        if not success:
            raise NotFoundException("Role", role_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Permission management endpoints
@router.post("/permissions", response_model=PermissionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:permission:create"))
):
    """Create a new permission."""
    try:
        rbac_service = RBACService(db)
        permission = rbac_service.create_permission(permission_data)
        return permission
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/permissions", response_model=List[PermissionResponseSchema])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:permission:read"))
):
    """Get all permissions."""
    try:
        rbac_service = RBACService(db)
        permissions = rbac_service.get_all_permissions()
        return permissions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/permissions/{permission_id}", response_model=PermissionResponseSchema)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:permission:read"))
):
    """Get a specific permission by ID."""
    try:
        rbac_service = RBACService(db)
        permission = rbac_service.get_permission(permission_id)
        if not permission:
            raise NotFoundException("Permission", permission_id)
        return permission
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/permissions/{permission_id}", response_model=PermissionResponseSchema)
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:permission:update"))
):
    """Update a permission."""
    try:
        rbac_service = RBACService(db)
        permission = rbac_service.update_permission(permission_id, permission_data)
        if not permission:
            raise NotFoundException("Permission", permission_id)
        return permission
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:permission:delete"))
):
    """Delete a permission."""
    try:
        rbac_service = RBACService(db)
        success = rbac_service.delete_permission(permission_id)
        if not success:
            raise NotFoundException("Permission", permission_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# User role assignment endpoints
@router.post("/users/{user_id}/roles", response_model=UserRoleResponseSchema, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    user_id: int,
    user_role_data: UserRoleCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:user:assign_role"))
):
    """Assign a role to a user."""
    try:
        rbac_service = RBACService(db)
        user_role = rbac_service.assign_role_to_user(user_id, user_role_data.role_id)
        return user_role
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac:user:remove_role"))
):
    """Remove a role from a user."""
    try:
        rbac_service = RBACService(db)
        success = rbac_service.remove_role_from_user(user_id, role_id)
        if not success:
            raise NotFoundException("User Role", f"{user_id}-{role_id}")
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 