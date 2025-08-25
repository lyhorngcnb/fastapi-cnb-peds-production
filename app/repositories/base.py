from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from pydantic import BaseModel
from app.core.exceptions import NotFoundException, DatabaseException

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            raise DatabaseException(f"Error retrieving {self.model.__name__}: {str(e)}")
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering."""
        try:
            query = db.query(self.model)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        query = query.filter(getattr(self.model, field) == value)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(f"Error retrieving {self.model.__name__} list: {str(e)}")
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        try:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Error creating {self.model.__name__}: {str(e)}")
    
    def update(
        self, 
        db: Session, 
        id: Any, 
        obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """Update an existing record."""
        try:
            db_obj = self.get(db, id)
            if not db_obj:
                raise NotFoundException(self.model.__name__, id)
            
            obj_data = obj_in.model_dump(exclude_unset=True)
            for field, value in obj_data.items():
                setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except NotFoundException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Error updating {self.model.__name__}: {str(e)}")
    
    def delete(self, db: Session, id: Any) -> bool:
        """Delete a record by ID."""
        try:
            db_obj = self.get(db, id)
            if not db_obj:
                raise NotFoundException(self.model.__name__, id)
            
            db.delete(db_obj)
            db.commit()
            return True
        except NotFoundException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Error deleting {self.model.__name__}: {str(e)}")
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        try:
            query = db.query(self.model)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        query = query.filter(getattr(self.model, field) == value)
            
            return query.count()
        except Exception as e:
            raise DatabaseException(f"Error counting {self.model.__name__}: {str(e)}")
    
    def exists(self, db: Session, id: Any) -> bool:
        """Check if a record exists by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first() is not None
        except Exception as e:
            raise DatabaseException(f"Error checking existence of {self.model.__name__}: {str(e)}") 