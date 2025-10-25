"""
Interview Analysis API endpoints
Handles comprehensive interview analysis including CV and transcript analysis
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel

from app.services.interview_analysis_orchestrator import InterviewAnalysisOrchestrator
from app.core.auth import get_current_user
from app.schemas.user import UserResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# In-memory storage for analysis results (replace with database in production)
analysis_results_cache = {}
analysis_status_cache = {}


class StartAnalysisRequest(BaseModel):
    interview_id: str
    conversation_id: Optional[str] = None


class AnalysisStatusResponse(BaseModel):
    interview_id: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    progress: Optional[int] = None
    message: Optional[str] = None


class AnalysisResultResponse(BaseModel):
    interview_id: str
    status: str
    overall_score: Optional[dict] = None
    cv_analysis: Optional[dict] = None
    transcript_analysis: Optional[dict] = None
    ai_insights: Optional[dict] = None
    error: Optional[str] = None


async def run_analysis_background(
    interview_id: str,
    user_id: str,
    conversation_id: Optional[str]
):
    """Background task to run interview analysis"""
    try:
        print(f"[Analysis API] 🚀 Starting background analysis for {interview_id}")
        logger.info(f"[Analysis API] Starting background analysis for {interview_id}")
        
        # Update status
        analysis_status_cache[interview_id] = {
            "status": "in_progress",
            "progress": 10,
            "message": "Starting analysis..."
        }
        
        # Run analysis
        orchestrator = InterviewAnalysisOrchestrator()
        results = await orchestrator.analyze_interview(
            interview_id=interview_id,
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        # Store results
        analysis_results_cache[interview_id] = results
        
        # Update status
        if results['analysis_status'] == 'completed':
            analysis_status_cache[interview_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Analysis complete!"
            }
        else:
            analysis_status_cache[interview_id] = {
                "status": "failed",
                "progress": 0,
                "message": results.get('error', 'Analysis failed')
            }
        
        logger.info(f"[Analysis API] Background analysis complete for {interview_id}")
        
    except Exception as e:
        logger.error(f"[Analysis API] Background analysis error: {e}", exc_info=True)
        analysis_status_cache[interview_id] = {
            "status": "failed",
            "progress": 0,
            "message": str(e)
        }


@router.post("/start", response_model=AnalysisStatusResponse)
async def start_interview_analysis(
    request: StartAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Start comprehensive interview analysis (CV + transcript + AI insights).
    Analysis runs in background.
    
    Args:
        request: Analysis request with interview_id and optional conversation_id
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        
    Returns:
        Analysis status response
    """
    try:
        interview_id = request.interview_id
        conversation_id = request.conversation_id
        
        print(f"[Analysis API] 📝 Start analysis request for interview {interview_id}")
        logger.info(f"[Analysis API] Start analysis request for interview {interview_id}")
        
        # Check if analysis is already running
        if interview_id in analysis_status_cache:
            status = analysis_status_cache[interview_id]
            if status['status'] == 'in_progress':
                return AnalysisStatusResponse(
                    interview_id=interview_id,
                    status="in_progress",
                    progress=status.get('progress', 50),
                    message="Analysis already in progress"
                )
        
        # Initialize status
        analysis_status_cache[interview_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Analysis queued"
        }
        
        # Start background analysis
        print(f"[Analysis API] 📤 Adding background task for {interview_id}")
        background_tasks.add_task(
            run_analysis_background,
            interview_id=interview_id,
            user_id=current_user.id,
            conversation_id=conversation_id
        )
        print(f"[Analysis API] ✅ Background task added successfully")
        
        return AnalysisStatusResponse(
            interview_id=interview_id,
            status="pending",
            progress=0,
            message="Analysis started"
        )
        
    except Exception as e:
        logger.error(f"[Analysis API] Error starting analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{interview_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    interview_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Check analysis status for an interview.
    
    Args:
        interview_id: Interview ID
        current_user: Authenticated user
        
    Returns:
        Current analysis status
    """
    try:
        if interview_id not in analysis_status_cache:
            return AnalysisStatusResponse(
                interview_id=interview_id,
                status="not_started",
                progress=0,
                message="Analysis not started"
            )
        
        status = analysis_status_cache[interview_id]
        
        return AnalysisStatusResponse(
            interview_id=interview_id,
            status=status['status'],
            progress=status.get('progress', 0),
            message=status.get('message', '')
        )
        
    except Exception as e:
        logger.error(f"[Analysis API] Error getting status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{interview_id}", response_model=AnalysisResultResponse)
async def get_analysis_results(
    interview_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get analysis results for an interview.
    
    Args:
        interview_id: Interview ID
        current_user: Authenticated user
        
    Returns:
        Complete analysis results
    """
    try:
        # Check if analysis is complete
        if interview_id not in analysis_results_cache:
            # Check status
            if interview_id in analysis_status_cache:
                status = analysis_status_cache[interview_id]
                if status['status'] in ['pending', 'in_progress']:
                    raise HTTPException(
                        status_code=202,
                        detail="Analysis still in progress"
                    )
            
            raise HTTPException(
                status_code=404,
                detail="Analysis results not found"
            )
        
        results = analysis_results_cache[interview_id]
        
        return AnalysisResultResponse(
            interview_id=interview_id,
            status=results.get('analysis_status', 'unknown'),
            overall_score=results.get('overall_score'),
            cv_analysis=results.get('cv_analysis'),
            transcript_analysis=results.get('transcript_analysis'),
            ai_insights=results.get('ai_insights'),
            error=results.get('error')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Analysis API] Error getting results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/results/{interview_id}")
async def clear_analysis_results(
    interview_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Clear analysis results from cache (for testing/cleanup).
    
    Args:
        interview_id: Interview ID
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        if interview_id in analysis_results_cache:
            del analysis_results_cache[interview_id]
        
        if interview_id in analysis_status_cache:
            del analysis_status_cache[interview_id]
        
        return {"message": "Analysis results cleared", "interview_id": interview_id}
        
    except Exception as e:
        logger.error(f"[Analysis API] Error clearing results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

