from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.domain.rbac_models import User, Role, Permission, user_roles
from app.domain.rbac_schemas import (
    UserCreate, RoleCreate, PermissionCreate, 
    UserRoleAssign, RolePermissionAssign
)

class RBACService:
    def __init__(self, db: Session):
        self.db = db

    # User Management
    def create_user(self, user_data: UserCreate, created_by: Optional[int] = None) -> User:
        """Create a new user with optional role assignments."""
        # Check if username or email already exists
        existing_user = self.db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            department=user_data.department
        )
        user.set_password(user_data.password)
        
        self.db.add(user)
        self.db.flush()  # Get the user ID

        # Assign roles if provided
        if user_data.role_names:
            for role_name in user_data.role_names:
                role = self.db.query(Role).filter(Role.name == role_name).first()
                if role:
                    # Insert role assignment directly
                    self.db.execute(
                        user_roles.insert().values(
                            user_id=user.id,
                            role_id=role.id
                        )
                    )

        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with roles and permissions."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username with roles and permissions."""
        return self.db.query(User).filter(User.username == username).first()

    def get_all_users(self) -> List[User]:
        """Get all users with their roles."""
        return self.db.query(User).all()

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update fields
        for field, value in user_data.items():
            if hasattr(user, field) and value is not None:
                if field == "password":
                    user.set_password(value)
                else:
                    setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        self.db.delete(user)
        self.db.commit()
        return True

    # Role Management
    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role with optional permission assignments."""
        existing_role = self.db.query(Role).filter(Role.name == role_data.name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists"
            )

        role = Role(
            name=role_data.name,
            description=role_data.description
        )
        self.db.add(role)
        self.db.flush()

        # Assign permissions if provided
        if role_data.permission_names:
            for perm_name in role_data.permission_names:
                action, resource = perm_name.split(":", 1) if ":" in perm_name else (perm_name, "*")
                permission = self.db.query(Permission).filter(
                    Permission.action == action,
                    Permission.resource == resource
                ).first()
                if permission:
                    role.permissions.append(permission)

        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID with permissions."""
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get role by name with permissions."""
        return self.db.query(Role).filter(Role.name == role_name).first()

    def get_all_roles(self) -> List[Role]:
        """Get all roles with their permissions."""
        return self.db.query(Role).all()

    def update_role(self, role_id: int, role_data: Dict[str, Any]) -> Role:
        """Update role information."""
        role = self.get_role_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        for field, value in role_data.items():
            if hasattr(role, field) and value is not None:
                setattr(role, field, value)

        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: int) -> bool:
        """Delete a role."""
        role = self.get_role_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        self.db.delete(role)
        self.db.commit()
        return True

    # Permission Management
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        existing_permission = self.db.query(Permission).filter(
            Permission.action == permission_data.action,
            Permission.resource == permission_data.resource
        ).first()
        
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists"
            )

        permission = Permission(
            action=permission_data.action,
            resource=permission_data.resource,
            description=permission_data.description
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID."""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()

    def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        return self.db.query(Permission).all()

    # Role Assignment
    def assign_role_to_user(self, assignment: UserRoleAssign) -> dict:
        """Assign a role to a user."""
        # Check if user exists
        user = self.get_user_by_id(assignment.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if role exists
        role = self.get_role_by_id(assignment.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        # Check if assignment already exists
        existing_assignment = self.db.execute(
            user_roles.select().where(
                user_roles.c.user_id == assignment.user_id,
                user_roles.c.role_id == assignment.role_id
            )
        ).first()

        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this role"
            )

        # Insert the assignment
        self.db.execute(
            user_roles.insert().values(
                user_id=assignment.user_id,
                role_id=assignment.role_id,
                assigned_by=assignment.assigned_by
            )
        )
        self.db.commit()
        
        return {
            "user_id": assignment.user_id,
            "role_id": assignment.role_id
        }

    def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Remove a role from a user."""
        result = self.db.execute(
            user_roles.delete().where(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id
            )
        )
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )

        self.db.commit()
        return True

    def get_user_roles(self, user_id: int) -> List[dict]:
        """Get all roles assigned to a user."""
        result = self.db.execute(
            user_roles.select().where(user_roles.c.user_id == user_id)
        ).fetchall()
        
        return [
            {
                "user_id": row.user_id,
                "role_id": row.role_id
            }
            for row in result
        ]

    # Permission Assignment
    def assign_permission_to_role(self, assignment: RolePermissionAssign) -> bool:
        """Assign a permission to a role."""
        role = self.get_role_by_id(assignment.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        permission = self.get_permission_by_id(assignment.permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        # Check if assignment already exists
        if permission in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already has this permission"
            )

        role.permissions.append(permission)
        self.db.commit()
        return True

    def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove a permission from a role."""
        role = self.get_role_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        permission = self.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        if permission not in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role does not have this permission"
            )

        role.permissions.remove(permission)
        self.db.commit()
        return True

    # Permission Checking
    def check_user_permission(self, user_id: int, action: str, resource: str) -> bool:
        """Check if a user has a specific permission."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        return user.has_permission(action, resource)

    def get_user_permissions(self, user_id: int) -> List[Dict[str, str]]:
        """Get all permissions for a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return []

        permissions = []
        for role in user.roles:
            for permission in role.permissions:
                permissions.append({
                    "action": permission.action,
                    "resource": permission.resource,
                    "role": role.name
                })
        return permissions

    # Initialize default data
    def initialize_default_data(self):
        """Initialize default roles and permissions for the Property Evaluation system."""
        # Create default permissions
        default_permissions = [
            ("read", "collateral_evaluation", "View collateral evaluation data"),
            ("edit", "collateral_evaluation", "Edit collateral evaluation data"),
            ("clear", "collateral_evaluation", "Clear collateral evaluation data"),
            ("authorize", "collateral_evaluation", "Authorize collateral evaluation"),
            ("comment", "collateral_evaluation", "Add comments to evaluations"),
            ("read", "user_management", "View user information"),
            ("edit", "user_management", "Manage users"),
            ("read", "role_management", "View roles and permissions"),
            ("edit", "role_management", "Manage roles and permissions"),
        ]

        for action, resource, description in default_permissions:
            existing = self.db.query(Permission).filter(
                Permission.action == action,
                Permission.resource == resource
            ).first()
            if not existing:
                permission = Permission(
                    action=action,
                    resource=resource,
                    description=description
                )
                self.db.add(permission)

        self.db.commit()

        # Create default roles
        default_roles = [
            ("Viewer", "Can only view collateral evaluation data"),
            ("Inputter", "Can input and edit collateral evaluation data"),
            ("Authorizer", "Can authorize collateral evaluations and manage the system"),
            ("Admin", "Full system administration access")
        ]

        for role_name, description in default_roles:
            existing_role = self.db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                role = Role(name=role_name, description=description)
                self.db.add(role)
                self.db.flush()

                # Assign permissions based on role
                if role_name == "Viewer":
                    permissions = self.db.query(Permission).filter(
                        Permission.action == "read"
                    ).all()
                elif role_name == "Inputter":
                    permissions = self.db.query(Permission).filter(
                        Permission.action.in_(["read", "edit", "clear"])
                    ).all()
                elif role_name == "Authorizer":
                    permissions = self.db.query(Permission).filter(
                        Permission.action.in_(["read", "edit", "authorize", "comment"])
                    ).all()
                elif role_name == "Admin":
                    permissions = self.db.query(Permission).all()

                for permission in permissions:
                    role.permissions.append(permission)

        self.db.commit() 