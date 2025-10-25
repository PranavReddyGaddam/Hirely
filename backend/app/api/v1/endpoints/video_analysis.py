"""
Video Analysis API Endpoints
Process saved interview videos and run CV analysis
"""

from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from typing import Dict
import cv2
import numpy as np
import tempfile
import os
from pathlib import Path

from app.cv.services.cv_processor import CVProcessor
from app.services.groq_service import GroqService
from app.core.auth import get_current_user
from app.schemas.user import UserResponse
from app.utils.logger import get_logger
import json

logger = get_logger(__name__)
router = APIRouter()


@router.post("/video/analyze-saved-interview")
async def analyze_saved_interview_video(
    video: UploadFile = File(...),
    interview_id: str = Form(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Analyze a saved interview video file
    
    This endpoint:
    1. Accepts a video file (WebM, MP4, etc.)
    2. Extracts frames at 5 FPS
    3. Runs CV analysis on each frame
    4. Generates comprehensive behavioral analysis
    5. Returns analysis JSON + AI insights
    
    Args:
        video: Video file from interview recording
        interview_id: ID of the interview session
        current_user: Authenticated user
        
    Returns:
        Dict with cv_analysis, ai_insights, and export files
    """
    
    temp_video_path = None
    
    try:
        logger.info(f"[Video Analysis] Starting analysis for interview {interview_id}")
        logger.info(f"[Video Analysis] Video file: {video.filename}, size: {video.size} bytes")
        
        # Save uploaded video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            temp_video_path = temp_file.name
            content = await video.read()
            temp_file.write(content)
            logger.info(f"[Video Analysis] Saved video to temp file: {temp_video_path}")
        
        # Open video with OpenCV
        cap = cv2.VideoCapture(temp_video_path)
        
        if not cap.isOpened():
            raise HTTPException(
                status_code=400,
                detail="Failed to open video file. Ensure it's a valid video format."
            )
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"[Video Analysis] Video properties: {fps:.2f} FPS, {total_frames} frames, {duration:.2f}s duration")
        
        # Initialize CV processor
        processor = CVProcessor()
        processor.start_session()
        
        # Process video at 5 FPS (extract every Nth frame)
        target_fps = 5
        frame_skip = max(1, int(fps / target_fps))
        
        frame_count = 0
        processed_count = 0
        
        logger.info(f"[Video Analysis] Processing every {frame_skip} frames (targeting 5 FPS)")
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Process every Nth frame
            if frame_count % frame_skip == 0:
                # Encode frame as JPEG
                success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                if success:
                    # Process frame with CV system
                    frame_bytes = buffer.tobytes()
                    metrics = processor.process_frame(frame_bytes)
                    processed_count += 1
                    
                    if processed_count % 25 == 0:  # Log every 5 seconds
                        logger.info(f"[Video Analysis] Processed {processed_count} frames...")
            
            frame_count += 1
        
        cap.release()
        
        logger.info(f"[Video Analysis] Finished processing {processed_count} frames from {frame_count} total frames")
        
        # Stop session and generate analysis
        export_result = processor.stop_session(export_path="exports")
        
        # Read the generated analysis file
        analysis_file = export_result['export_files']['interview_analysis']
        
        with open(analysis_file, 'r') as f:
            cv_analysis = json.load(f)
        
        # Generate AI insights using Groq
        logger.info("[Video Analysis] Generating AI insights with Groq...")
        groq_service = GroqService()
        
        # Import the helper function from cv_tracking
        from app.api.v1.endpoints.cv_tracking import generate_groq_insights
        ai_insights = await generate_groq_insights(groq_service, cv_analysis)
        
        # Cleanup processor
        processor.cleanup()
        
        logger.info(f"[Video Analysis] Analysis complete for interview {interview_id}")
        
        return {
            "success": True,
            "message": "Video analysis completed successfully",
            "video_info": {
                "filename": video.filename,
                "duration_seconds": duration,
                "total_frames": frame_count,
                "frames_analyzed": processed_count,
                "target_fps": target_fps,
                "actual_fps": processed_count / duration if duration > 0 else 0
            },
            "cv_analysis": cv_analysis,
            "ai_insights": ai_insights,
            "export_files": export_result['export_files']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Video Analysis] Error analyzing video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")
    
    finally:
        # Cleanup temporary video file
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.unlink(temp_video_path)
                logger.info(f"[Video Analysis] Cleaned up temp file: {temp_video_path}")
            except Exception as e:
                logger.warning(f"[Video Analysis] Failed to cleanup temp file: {e}")


@router.get("/video/supported-formats")
async def get_supported_video_formats():
    """
    Get list of supported video formats for analysis
    """
    return {
        "supported_formats": [
            {
                "format": "WebM",
                "extensions": [".webm"],
                "codecs": ["VP8", "VP9"],
                "recommended": True,
                "note": "Default format from browser MediaRecorder"
            },
            {
                "format": "MP4",
                "extensions": [".mp4", ".m4v"],
                "codecs": ["H.264", "H.265"],
                "recommended": True,
                "note": "Widely supported"
            },
            {
                "format": "AVI",
                "extensions": [".avi"],
                "codecs": ["Various"],
                "recommended": False,
                "note": "Legacy format"
            },
            {
                "format": "MOV",
                "extensions": [".mov"],
                "codecs": ["Various"],
                "recommended": True,
                "note": "Apple QuickTime format"
            }
        ],
        "notes": [
            "Browser-recorded videos (WebM) are automatically supported",
            "Video will be analyzed at 5 FPS regardless of source FPS",
            "Larger videos may take longer to process",
            "Recommended max file size: 500MB"
        ]
    }

