from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisResult
from app.services.analysis_service import AnalysisService
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Start AI analysis of interview video"""
    analysis_service = AnalysisService()
    try:
        analysis = await analysis_service.start_analysis(analysis_request, current_user.id)
        
        # Start background analysis
        background_tasks.add_task(
            analysis_service.process_interview_analysis,
            analysis.id,
            analysis_request.interview_id
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{analysis_id}", response_model=AnalysisResult)
async def get_analysis_result(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    """Get analysis results"""
    analysis_service = AnalysisService()
    try:
        result = await analysis_service.get_analysis_result(analysis_id, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Analysis not found")

@router.get("/interview/{interview_id}/latest", response_model=AnalysisResult)
async def get_latest_analysis(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """Get latest analysis for an interview"""
    analysis_service = AnalysisService()
    try:
        result = await analysis_service.get_latest_analysis(interview_id, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Analysis not found")

@router.post("/{analysis_id}/regenerate")
async def regenerate_analysis(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Regenerate analysis with updated parameters"""
    analysis_service = AnalysisService()
    try:
        analysis = await analysis_service.regenerate_analysis(analysis_id, current_user.id)
        
        # Start background regeneration
        background_tasks.add_task(
            analysis_service.process_interview_analysis,
            analysis.id,
            analysis.interview_id
        )
        
        return {"message": "Analysis regeneration started", "analysis_id": analysis.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
