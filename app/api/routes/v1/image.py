import os
import io
import mimetypes
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from minio.error import S3Error
from app.services.minio_service import minio_service
from app.core.auth import get_current_user
from app.domain.rbac_models import User

router = APIRouter(prefix="/image", tags=["image"])

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "customer-images")
MINIO_EXTERNAL_HOST = os.getenv("MINIO_EXTERNAL_HOST", "http://localhost:9002")

def generate_file_path(original_filename: str) -> str:
    """Generates a file path with a date-based folder and timestamped filename."""
    now = datetime.now()
    folder_name = now.strftime("%Y%m%d")
    timestamp = now.strftime("%Y%m%d%H%M%S")
    file_extension = os.path.splitext(original_filename)[1] if original_filename else ""
    return f"{folder_name}/{timestamp}{file_extension}"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return a previewable link."""
    try:
        file_data = await file.read()
        file_size = len(file_data)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        new_filename = generate_file_path(file.filename)
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        minio_service.client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=new_filename,
            data=io.BytesIO(file_data),
            length=file_size,
            content_type=content_type
        )

        file_url = f"{MINIO_EXTERNAL_HOST}/{BUCKET_NAME}/{new_filename}"
        return {
            "message": "Upload successful",
            "original_filename": file.filename,
            "full_path": new_filename,
            "size": file_size,
            "content_type": content_type,
            "url": file_url
        }
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/list")
async def list_files():
    """List all uploaded files."""
    try:
        objects = minio_service.client.list_objects(BUCKET_NAME, recursive=True)
        files = []
        for obj in objects:
            files.append({
                "name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                "url": f"{MINIO_EXTERNAL_HOST}/{BUCKET_NAME}/{obj.object_name}"
            })
        return {"files": files}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.delete("/{file_path:path}")
async def delete_file(file_path: str):
    """Delete a file by its path."""
    try:
        minio_service.client.remove_object(BUCKET_NAME, file_path)
        return {"message": "File deleted successfully"}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.post("/make-bucket-public")
async def make_bucket_public():
    """Make the bucket public for read access."""
    try:
        success = minio_service.make_bucket_public()
        if success:
            return {"message": "Bucket made public successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to make bucket public")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to make bucket public: {str(e)}") 