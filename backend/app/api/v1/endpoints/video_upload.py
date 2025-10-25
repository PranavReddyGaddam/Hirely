"""
Video Upload API endpoints for uploading interview videos to S3
"""
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from typing import Optional
from app.services.supabase_service import SupabaseService
from app.services.s3_service import S3Service
from app.core.auth import get_current_user
from app.schemas.user import UserResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_interview_video(
    interview_id: str = Form(...),
    video: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Upload interview video to Supabase Storage (object storage).
    
    Args:
        interview_id: Interview ID
        video: Video file (WebM, MP4, etc.)
        current_user: Authenticated user
        
    Returns:
        Video metadata including storage path and URL
    """
    try:
        logger.info(f"[Video Upload] Starting upload for interview {interview_id}")
        logger.info(f"[Video Upload] User: {current_user.email}")
        logger.info(f"[Video Upload] Video filename: {video.filename}")
        logger.info(f"[Video Upload] Content type: {video.content_type}")
        
        # Read video data
        video_data = await video.read()
        video_size_mb = len(video_data) / 1024 / 1024
        
        logger.info(f"[Video Upload] Video size: {video_size_mb:.2f} MB")
        
        # Validate file size (max 500 MB)
        if video_size_mb > 500:
            raise HTTPException(
                status_code=413,
                detail="Video file too large. Maximum size is 500 MB."
            )
        
        # Determine file extension
        file_extension = "webm"  # Default
        if video.content_type:
            if "mp4" in video.content_type:
                file_extension = "mp4"
            elif "quicktime" in video.content_type:
                file_extension = "mov"
        
        # Upload to S3
        s3_service = S3Service()
        upload_result = await s3_service.upload_video(
            user_id=current_user.id,
            interview_id=interview_id,
            video_data=video_data,
            file_extension=file_extension
        )
        
        if not upload_result:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload video to storage"
            )
        
        # Update interview record with video metadata (using SupabaseService for DB operations)
        supabase_service = SupabaseService()
        metadata_updated = await supabase_service.update_interview_video_metadata(
            interview_id=interview_id,
            storage_path=upload_result["storage_path"],
            public_url=upload_result["public_url"],
            size_bytes=upload_result["size_bytes"]
        )
        
        if not metadata_updated:
            logger.warning(f"[Video Upload] Failed to update interview metadata, but upload succeeded")
        
        logger.info(f"[Video Upload] ✅ Video uploaded successfully: {upload_result['storage_path']}")
        
        return {
            "success": True,
            "message": "Video uploaded successfully",
            "storage_path": upload_result["storage_path"],
            "video_url": upload_result["public_url"],
            "size_bytes": upload_result["size_bytes"],
            "size_mb": round(upload_result["size_bytes"] / 1024 / 1024, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Video Upload] Error uploading video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{interview_id}")
async def get_video_url(
    interview_id: str,
    expires_in: int = 3600,  # 1 hour default
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a signed URL for accessing an interview video.
    
    Args:
        interview_id: Interview ID
        expires_in: URL expiry time in seconds (default 3600 = 1 hour)
        current_user: Authenticated user
        
    Returns:
        Signed URL for video access
    """
    try:
        supabase_service = SupabaseService()
        
        # Get interview to verify ownership and get storage path
        interview = await supabase_service.get_interview(interview_id, current_user.id)
        
        if not interview:
            raise HTTPException(
                status_code=404,
                detail="Interview not found or you don't have access"
            )
        
        if not interview.video_storage_path:
            raise HTTPException(
                status_code=404,
                detail="No video found for this interview"
            )
        
        # Generate signed URL from S3
        s3_service = S3Service()
        signed_url = await s3_service.get_signed_url_async(
            s3_key=interview.video_storage_path,
            expires_in=expires_in
        )
        
        if not signed_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate video URL"
            )
        
        return {
            "success": True,
            "video_url": signed_url,
            "expires_in": expires_in,
            "storage_path": interview.video_storage_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{interview_id}")
async def delete_interview_video(
    interview_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete interview video from S3.
    
    Args:
        interview_id: Interview ID
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        supabase_service = SupabaseService()
        
        # Get interview to verify ownership and get storage path
        interview = await supabase_service.get_interview(interview_id, current_user.id)
        
        if not interview:
            raise HTTPException(
                status_code=404,
                detail="Interview not found or you don't have access"
            )
        
        if not interview.video_storage_path:
            raise HTTPException(
                status_code=404,
                detail="No video found for this interview"
            )
        
        # Delete video from S3
        s3_service = S3Service()
        deleted = await s3_service.delete_video(interview.video_storage_path)
        
        if not deleted:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete video from storage"
            )
        
        # Update interview record to remove video metadata
        await supabase_service.update_interview(
            interview_id=interview_id,
            interview_data={
                "video_storage_path": None,
                "video_url": None,
                "video_size_bytes": None,
                "video_uploaded_at": None
            }
        )
        
        return {
            "success": True,
            "message": "Video deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

