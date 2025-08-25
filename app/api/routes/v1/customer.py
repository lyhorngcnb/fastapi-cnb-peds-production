from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.customer_service import CustomerService
from app.domain.customer_schemas import (
	CustomerCreate, 
	CustomerUpdate, 
	CustomerResponse, 
	CustomerListResponse,
	ImageUploadResponse
)
from app.core.auth import get_current_user
from app.domain.rbac_models import User

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(
	customer_data: CustomerCreate,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Create a new customer.
	
	- **first_name**: Customer's first name (required)
	- **last_name**: Customer's last name (required)
	- **national_id**: Unique national ID (required)
	- **gender**: Gender (optional: Male, Female, Other)
	- **date_of_birth**: Date of birth (optional)
	- **phone_number**: Phone number (optional)
	- **email**: Email address (optional)
	- **address**: Address (optional)
	"""
	return CustomerService.create_customer(db, customer_data, current_user.id)

@router.get("/", response_model=CustomerListResponse)
def get_customers(
	skip: int = Query(0, ge=0, description="Number of records to skip"),
	limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
	search: Optional[str] = Query(None, description="Search term for name, national ID, email, or phone"),
	is_active: Optional[bool] = Query(None, description="Filter by active status"),
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Get customers with pagination and search.
	
	- **skip**: Number of records to skip for pagination
	- **limit**: Number of records to return (max 1000)
	- **search**: Search term for name, national ID, email, or phone
	- **is_active**: Filter by active status
	"""
	customers, total = CustomerService.get_customers(
		db, skip=skip, limit=limit, search=search, is_active=is_active
	)
	
	return CustomerListResponse(
		customers=customers,
		total=total,
		page=skip // limit + 1,
		size=limit
	)

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
	customer_id: int,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Get a customer by ID.
	
	- **customer_id**: Customer's unique identifier
	"""
	return CustomerService.get_customer(db, customer_id)

@router.get("/national-id/{national_id}", response_model=CustomerResponse)
def get_customer_by_national_id(
	national_id: str,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Get a customer by national ID.
	
	- **national_id**: Customer's national ID
	"""
	return CustomerService.get_customer_by_national_id(db, national_id)

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
	customer_id: int,
	customer_data: CustomerUpdate,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Update a customer.
	
	- **customer_id**: Customer's unique identifier
	- **customer_data**: Customer data to update (all fields optional)
	"""
	return CustomerService.update_customer(db, customer_id, customer_data)

@router.put("/{customer_id}/photo", response_model=CustomerResponse)
def update_customer_photo(
	customer_id: int,
	file: UploadFile = File(...),
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Update the customer's profile photo. This uploads the image to storage and updates `photo_url`.
	
	- **customer_id**: Customer's unique identifier
	- **file**: Image file to upload as profile photo
	"""
	CustomerService.upload_customer_image(db, customer_id, file, image_type="photo")
	return CustomerService.get_customer(db, customer_id)

@router.delete("/{customer_id}", status_code=204)
def delete_customer(
	customer_id: int,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Soft delete a customer (set is_active to False).
	
	- **customer_id**: Customer's unique identifier
	"""
	CustomerService.delete_customer(db, customer_id)
	return {"message": "Customer deleted successfully"}

@router.post("/{customer_id}/images/{image_type}", response_model=ImageUploadResponse)
def upload_customer_image(
	customer_id: int,
	image_type: str,
	file: UploadFile = File(...),
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Upload an image for a customer.
	
	- **customer_id**: Customer's unique identifier
	- **image_type**: Type of image (photo, nid_front, nid_back)
	- **file**: Image file to upload
	"""
	result = CustomerService.upload_customer_image(db, customer_id, file, image_type)
	return ImageUploadResponse(
		file_url=result["file_url"],
		file_name=result["file_name"],
		file_size=result["file_size"],
		content_type=result["content_type"]
	)

@router.delete("/{customer_id}/images/{image_type}", status_code=204)
def delete_customer_image(
	customer_id: int,
	image_type: str,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Delete an image for a customer.
	
	- **customer_id**: Customer's unique identifier
	- **image_type**: Type of image to delete (photo, nid_front, nid_back)
	"""
	CustomerService.delete_customer_image(db, customer_id, image_type)
	return {"message": "Image deleted successfully"}

@router.get("/{customer_id}/images/{image_type}/url")
def get_customer_image_url(
	customer_id: int,
	image_type: str,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Get a presigned URL for a customer's image.
	
	- **customer_id**: Customer's unique identifier
	- **image_type**: Type of image (photo, nid_front, nid_back)
	"""
	customer = CustomerService.get_customer(db, customer_id)
	
	file_name = None
	if image_type == "photo":
		file_name = customer.photo_url
	elif image_type == "nid_front":
		file_name = customer.nid_front_url
	elif image_type == "nid_back":
		file_name = customer.nid_back_url
	else:
		raise HTTPException(
			status_code=400,
			detail=f"Invalid image type. Must be one of: photo, nid_front, nid_back"
		)
	
	if not file_name:
		raise HTTPException(
			status_code=404,
			detail=f"No {image_type} image found for this customer"
		)
	
	from app.core.minio_service import minio_service
	file_url = minio_service.get_file_url(file_name)
	
	if not file_url:
		raise HTTPException(
			status_code=404,
			detail="Image file not found in storage"
		)
	
	return {"file_url": file_url, "file_name": file_name} 