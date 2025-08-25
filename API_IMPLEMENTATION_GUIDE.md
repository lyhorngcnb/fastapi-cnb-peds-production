# API Implementation Guide

## 🚀 **Step-by-Step Process for Creating New APIs**

### **1. Plan Your API**
- Define the API purpose and functionality
- Identify required data models
- Plan the endpoints (GET, POST, PUT, DELETE)
- Define request/response schemas

### **2. Create Domain Models** (if needed)
```bash
# Location: app/domain/
# Example: app/domain/your_model.py
```

**Example:**
```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.domain.rbac_models import Base

class YourModel(Base):
    __tablename__ = "your_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### **3. Create Schemas** (Request/Response models)
```bash
# Location: app/domain/your_schemas.py
# or app/schemas/your_schemas.py
```

**Example:**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class YourModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class YourModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class YourModelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
```

### **4. Create Service Layer**
```bash
# Location: app/core/your_service.py
```

**Example:**
```python
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.domain.your_model import YourModel
from app.domain.your_schemas import YourModelCreate, YourModelUpdate
import logging

logger = logging.getLogger(__name__)

class YourService:
    """Service for your business logic."""
    
    @staticmethod
    def create_your_model(db: Session, data: YourModelCreate, user_id: int) -> YourModel:
        """Create a new record."""
        try:
            your_model = YourModel(
                name=data.name,
                description=data.description,
                created_by=user_id
            )
            db.add(your_model)
            db.commit()
            db.refresh(your_model)
            return your_model
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating your model: {e}")
            raise HTTPException(status_code=500, detail="Failed to create record")
    
    @staticmethod
    def get_your_model(db: Session, model_id: int) -> Optional[YourModel]:
        """Get a record by ID."""
        return db.query(YourModel).filter(YourModel.id == model_id).first()
    
    @staticmethod
    def get_your_models(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get records with pagination and filtering."""
        query = db.query(YourModel)
        
        if search:
            query = query.filter(YourModel.name.contains(search))
        
        total = query.count()
        models = query.offset(skip).limit(limit).all()
        
        return {
            "items": models,
            "total": total,
            "page": skip // limit + 1,
            "size": limit
        }
    
    @staticmethod
    def update_your_model(db: Session, model_id: int, data: YourModelUpdate) -> Optional[YourModel]:
        """Update a record."""
        try:
            model = YourService.get_your_model(db, model_id)
            if not model:
                return None
            
            update_data = data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(model, field, value)
            
            db.commit()
            db.refresh(model)
            return model
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating your model: {e}")
            raise HTTPException(status_code=500, detail="Failed to update record")
    
    @staticmethod
    def delete_your_model(db: Session, model_id: int) -> bool:
        """Delete a record."""
        try:
            model = YourService.get_your_model(db, model_id)
            if not model:
                return False
            
            db.delete(model)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting your model: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete record")
```

### **5. Create Router/API Endpoints**
```bash
# Location: app/api/routes/v1/your_router.py
```

**Example:**
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.core.your_service import YourService
from app.domain.your_schemas import (
    YourModelCreate,
    YourModelUpdate,
    YourModelResponse
)
from app.core.dependencies import get_current_active_user, require_permission
from app.core.exceptions import NotFoundException
from app.domain.rbac_models import User

router = APIRouter(prefix="/your-models", tags=["your-models"])

@router.post("/", response_model=YourModelResponse, status_code=status.HTTP_201_CREATED)
async def create_your_model(
    data: YourModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("your_model:create"))
):
    """Create a new record."""
    try:
        result = YourService.create_your_model(db, data, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=Dict[str, Any])
async def get_your_models(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("your_model:read"))
):
    """Get records with pagination and filtering."""
    try:
        skip = (page - 1) * size
        result = YourService.get_your_models(db, skip, size, search)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{model_id}", response_model=YourModelResponse)
async def get_your_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("your_model:read"))
):
    """Get a specific record by ID."""
    try:
        model = YourService.get_your_model(db, model_id)
        if not model:
            raise NotFoundException("YourModel", model_id)
        return model
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{model_id}", response_model=YourModelResponse)
async def update_your_model(
    model_id: int,
    data: YourModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("your_model:update"))
):
    """Update a record."""
    try:
        model = YourService.update_your_model(db, model_id, data)
        if not model:
            raise NotFoundException("YourModel", model_id)
        return model
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_your_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("your_model:delete"))
):
    """Delete a record."""
    try:
        success = YourService.delete_your_model(db, model_id)
        if not success:
            raise NotFoundException("YourModel", model_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

### **6. Register Router in v1 __init__.py**
```bash
# Location: app/api/routes/v1/__init__.py
```

**Add to the file:**
```python
from app.api.routes.v1.your_router import router as your_router

# Add to v1_routers list
v1_routers = [
    # ... existing routers
    your_router,
]
```

### **7. Add RBAC Permissions** (if needed)
```bash
# Location: app/core/rbac_service.py
```

**Add to initialize_default_data method:**
```python
# Add permissions for your new API
("read", "your_model", "View your model data"),
("create", "your_model", "Create your model data"),
("update", "your_model", "Update your model data"),
("delete", "your_model", "Delete your model data"),
```

### **8. Create Tests**
```bash
# Location: tests/test_your_api.py
```

**Example:**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.infrastructure.database import get_db

client = TestClient(app)

def test_create_your_model():
    """Test creating a new record."""
    response = client.post(
        "/api/v1/your-models/",
        json={
            "name": "Test Model",
            "description": "Test Description"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Model"

def test_get_your_models():
    """Test getting records."""
    response = client.get("/api/v1/your-models/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
```

## 📁 **File Structure Template**

```
app/
├── domain/
│   ├── your_model.py          # SQLAlchemy models
│   └── your_schemas.py        # Pydantic schemas
├── core/
│   └── your_service.py        # Business logic
├── api/routes/v1/
│   └── your_router.py         # API endpoints
└── infrastructure/
    └── database.py            # Database connection

tests/
├── test_your_api.py           # API tests
├── test_your_service.py       # Service tests
└── conftest.py                # Test configuration
```

## 🔧 **Quick Start Commands**

```bash
# 1. Create model file
touch app/domain/your_model.py

# 2. Create schemas file
touch app/domain/your_schemas.py

# 3. Create service file
touch app/core/your_service.py

# 4. Create router file
touch app/api/routes/v1/your_router.py

# 5. Create test file
touch tests/test_your_api.py

# 6. Restart application
docker compose restart fastapi
```

## ✅ **Checklist**

- [ ] Domain model created
- [ ] Schemas defined (Create, Update, Response)
- [ ] Service layer implemented
- [ ] Router endpoints created
- [ ] Router registered in v1 __init__.py
- [ ] RBAC permissions added (if needed)
- [ ] Tests written
- [ ] Application restarted
- [ ] API tested via /docs

## 🎯 **Best Practices**

1. **Follow Naming Conventions**: Use consistent naming across models, services, and routers
2. **Error Handling**: Always include proper error handling and logging
3. **Validation**: Use Pydantic for request/response validation
4. **Permissions**: Implement RBAC for sensitive operations
5. **Testing**: Write comprehensive tests for all endpoints
6. **Documentation**: Add docstrings to all functions and classes
7. **Logging**: Include proper logging for debugging and monitoring 