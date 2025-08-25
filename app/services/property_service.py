from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.domain.property_models import Property
from app.schemas.property import PropertyCreateSchema, PropertyUpdateSchema, PropertyResponseSchema
from app.core.exceptions import NotFoundException, ValidationException

class PropertyService:
    """Service for property-related business logic."""
    
    def __init__(self):
        pass
    
    def create_property(self, db: Session, property_data: PropertyCreateSchema, user_id: int) -> PropertyResponseSchema:
        """Create a new property."""
        # This is a placeholder implementation
        # In a real application, you would map the schema to the Property model
        raise NotImplementedError("Property creation not yet implemented")
    
    def get_property(self, db: Session, property_id: int) -> Optional[PropertyResponseSchema]:
        """Get a property by ID."""
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return None
        # Convert to response schema
        return PropertyResponseSchema(
            id=property_obj.id,
            title=f"Property {property_obj.property_code}",
            property_type=property_obj.type_of_property.value if property_obj.type_of_property else "Unknown",
            address="Address placeholder",
            province_id=property_obj.province_id or 0,
            district_id=property_obj.district_id or 0,
            commune_id=property_obj.commune_id,
            village_id=property_obj.village_id,
            area=0,  # Placeholder
            currency="USD",
            created_at=property_obj.created_at,
            updated_at=property_obj.updated_at
        )
    
    def get_properties_with_filters(
        self, 
        db: Session, 
        page: int, 
        size: int, 
        search: Optional[str] = None,
        property_type: Optional[str] = None,
        province_id: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get properties with pagination and filtering."""
        query = db.query(Property)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Property.property_code.contains(search),
                    Property.information_property.contains(search)
                )
            )
        
        if property_type:
            query = query.filter(Property.type_of_property == property_type)
        
        if province_id:
            query = query.filter(Property.province_id == province_id)
        
        if district_id:
            query = query.filter(Property.district_id == district_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        properties = query.offset((page - 1) * size).limit(size).all()
        
        # Convert to response schemas
        property_list = []
        for prop in properties:
            property_list.append(PropertyResponseSchema(
                id=prop.id,
                title=f"Property {prop.property_code}",
                property_type=prop.type_of_property.value if prop.type_of_property else "Unknown",
                address="Address placeholder",
                province_id=prop.province_id or 0,
                district_id=prop.district_id or 0,
                commune_id=prop.commune_id,
                village_id=prop.village_id,
                area=0,  # Placeholder
                currency="USD",
                created_at=prop.created_at,
                updated_at=prop.updated_at
            ))
        
        return {
            "properties": property_list,
            "total": total,
            "page": page,
            "size": size
        }
    
    def update_property(self, db: Session, property_id: int, property_data: PropertyUpdateSchema) -> Optional[PropertyResponseSchema]:
        """Update a property."""
        # This is a placeholder implementation
        raise NotImplementedError("Property update not yet implemented")
    
    def delete_property(self, db: Session, property_id: int) -> bool:
        """Delete a property."""
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return False
        
        db.delete(property_obj)
        db.commit()
        return True 