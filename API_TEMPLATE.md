# 🚀 Quick API Implementation Template

## **Step-by-Step Checklist**

### **1. Create Domain Model** ✅
```bash
# Create: app/domain/your_model.py
```
```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.domain.rbac_models import Base

class YourModel(Base):
    __tablename__ = "your_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### **2. Create Schemas** ✅
```bash
# Create: app/domain/your_schemas.py
```
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class YourModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class YourModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class YourModelResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
```

### **3. Create Service** ✅
```bash
# Create: app/core/your_service.py
```
```python
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.domain.your_model import YourModel
from app.domain.your_schemas import YourModelCreate, YourModelUpdate
import logging

logger = logging.getLogger(__name__)

class YourService:
    @staticmethod
    def create_your_model(db: Session, data: YourModelCreate, user_id: int) -> YourModel:
        try:
            your_model = YourModel(name=data.name)
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
        return db.query(YourModel).filter(YourModel.id == model_id).first()
    
    @staticmethod
    def get_your_models(db: Session, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        query = db.query(YourModel)
        total = query.count()
        models = query.offset(skip).limit(limit).all()
        return {"items": models, "total": total, "page": skip // limit + 1, "size": limit}
    
    @staticmethod
    def update_your_model(db: Session, model_id: int, data: YourModelUpdate) -> Optional[YourModel]:
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

### **4. Create Router** ✅
```bash
# Create: app/api/routes/v1/your_router.py
```
```python
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.core.your_service import YourService
from app.domain.your_schemas import YourModelCreate, YourModelUpdate, YourModelResponse
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("your_model:read"))
):
    """Get records with pagination."""
    try:
        skip = (page - 1) * size
        result = YourService.get_your_models(db, skip, size)
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

### **5. Register Router** ✅
```bash
# Edit: app/api/routes/v1/__init__.py
```
```python
from app.api.routes.v1.your_router import router as your_router

# Add to v1_routers list
v1_routers = [
    # ... existing routers
    your_router,
]
```

### **6. Add RBAC Permissions** ✅
```bash
# Edit: app/core/rbac_service.py
# Add to initialize_default_data method:
```
```python
# Add permissions for your new API
("read", "your_model", "View your model data"),
("create", "your_model", "Create your model data"),
("update", "your_model", "Update your model data"),
("delete", "your_model", "Delete your model data"),
```

### **7. Create Tests** ✅
```bash
# Create: tests/test_your_api.py
```
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_your_model():
    """Test creating a new record."""
    response = client.post(
        "/api/v1/your-models/",
        json={"name": "Test Model"}
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

### **8. Restart Application** ✅
```bash
docker compose restart fastapi
```

### **9. Test API** ✅
```bash
# Check health
curl http://localhost:8080/health

# Test your new API
curl http://localhost:8080/docs
```

## **Quick Commands**

```bash
# Create all files at once
touch app/domain/your_model.py
touch app/domain/your_schemas.py
touch app/core/your_service.py
touch app/api/routes/v1/your_router.py
touch tests/test_your_api.py

# Restart and test
docker compose restart fastapi
curl http://localhost:8080/health
```

## **File Structure**
```
app/
├── domain/
│   ├── your_model.py          # ✅ SQLAlchemy model
│   └── your_schemas.py        # ✅ Pydantic schemas
├── core/
│   └── your_service.py        # ✅ Business logic
└── api/routes/v1/
    └── your_router.py         # ✅ API endpoints

tests/
└── test_your_api.py           # ✅ Tests
```

## **API Endpoints Created**
- `POST /api/v1/your-models/` - Create
- `GET /api/v1/your-models/` - List with pagination
- `GET /api/v1/your-models/{id}` - Get by ID
- `PUT /api/v1/your-models/{id}` - Update
- `DELETE /api/v1/your-models/{id}` - Delete

## **Next Steps**
1. Customize the model fields
2. Add validation rules
3. Implement business logic
4. Add more endpoints if needed
5. Write comprehensive tests
6. Add documentation 