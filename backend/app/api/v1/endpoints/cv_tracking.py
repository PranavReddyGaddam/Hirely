"""
CV Tracking API Endpoints
Handles frame processing and session management for interview behavioral analysis
"""

from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from typing import Dict, Optional
import json
from pathlib import Path

from app.cv.services.cv_processor import CVProcessor
from app.services.groq_service import GroqService
from app.core.auth import get_current_user
from app.schemas.user import UserResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Store CV processors for each interview session
cv_sessions: Dict[str, CVProcessor] = {}


@router.post("/cv/start-session")
async def start_cv_session(
    interview_id: str = Form(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Start CV tracking session for an interview
    Initializes MediaPipe and detectors
    """
    try:
        logger.info(f"[CV API] Starting session for interview {interview_id}")
        
        # Create new CV processor for this interview
        processor = CVProcessor()
        result = processor.start_session()
        
        # Store in sessions dict
        cv_sessions[interview_id] = processor
        
        logger.info(f"[CV API] Session started: {result['session_id']}")
        
        return {
            "success": True,
            "message": "CV tracking started",
            **result
        }
        
    except Exception as e:
        logger.error(f"[CV API] Error starting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cv/process-frame")
async def process_frame(
    frame: UploadFile = File(...),
    interview_id: str = Form(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Process single video frame and return behavioral metrics
    Returns all 27 metrics in real-time
    """
    try:
        # Get processor for this interview
        processor = cv_sessions.get(interview_id)
        
        if not processor:
            raise HTTPException(
                status_code=404,
                detail=f"No active CV session for interview {interview_id}. Call start-session first."
            )
        
        # Read frame bytes
        frame_bytes = await frame.read()
        
        # Process frame (uses exact CV copy logic)
        metrics = processor.process_frame(frame_bytes)
        
        return {
            "success": True,
            "metrics": metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CV API] Error processing frame: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cv/end-session")
async def end_cv_session(
    interview_id: str = Form(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    End CV tracking session
    Generates analysis files and AI insights using Groq
    """
    try:
        logger.info(f"[CV API] Ending session for interview {interview_id}")
        
        # Get processor
        processor = cv_sessions.get(interview_id)
        
        if not processor:
            raise HTTPException(
                status_code=404,
                detail=f"No active CV session for interview {interview_id}"
            )
        
        # Stop session and generate exports
        export_result = processor.stop_session(export_path="exports")
        
        # Read the generated analysis file
        analysis_file = export_result['export_files']['interview_analysis']
        
        with open(analysis_file, 'r') as f:
            cv_analysis = json.load(f)
        
        # Generate AI insights using Groq
        logger.info("[CV API] Generating AI insights with Groq...")
        groq_service = GroqService()
        
        # Use existing Groq service to analyze CV data
        ai_insights = await generate_groq_insights(groq_service, cv_analysis)
        
        # Cleanup
        processor.cleanup()
        del cv_sessions[interview_id]
        
        logger.info(f"[CV API] Session ended successfully")
        
        return {
            "success": True,
            "cv_analysis": cv_analysis,
            "ai_insights": ai_insights,
            "export_files": export_result['export_files'],
            "session_stats": {
                "total_frames": export_result['total_frames'],
                "duration_seconds": export_result['duration_seconds']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CV API] Error ending session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cv/session-status/{interview_id}")
async def get_session_status(
    interview_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current status of CV tracking session
    """
    processor = cv_sessions.get(interview_id)
    
    if not processor:
        return {
            "active": False,
            "message": "No active session"
        }
    
    return {
        "active": processor.session_active,
        "frame_count": processor.frame_count,
        "session_id": processor.data_logger.session_id
    }


async def generate_groq_insights(groq_service: GroqService, cv_analysis: Dict) -> Dict:
    """
    Generate AI insights from CV analysis using Groq
    """
    
    if not groq_service.client:
        logger.warning("[CV API] Groq not available, returning basic analysis")
        return {
            "overall_assessment": "CV analysis completed successfully. Detailed AI insights unavailable.",
            "strengths": [],
            "improvements": [],
            "recommendations": []
        }
    
    try:
        # Build comprehensive prompt
        prompt = build_groq_analysis_prompt(cv_analysis)
        
        # Call Groq
        response = groq_service.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": get_groq_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract response
        ai_text = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            ai_insights = json.loads(ai_text)
        except:
            # If not JSON, structure the text response
            ai_insights = {
                "overall_assessment": ai_text[:500],
                "detailed_analysis": ai_text
            }
        
        return ai_insights
        
    except Exception as e:
        logger.error(f"[CV API] Error generating Groq insights: {e}", exc_info=True)
        return {
            "overall_assessment": "Analysis completed. AI insights generation failed.",
            "error": str(e)
        }


def get_groq_system_prompt() -> str:
    """System prompt for Groq CV analysis"""
    return """You are an expert interview coach analyzing a candidate's video interview performance based on comprehensive behavioral metrics.

You have access to:
- Facial expressions and emotional patterns
- Eye contact and attention levels  
- Body posture and positioning
- Hand gestures and nervous behaviors
- Stress indicators and confidence levels
- Head movements and gaze direction

Provide a constructive, actionable analysis including:
1. Overall Assessment (2-3 sentences)
2. Top 3 Strengths (specific behaviors with data)
3. Top 3 Areas for Improvement (with actionable tips)
4. Key Recommendations (3-5 specific actions)

Be specific, reference the metrics, and provide encouragement alongside constructive feedback.
Return your response as JSON with keys: overall_assessment, strengths (array), improvements (array), recommendations (array)."""


def build_groq_analysis_prompt(cv_analysis: Dict) -> str:
    """Build detailed analysis prompt from CV data"""
    
    session = cv_analysis.get('session_info', {})
    emotions = cv_analysis.get('emotions', {})
    facial = cv_analysis.get('facial_metrics', {})
    head_pose = cv_analysis.get('head_pose', {})
    postures = cv_analysis.get('postures', {})
    gestures = cv_analysis.get('gestures', {})
    stress = cv_analysis.get('stress', {})
    attention = cv_analysis.get('attention', {})
    overall = cv_analysis.get('overall_interview_score', {})
    
    prompt = f"""Analyze this interview performance:

**OVERALL SCORES:**
- Overall Score: {overall.get('overall_score', 0):.1f}/100
- Attention: {overall.get('attention_score', 0) * 100:.1f}%
- Posture: {overall.get('posture_score', 0) * 100:.1f}%
- Expression: {overall.get('expression_score', 0) * 100:.1f}%
- Gesture Control: {overall.get('gesture_score', 0) * 100:.1f}%

**SESSION INFO:**
- Duration: {session.get('duration_seconds', 0) / 60:.1f} minutes
- Frames Analyzed: {session.get('total_frames_analyzed', 0)}

**EMOTIONS:**
- Dominant: {emotions.get('dominant_emotion', 'unknown')}
- Calm: {emotions.get('expression_distribution', {}).get('calm', 0):.1f}%
- Smile: {emotions.get('expression_distribution', {}).get('genuine_smile', 0):.1f}%
- Emotional Stability: {emotions.get('emotional_stability', {}).get('score', 'unknown')}

**EYE CONTACT:**
- Looking at Camera: {head_pose.get('camera_focus', {}).get('looking_at_camera_percentage', 0):.1f}%
- Blink Rate: {facial.get('blink_pattern', {}).get('avg_blink_rate_per_minute', 0):.1f} bpm

**POSTURE:**
- Dominant: {postures.get('dominant_posture', 'unknown')}
- Good Posture: {postures.get('posture_quality', {}).get('good_posture_percentage', 0):.1f}%

**GESTURES:**
- Face Touching: {gestures.get('face_touching', {}).get('percentage_of_time', 0):.1f}%
- Hand Fidgeting: {gestures.get('hand_fidgeting', {}).get('percentage_of_time', 0):.1f}%

**STRESS:**
- Level: {stress.get('dominant_stress_level', 'unknown')}

**ATTENTION:**
- Engaged: {attention.get('engagement_breakdown', {}).get('engaged_percentage', 0):.1f}%
- Distracted: {attention.get('engagement_breakdown', {}).get('distracted_percentage', 0):.1f}%

Provide your analysis as JSON."""

    return prompt
