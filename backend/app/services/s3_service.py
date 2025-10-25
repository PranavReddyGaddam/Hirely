"""
AWS S3 Service for Video Storage
Handles upload, download, and deletion of interview videos from S3
"""
import os
import asyncio
import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class S3Service:
    """Service for interacting with AWS S3 for video storage"""
    
    def __init__(self):
        self.access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        
        if not all([self.access_key_id, self.secret_access_key, self.bucket_name]):
            raise ValueError("AWS credentials not configured. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_S3_BUCKET environment variables.")
        
        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region
        )
        
        logger.info(f"[S3 Service] Initialized for bucket: {self.bucket_name} in region: {self.region}")
    
    async def upload_video(
        self,
        user_id: str,
        interview_id: str,
        video_data: bytes,
        file_extension: str = "webm"
    ) -> Optional[Dict[str, Any]]:
        """
        Upload interview video to S3.
        
        Args:
            user_id: User ID (used for folder organization)
            interview_id: Interview ID
            video_data: Video file bytes
            file_extension: File extension (webm, mp4, etc.)
            
        Returns:
            Dict with s3_key and public_url, or None if failed
        """
        try:
            import time
            timestamp = int(time.time())
            
            # S3 key: user_id/interview_id_timestamp.webm
            s3_key = f"{user_id}/{interview_id}_{timestamp}.{file_extension}"
            
            logger.info(f"[S3] Uploading video: {s3_key}")
            logger.info(f"[S3] Video size: {len(video_data) / 1024 / 1024:.2f} MB")
            
            # Determine content type
            content_type_map = {
                "webm": "video/webm",
                "mp4": "video/mp4",
                "mov": "video/quicktime"
            }
            content_type = content_type_map.get(file_extension, "video/webm")
            
            # Upload to S3 (run in thread to avoid blocking)
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=video_data,
                ContentType=content_type
            )
            
            # Generate presigned URL (valid for 1 year)
            public_url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=31536000  # 1 year
            )
            
            logger.info(f"[S3] ✅ Video uploaded successfully: {s3_key}")
            
            return {
                "storage_path": s3_key,
                "public_url": public_url,
                "size_bytes": len(video_data)
            }
            
        except ClientError as e:
            logger.error(f"[S3] Error uploading video to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"[S3] Unexpected error uploading video: {e}", exc_info=True)
            return None
    
    async def download_video(self, s3_key: str) -> Optional[bytes]:
        """
        Download video from S3.
        
        Args:
            s3_key: S3 key (user_id/interview_id_timestamp.webm)
            
        Returns:
            Video bytes or None if failed
        """
        try:
            logger.info(f"[S3] Downloading video: {s3_key}")
            
            response = await asyncio.to_thread(
                self.s3_client.get_object,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            video_data = await asyncio.to_thread(response['Body'].read)
            logger.info(f"[S3] ✅ Video downloaded: {len(video_data) / 1024 / 1024:.2f} MB")
            
            return video_data
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchKey':
                logger.error(f"[S3] Video not found: {s3_key}")
            else:
                logger.error(f"[S3] Error downloading video: {e}")
            return None
        except Exception as e:
            logger.error(f"[S3] Unexpected error downloading video: {e}", exc_info=True)
            return None
    
    async def delete_video(self, s3_key: str) -> bool:
        """
        Delete video from S3.
        
        Args:
            s3_key: S3 key (user_id/interview_id_timestamp.webm)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[S3] Deleting video: {s3_key}")
            
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"[S3] ✅ Video deleted successfully: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"[S3] Error deleting video: {e}")
            return False
        except Exception as e:
            logger.error(f"[S3] Unexpected error deleting video: {e}", exc_info=True)
            return False
    
    def get_signed_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for accessing a video.
        
        Args:
            s3_key: S3 key (user_id/interview_id_timestamp.webm)
            expires_in: URL expiry time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"[S3] Error generating signed URL: {e}")
            return None
    
    async def get_signed_url_async(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for accessing a video (async version).
        
        Args:
            s3_key: S3 key (user_id/interview_id_timestamp.webm)
            expires_in: URL expiry time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        try:
            url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"[S3] Error generating signed URL: {e}")
            return None
