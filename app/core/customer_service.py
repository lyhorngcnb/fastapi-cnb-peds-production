from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, UploadFile
from app.domain.customer import Customer, GenderEnum
from app.domain.customer_schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core.minio_service import minio_service
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    
    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate, created_by: int) -> Customer:
        """Create a new customer."""
        try:
            # Check if customer with same national_id already exists
            existing_customer = db.query(Customer).filter(
                Customer.national_id == customer_data.national_id
            ).first()
            
            if existing_customer:
                raise HTTPException(
                    status_code=400,
                    detail=f"Customer with national ID {customer_data.national_id} already exists"
                )
            
            # Create new customer
            gender_enum = None
            if customer_data.gender:
                gender_enum = GenderEnum(customer_data.gender)
            
            db_customer = Customer(
                first_name=customer_data.first_name,
                last_name=customer_data.last_name,
                national_id=customer_data.national_id,
                gender=gender_enum,
                date_of_birth=customer_data.date_of_birth,
                phone_number=customer_data.phone_number,
                email=customer_data.email,
                photo_url=customer_data.photo_url,
                address=customer_data.address,
                created_by=created_by
            )
            
            db.add(db_customer)
            db.commit()
            db.refresh(db_customer)
            
            # Convert enum to string for response
            if db_customer.gender:
                db_customer.gender = db_customer.gender.value
            
            return db_customer
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating customer: {e}")
            raise HTTPException(status_code=500, detail="Failed to create customer")

    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Convert enum to string for response
        if customer.gender:
            customer.gender = customer.gender.value
        
        return customer

    @staticmethod
    def get_customer_by_national_id(db: Session, national_id: str) -> Optional[Customer]:
        """Get a customer by national ID."""
        customer = db.query(Customer).filter(Customer.national_id == national_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    @staticmethod
    def get_customers(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Customer], int]:
        """Get customers with pagination and search."""
        query = db.query(Customer)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        
        if search:
            search_filter = or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.national_id.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        customers = query.offset(skip).limit(limit).all()
        
        # Convert enums to strings for response
        for customer in customers:
            if customer.gender:
                customer.gender = customer.gender.value
        
        return customers, total

    @staticmethod
    def update_customer(db: Session, customer_id: int, customer_data: CustomerUpdate) -> Customer:
        """Update a customer."""
        try:
            customer = CustomerService.get_customer(db, customer_id)
            
            # Check if national_id is being updated and if it already exists
            if customer_data.national_id and customer_data.national_id != customer.national_id:
                existing_customer = db.query(Customer).filter(
                    and_(
                        Customer.national_id == customer_data.national_id,
                        Customer.id != customer_id
                    )
                ).first()
                
                if existing_customer:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Customer with national ID {customer_data.national_id} already exists"
                    )
            
            # Update fields
            update_data = customer_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == 'gender' and value:
                    setattr(customer, field, GenderEnum(value))
                else:
                    setattr(customer, field, value)
            
            db.commit()
            db.refresh(customer)
            
            # Convert enum to string for response
            if customer.gender:
                customer.gender = customer.gender.value
            
            return customer
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating customer: {e}")
            raise HTTPException(status_code=500, detail="Failed to update customer")

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        """Soft delete a customer (set is_active to False)."""
        try:
            customer = CustomerService.get_customer(db, customer_id)
            customer.is_active = False
            db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting customer: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete customer")

    @staticmethod
    def upload_customer_image(
        db: Session, 
        customer_id: int, 
        file: UploadFile, 
        image_type: str
    ) -> dict:
        """Upload an image for a customer using the same approach as /api/v1/image/upload."""
        try:
            import os
            import io
            import mimetypes
            from datetime import datetime
            from minio.error import S3Error
            
            customer = CustomerService.get_customer(db, customer_id)
            
            # Validate image type
            valid_types = ["photo", "nid_front", "nid_back"]
            if image_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image type. Must be one of: {', '.join(valid_types)}"
                )
            
            # Validate file type
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="File must be an image"
                )
            
            # Read file data
            file_data = file.file.read()
            file_size = len(file_data)
            if file_size == 0:
                raise HTTPException(status_code=400, detail="Empty file")
            
            # Generate file path using the same approach as image upload
            now = datetime.now()
            folder_name = now.strftime("%Y%m%d")
            timestamp = now.strftime("%Y%m%d%H%M%S")
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            new_filename = f"customers/{customer_id}/{image_type}/{folder_name}/{timestamp}{file_extension}"
            
            # Get content type
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
            
            # Upload to MinIO using the same approach as image upload
            minio_service.client.put_object(
                bucket_name=minio_service.bucket_name,
                object_name=new_filename,
                data=io.BytesIO(file_data),
                length=file_size,
                content_type=content_type
            )
            
            # Generate URL using the same format as image upload
            minio_external_host = os.getenv("MINIO_EXTERNAL_HOST", "http://localhost:9002")
            file_url = f"{minio_external_host}/{minio_service.bucket_name}/{new_filename}"
            
            # Update customer record
            if image_type == "photo":
                customer.photo_url = new_filename
            elif image_type == "nid_front":
                customer.nid_front_url = new_filename
            elif image_type == "nid_back":
                customer.nid_back_url = new_filename
            
            db.commit()
            
            return {
                "file_url": file_url,
                "file_name": new_filename,
                "file_size": file_size,
                "content_type": content_type,
                "original_name": file.filename
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error uploading customer image: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload image")

    @staticmethod
    def delete_customer_image(
        db: Session, 
        customer_id: int, 
        image_type: str
    ) -> bool:
        """Delete an image for a customer using the same approach as /api/v1/image/upload."""
        try:
            from minio.error import S3Error
            
            customer = CustomerService.get_customer(db, customer_id)
            
            # Validate image type
            valid_types = ["photo", "nid_front", "nid_back"]
            if image_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image type. Must be one of: {', '.join(valid_types)}"
                )
            
            # Get current file name
            current_file = None
            if image_type == "photo":
                current_file = customer.photo_url
                customer.photo_url = None
            elif image_type == "nid_front":
                current_file = customer.nid_front_url
                customer.nid_front_url = None
            elif image_type == "nid_back":
                current_file = customer.nid_back_url
                customer.nid_back_url = None
            
            # Delete from MinIO if exists using the same approach as image upload
            if current_file:
                try:
                    minio_service.client.remove_object(minio_service.bucket_name, current_file)
                except S3Error as e:
                    logger.warning(f"File not found in MinIO: {current_file}, error: {e}")
            
            db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting customer image: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete image") 