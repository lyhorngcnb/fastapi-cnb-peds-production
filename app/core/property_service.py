from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException
from app.domain.property_models import Property, LandDetail, BuildingDetail, GoogleMap, Document
from app.domain.location_models import Province, District, Commune, Village
from app.domain.customer import Customer
from app.domain.loan_request import LoanRequest
from app.domain.property_schemas import (
    PropertyCreate, PropertyUpdate, PropertyResponse,
    LandDetailCreate, LandDetailUpdate, LandDetailResponse,
    BuildingDetailCreate, BuildingDetailUpdate, BuildingDetailResponse,
    GoogleMapCreate, GoogleMapUpdate, GoogleMapResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse
)
from app.core.property_code_generator import PropertyCodeGenerator
import logging

logger = logging.getLogger(__name__)

class PropertyService:
    
    @staticmethod
    def create_property(db: Session, property_data: PropertyCreate, created_by: int) -> Property:
        """Create a new property with all its details."""
        try:
            # Validate loan request exists
            loan_request = db.query(LoanRequest).filter(LoanRequest.id == property_data.requester_id).first()
            if not loan_request:
                raise HTTPException(
                    status_code=404,
                    detail=f"Loan request with ID {property_data.requester_id} not found"
                )
            
            # Validate owner 1 exists
            owner_1 = db.query(Customer).filter(Customer.id == property_data.owner_1_id).first()
            if not owner_1:
                raise HTTPException(
                    status_code=404,
                    detail=f"Owner 1 (Customer) with ID {property_data.owner_1_id} not found"
                )
            
            # Validate owner 2 if provided
            if property_data.owner_2_id:
                owner_2 = db.query(Customer).filter(Customer.id == property_data.owner_2_id).first()
                if not owner_2:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Owner 2 (Customer) with ID {property_data.owner_2_id} not found"
                    )
            
            # Validate old property if provided
            if property_data.old_property_id:
                old_property = db.query(Property).filter(Property.id == property_data.old_property_id).first()
                if not old_property:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Old property with ID {property_data.old_property_id} not found"
                    )
            
            # Validate location references
            if property_data.province_id:
                province = db.query(Province).filter(Province.id == property_data.province_id).first()
                if not province:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Province with ID {property_data.province_id} not found"
                    )
            
            if property_data.district_id:
                district = db.query(District).filter(District.id == property_data.district_id).first()
                if not district:
                    raise HTTPException(
                        status_code=404,
                        detail=f"District with ID {property_data.district_id} not found"
                    )
            
            if property_data.commune_id:
                commune = db.query(Commune).filter(Commune.id == property_data.commune_id).first()
                if not commune:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Commune with ID {property_data.commune_id} not found"
                    )
            
            if property_data.village_id:
                village = db.query(Village).filter(Village.id == property_data.village_id).first()
                if not village:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Village with ID {property_data.village_id} not found"
                    )
            
            # Generate property code
            property_code = PropertyCodeGenerator.generate_property_code(db)
            
            # Create property
            db_property = Property(
                property_code=property_code,
                requester_id=property_data.requester_id,
                old_property_id=property_data.old_property_id,
                ownership_title=property_data.ownership_title,
                owner_1_id=property_data.owner_1_id,
                owner_2_id=property_data.owner_2_id,
                type_of_title=property_data.type_of_title,
                title_number=property_data.title_number,
                type_of_property=property_data.type_of_property,
                information_property=property_data.information_property,
                province_id=property_data.province_id,
                district_id=property_data.district_id,
                commune_id=property_data.commune_id,
                village_id=property_data.village_id,
                measurement_info=property_data.measurement_info,
                remark=property_data.remark,
                created_by=created_by
            )
            
            db.add(db_property)
            db.flush()  # Get the ID without committing
            
            # Create land details
            for land_detail_data in property_data.land_details or []:
                land_detail = LandDetail(
                    property_id=db_property.id,
                    land_size=land_detail_data.land_size,
                    front=land_detail_data.front,
                    back=land_detail_data.back,
                    length=land_detail_data.length,
                    width=land_detail_data.width,
                    flat_unit_type=land_detail_data.flat_unit_type,
                    number_of_lot=land_detail_data.number_of_lot
                )
                db.add(land_detail)
            
            # Create building details
            for building_detail_data in property_data.building_details or []:
                building_detail = BuildingDetail(
                    property_id=db_property.id,
                    source_type=building_detail_data.source_type,
                    agency_name=building_detail_data.agency_name,
                    description=building_detail_data.description,
                    total_building_area=building_detail_data.total_building_area,
                    building_width=building_detail_data.building_width,
                    building_length=building_detail_data.building_length,
                    number_of_floors=building_detail_data.number_of_floors,
                    estimated_size=building_detail_data.estimated_size,
                    remark=building_detail_data.remark
                )
                db.add(building_detail)
            
            # Create google maps
            for google_map_data in property_data.google_maps or []:
                google_map = GoogleMap(
                    property_id=db_property.id,
                    map_coordinates=google_map_data.map_coordinates,
                    map_color=google_map_data.map_color
                )
                db.add(google_map)
            
            # Create documents
            for document_data in property_data.documents or []:
                document = Document(
                    property_id=db_property.id,
                    file_url=document_data.file_url,
                    file_type=document_data.file_type,
                    title=document_data.title,
                    uploaded_by=created_by
                )
                db.add(document)
            
            db.commit()
            db.refresh(db_property)
            
            return db_property
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating property: {e}")
            raise HTTPException(status_code=500, detail="Failed to create property")

    @staticmethod
    def get_property(db: Session, property_id: int) -> Optional[Property]:
        """Get a property by ID."""
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_obj

    @staticmethod
    def get_properties(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        property_code: Optional[str] = None,
        type_of_property: Optional[str] = None,
        ownership_title: Optional[str] = None,
        requester_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        province_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Property], int]:
        """Get properties with pagination and filters."""
        query = db.query(Property)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Property.is_active == is_active)
        
        if property_code:
            query = query.filter(Property.property_code.ilike(f"%{property_code}%"))
        
        if type_of_property:
            query = query.filter(Property.type_of_property.ilike(f"%{type_of_property}%"))
        
        if ownership_title:
            query = query.filter(Property.ownership_title.ilike(f"%{ownership_title}%"))
        
        if requester_id:
            query = query.filter(Property.requester_id == requester_id)
        
        if owner_id:
            query = query.filter(
                or_(
                    Property.owner_1_id == owner_id,
                    Property.owner_2_id == owner_id
                )
            )
        
        if province_id:
            query = query.filter(Property.province_id == province_id)
        
        if search:
            # Search in property code, title number, information property
            search_filter = or_(
                Property.property_code.ilike(f"%{search}%"),
                Property.title_number.ilike(f"%{search}%"),
                Property.information_property.ilike(f"%{search}%"),
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.national_id.ilike(f"%{search}%")
            )
            query = query.join(Customer, or_(
                Property.owner_1_id == Customer.id,
                Property.owner_2_id == Customer.id
            )).filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        properties = query.offset(skip).limit(limit).all()
        
        return properties, total

    @staticmethod
    def update_property(db: Session, property_id: int, property_data: PropertyUpdate) -> Property:
        """Update a property."""
        try:
            property_obj = PropertyService.get_property(db, property_id)
            
            # Validate references if being updated
            if property_data.owner_1_id and property_data.owner_1_id != property_obj.owner_1_id:
                owner_1 = db.query(Customer).filter(Customer.id == property_data.owner_1_id).first()
                if not owner_1:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Owner 1 (Customer) with ID {property_data.owner_1_id} not found"
                    )
            
            if property_data.owner_2_id and property_data.owner_2_id != property_obj.owner_2_id:
                owner_2 = db.query(Customer).filter(Customer.id == property_data.owner_2_id).first()
                if not owner_2:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Owner 2 (Customer) with ID {property_data.owner_2_id} not found"
                    )
            
            # Update fields
            update_data = property_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(property_obj, field, value)
            
            db.commit()
            db.refresh(property_obj)
            
            return property_obj
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating property: {e}")
            raise HTTPException(status_code=500, detail="Failed to update property")

    @staticmethod
    def delete_property(db: Session, property_id: int) -> bool:
        """Soft delete a property (set is_active to False)."""
        try:
            property_obj = PropertyService.get_property(db, property_id)
            property_obj.is_active = False
            db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting property: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete property")

    # Land Detail methods
    @staticmethod
    def create_land_detail(db: Session, property_id: int, land_detail_data: LandDetailCreate) -> LandDetail:
        """Create a land detail for a property."""
        try:
            # Validate property exists
            property_obj = PropertyService.get_property(db, property_id)
            
            land_detail = LandDetail(
                property_id=property_id,
                land_size=land_detail_data.land_size,
                front=land_detail_data.front,
                back=land_detail_data.back,
                length=land_detail_data.length,
                width=land_detail_data.width,
                flat_unit_type=land_detail_data.flat_unit_type,
                number_of_lot=land_detail_data.number_of_lot
            )
            
            db.add(land_detail)
            db.commit()
            db.refresh(land_detail)
            
            return land_detail
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating land detail: {e}")
            raise HTTPException(status_code=500, detail="Failed to create land detail")

    @staticmethod
    def update_land_detail(db: Session, land_detail_id: int, land_detail_data: LandDetailUpdate) -> LandDetail:
        """Update a land detail."""
        try:
            land_detail = db.query(LandDetail).filter(LandDetail.id == land_detail_id).first()
            if not land_detail:
                raise HTTPException(status_code=404, detail="Land detail not found")
            
            update_data = land_detail_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(land_detail, field, value)
            
            db.commit()
            db.refresh(land_detail)
            
            return land_detail
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating land detail: {e}")
            raise HTTPException(status_code=500, detail="Failed to update land detail")

    # Building Detail methods
    @staticmethod
    def create_building_detail(db: Session, property_id: int, building_detail_data: BuildingDetailCreate) -> BuildingDetail:
        """Create a building detail for a property."""
        try:
            # Validate property exists
            property_obj = PropertyService.get_property(db, property_id)
            
            building_detail = BuildingDetail(
                property_id=property_id,
                source_type=building_detail_data.source_type,
                agency_name=building_detail_data.agency_name,
                description=building_detail_data.description,
                total_building_area=building_detail_data.total_building_area,
                building_width=building_detail_data.building_width,
                building_length=building_detail_data.building_length,
                number_of_floors=building_detail_data.number_of_floors,
                estimated_size=building_detail_data.estimated_size,
                remark=building_detail_data.remark
            )
            
            db.add(building_detail)
            db.commit()
            db.refresh(building_detail)
            
            return building_detail
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating building detail: {e}")
            raise HTTPException(status_code=500, detail="Failed to create building detail")

    @staticmethod
    def update_building_detail(db: Session, building_detail_id: int, building_detail_data: BuildingDetailUpdate) -> BuildingDetail:
        """Update a building detail."""
        try:
            building_detail = db.query(BuildingDetail).filter(BuildingDetail.id == building_detail_id).first()
            if not building_detail:
                raise HTTPException(status_code=404, detail="Building detail not found")
            
            update_data = building_detail_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(building_detail, field, value)
            
            db.commit()
            db.refresh(building_detail)
            
            return building_detail
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating building detail: {e}")
            raise HTTPException(status_code=500, detail="Failed to update building detail")

    # Document methods
    @staticmethod
    def create_document(db: Session, property_id: int, document_data: DocumentCreate, uploaded_by: int) -> Document:
        """Create a document for a property."""
        try:
            # Validate property exists
            property_obj = PropertyService.get_property(db, property_id)
            
            document = Document(
                property_id=property_id,
                file_url=document_data.file_url,
                file_type=document_data.file_type,
                title=document_data.title,
                uploaded_by=uploaded_by
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            return document
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating document: {e}")
            raise HTTPException(status_code=500, detail="Failed to create document")

    @staticmethod
    def get_property_statistics(db: Session) -> dict:
        """Get property evaluation statistics."""
        try:
            # Total properties
            total_properties = db.query(Property).filter(Property.is_active == True).count()
            
            # Total by property type
            property_type_stats = db.query(
                Property.type_of_property,
                func.count(Property.id).label('count')
            ).filter(Property.is_active == True).group_by(Property.type_of_property).all()
            
            # Total by ownership title
            ownership_stats = db.query(
                Property.ownership_title,
                func.count(Property.id).label('count')
            ).filter(Property.is_active == True).group_by(Property.ownership_title).all()
            
            # Total by measurement info
            measurement_stats = db.query(
                Property.measurement_info,
                func.count(Property.id).label('count')
            ).filter(Property.is_active == True).group_by(Property.measurement_info).all()
            
            return {
                'total_properties': total_properties,
                'by_property_type': {stat.type_of_property.value: stat.count for stat in property_type_stats if stat.type_of_property},
                'by_ownership_title': {stat.ownership_title.value: stat.count for stat in ownership_stats},
                'by_measurement_info': {stat.measurement_info.value: stat.count for stat in measurement_stats if stat.measurement_info}
            }
            
        except Exception as e:
            logger.error(f"Error getting property statistics: {e}")
            raise HTTPException(status_code=500, detail="Failed to get statistics") 