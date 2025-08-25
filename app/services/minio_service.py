import os
from typing import Optional
from minio import Minio
from minio.error import S3Error
import uuid
from datetime import timedelta
from fastapi import HTTPException, UploadFile
import logging

logger = logging.getLogger(__name__)

class MinioService:
    def __init__(self):
        self.minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "customer-images")
        self.secure = False  # Set to True if using HTTPS
        
        try:
            self.client = Minio(
                self.minio_endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise HTTPException(status_code=500, detail="Storage service unavailable")

    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize storage")

    def upload_file(self, file: UploadFile, folder: str = "general") -> dict:
        """
        Upload a file to MinIO and return file information.
        
        Args:
            file: FastAPI UploadFile object
            folder: Folder within the bucket to store the file
            
        Returns:
            dict: File information including URL, name, size, etc.
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
            unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
            
            # Read file data
            file_data = file.file.read()
            file_size = len(file_data)
            
            # Reset file pointer for upload
            file.file.seek(0)
            
            # Upload file using BytesIO
            from io import BytesIO
            file_stream = BytesIO(file_data)
            
            self.client.put_object(
                self.bucket_name,
                unique_filename,
                file_stream,
                file_size,
                content_type=file.content_type
            )
            
            # Generate presigned URL for access (valid for 7 days)
            file_url = self.client.presigned_get_object(
                self.bucket_name,
                unique_filename,
                expires=timedelta(days=7)
            )
            
            return {
                "file_url": file_url,
                "file_name": unique_filename,
                "file_size": file_size,
                "content_type": file.content_type,
                "original_name": file.filename
            }
            
        except S3Error as e:
            logger.error(f"MinIO upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(status_code=500, detail="Upload failed")

    def delete_file(self, file_name: str) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            file_name: Name of the file to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            self.client.remove_object(self.bucket_name, file_name)
            return True
        except S3Error as e:
            logger.error(f"MinIO delete error: {e}")
            return False

    def get_file_url(self, file_name: str, expires: int = 604800) -> Optional[str]:
        """
        Generate a presigned URL for a file.
        
        Args:
            file_name: Name of the file
            expires: Expiration time in seconds (default: 7 days)
            
        Returns:
            str: Presigned URL or None if file doesn't exist
        """
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                file_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None

    def file_exists(self, file_name: str) -> bool:
        """
        Check if a file exists in the bucket.
        
        Args:
            file_name: Name of the file to check
            
        Returns:
            bool: True if file exists
        """
        try:
            self.client.stat_object(self.bucket_name, file_name)
            return True
        except S3Error:
            return False

    def make_bucket_public(self) -> bool:
        """Configure bucket policy to allow public read access to objects."""
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ],
            }
            import json
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
            return True
        except Exception as e:
            logger.error(f"Failed to set bucket policy: {e}")
            return False

# Global instance
minio_service = MinioService() 