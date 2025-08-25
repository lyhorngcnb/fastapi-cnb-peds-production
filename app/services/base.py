from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.repositories.base import BaseRepository
from app.core.exceptions import NotFoundException, ValidationException

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service with common business logic operations."""
    
    def __init__(self, repository: RepositoryType):
        self.repository = repository
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.repository.get(db, id)
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering."""
        return self.repository.get_multi(db, skip, limit, filters)
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record with validation."""
        self._validate_create_data(obj_in)
        return self.repository.create(db, obj_in)
    
    def update(
        self, 
        db: Session, 
        id: Any, 
        obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """Update an existing record with validation."""
        self._validate_update_data(obj_in)
        return self.repository.update(db, id, obj_in)
    
    def delete(self, db: Session, id: Any) -> bool:
        """Delete a record by ID."""
        return self.repository.delete(db, id)
    
    def count(self, db: Session, filters: Optional[dict] = None) -> int:
        """Count records with optional filtering."""
        return self.repository.count(db, filters)
    
    def exists(self, db: Session, id: Any) -> bool:
        """Check if a record exists by ID."""
        return self.repository.exists(db, id)
    
    def _validate_create_data(self, obj_in: CreateSchemaType) -> None:
        """Validate data before creation. Override in subclasses for custom validation."""
        pass
    
    def _validate_update_data(self, obj_in: UpdateSchemaType) -> None:
        """Validate data before update. Override in subclasses for custom validation."""
        pass
    
    def _check_business_rules(self, obj_in: Any) -> None:
        """Check business rules. Override in subclasses for custom business logic."""
        pass 