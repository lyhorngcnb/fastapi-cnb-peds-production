from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.infrastructure.database import get_db
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.domain.rbac_models import User
from app.services.rbac_service import RBACService

# Security scheme
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedException("Invalid token")
    except JWTError:
        raise UnauthorizedException("Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise UnauthorizedException("User not found")
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise UnauthorizedException("Inactive user")
    return current_user

def require_permission(permission: str):
    """Dependency to require a specific permission."""
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        rbac_service = RBACService(db)
        if not rbac_service.has_permission(current_user.id, permission):
            raise ForbiddenException(f"Permission '{permission}' required")
        return current_user
    
    return permission_checker

def require_role(role: str):
    """Dependency to require a specific role."""
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        rbac_service = RBACService(db)
        if not rbac_service.has_role(current_user.id, role):
            raise ForbiddenException(f"Role '{role}' required")
        return current_user
    
    return role_checker

# Common dependencies
def get_rbac_service(db: Session = Depends(get_db)) -> RBACService:
    """Get RBAC service instance."""
    return RBACService(db) 