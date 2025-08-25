from typing import Optional, List
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.domain.rbac_models import User
from app.services.rbac_service import RBACService
from app.infrastructure.database import get_db

security = HTTPBearer()

def require_permission(action: str, resource: str):
    """
    Decorator to require a specific permission for a route.
    
    Usage:
    @app.get("/collateral/{id}")
    @require_permission("read", "collateral_evaluation")
    def get_collateral(id: int, current_user: User = Depends(get_current_user)):
        ...
    """
    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        rbac_service = RBACService(db)
        
        if not rbac_service.check_user_permission(current_user.id, action, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {action}:{resource}"
            )
        
        return current_user
    
    return permission_dependency

def require_any_permission(permissions: List[tuple]):
    """
    Decorator to require any one of the specified permissions.
    
    Usage:
    @app.get("/collateral/{id}")
    @require_any_permission([("read", "collateral_evaluation"), ("edit", "collateral_evaluation")])
    def get_collateral(id: int, current_user: User = Depends(get_current_user)):
        ...
    """
    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        rbac_service = RBACService(db)
        
        for action, resource in permissions:
            if rbac_service.check_user_permission(current_user.id, action, resource):
                return current_user
        
        required_permissions = ", ".join([f"{action}:{resource}" for action, resource in permissions])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required one of: {required_permissions}"
        )
    
    return permission_dependency

def require_all_permissions(permissions: List[tuple]):
    """
    Decorator to require all specified permissions.
    
    Usage:
    @app.get("/admin/dashboard")
    @require_all_permissions([("read", "user_management"), ("read", "role_management")])
    def admin_dashboard(current_user: User = Depends(get_current_user)):
        ...
    """
    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        rbac_service = RBACService(db)
        
        for action, resource in permissions:
            if not rbac_service.check_user_permission(current_user.id, action, resource):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {action}:{resource}"
                )
        
        return current_user
    
    return permission_dependency

def require_role(role_name: str):
    """
    Decorator to require a specific role.
    
    Usage:
    @app.get("/admin/users")
    @require_role("Admin")
    def get_users(current_user: User = Depends(get_current_user)):
        ...
    """
    def role_dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {role_name}"
            )
        
        return current_user
    
    return role_dependency

def require_any_role(role_names: List[str]):
    """
    Decorator to require any one of the specified roles.
    
    Usage:
    @app.get("/collateral/{id}")
    @require_any_role(["Authorizer", "Admin"])
    def authorize_collateral(id: int, current_user: User = Depends(get_current_user)):
        ...
    """
    def role_dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:
        for role_name in role_names:
            if current_user.has_role(role_name):
                return current_user
        
        required_roles = ", ".join(role_names)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required one of roles: {required_roles}"
        )
    
    return role_dependency

# Predefined permission dependencies for common operations
require_read_collateral = require_permission("read", "collateral_evaluation")
require_edit_collateral = require_permission("edit", "collateral_evaluation")
require_clear_collateral = require_permission("clear", "collateral_evaluation")
require_authorize_collateral = require_permission("authorize", "collateral_evaluation")
require_comment_collateral = require_permission("comment", "collateral_evaluation")

require_read_users = require_permission("read", "user_management")
require_edit_users = require_permission("edit", "user_management")
require_read_roles = require_permission("read", "role_management")
require_edit_roles = require_permission("edit", "role_management")

# Predefined role dependencies
require_viewer = require_role("Viewer")
require_inputter = require_role("Inputter")
require_authorizer = require_role("Authorizer")
require_admin = require_role("Admin")

# Combined permission dependencies
require_collateral_access = require_any_permission([
    ("read", "collateral_evaluation"),
    ("edit", "collateral_evaluation"),
    ("authorize", "collateral_evaluation")
])

require_admin_access = require_all_permissions([
    ("read", "user_management"),
    ("edit", "user_management"),
    ("read", "role_management"),
    ("edit", "role_management")
])

# Utility function to get current user with permissions
def get_current_user_with_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get current user with their permissions."""
    rbac_service = RBACService(db)
    permissions = rbac_service.get_user_permissions(current_user.id)
    
    return {
        "user": current_user,
        "permissions": permissions,
        "roles": [role.name for role in current_user.roles]
    }

# Middleware to log permission checks (optional)
class RBACLoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Log permission checks here if needed
            pass
        
        await self.app(scope, receive, send) 