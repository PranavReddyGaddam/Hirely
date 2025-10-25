from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from typing import List
from pydantic import BaseModel
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewList, InterviewSetupRequest, InterviewType
from app.services.interview_service import InterviewService
from app.services.question_generator_service import QuestionGeneratorService
from app.core.auth import get_current_user

router = APIRouter()

# System Design schemas
class ScreenshotRequest(BaseModel):
    question_id: str
    image_data: str
    timestamp: int

class ProgressRequest(BaseModel):
    question_id: str
    progress_data: dict

class ChatRequest(BaseModel):
    question_id: str
    message: str
    context: str = "system_design"

@router.post("/setup", response_model=InterviewResponse)
async def setup_interview(
    setup_data: InterviewSetupRequest,
    request: Request,
    current_user = Depends(get_current_user)
):
    """Setup a new interview with custom parameters and generate questions"""
    interview_service = InterviewService()
    
    try:
        # Extract access token from request
        authorization = request.headers.get("Authorization")
        access_token = None
        if authorization and authorization.startswith("Bearer "):
            access_token = authorization.split(" ")[1]
        
        # Create the interview
        interview_data = InterviewCreate(
            title=f"{setup_data.position_title} Interview at {setup_data.company_name}",
            description=f"Customized interview for {setup_data.position_title} position",
            interview_type=InterviewType(setup_data.interview_type),
            job_description=setup_data.job_description,
            company_name=setup_data.company_name,
            position_title=setup_data.position_title,
            duration_minutes=setup_data.question_count * 2  # Estimate 2 minutes per question
        )
        
        # Create interview (this will also generate and store questions using Groq)
        interview = await interview_service.create_interview(
            interview_data, 
            current_user.id, 
            setup_data.question_count,
            setup_data.focus_areas,
            setup_data.difficulty_level,
            access_token
        )
        
        return interview
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=InterviewResponse)
async def create_interview(
    interview_data: InterviewCreate,
    current_user = Depends(get_current_user)
):
    """Create a new interview session"""
    interview_service = InterviewService()
    try:
        interview = await interview_service.create_interview(interview_data, current_user.id)
        return interview
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=InterviewList)
async def get_user_interviews(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Get all interviews for current user"""
    interview_service = InterviewService()
    try:
        interviews = await interview_service.get_user_interviews(current_user.id, skip, limit)
        return interviews
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """Get specific interview by ID"""
    interview_service = InterviewService()
    try:
        interview = await interview_service.get_interview(interview_id, current_user.id)
        return interview
    except Exception as e:
        raise HTTPException(status_code=404, detail="Interview not found")

@router.post("/{interview_id}/upload")
async def upload_interview_video(
    interview_id: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload interview video for analysis"""
    interview_service = InterviewService()
    try:
        result = await interview_service.upload_video(interview_id, file, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{interview_id}/debug")
async def debug_interview(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """Debug endpoint to check interview data"""
    interview_service = InterviewService()
    try:
        interview = await interview_service.get_interview(interview_id, current_user.id)
        return {
            "interview": interview,
            "questions_count": len(interview.questions) if interview.questions else 0,
            "responses_count": len(interview.responses) if interview.responses else 0
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{interview_id}/next_question")
async def get_next_question(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """Get the next question for an interview"""
    interview_service = InterviewService()
    try:
        question = await interview_service.get_next_question(interview_id, current_user.id)
        return {
            "question": question,
            "question_index": question.get("order_index", 1),
            "total_questions": 5  # TODO: Get actual total from interview
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="No more questions available")

@router.post("/{interview_id}/submit_answer")
async def submit_answer(
    interview_id: str,
    answer_data: dict,
    current_user = Depends(get_current_user)
):
    """Submit an answer for a question"""
    interview_service = InterviewService()
    try:
        result = await interview_service.submit_answer(interview_id, answer_data, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """Mark interview as completed"""
    interview_service = InterviewService()
    try:
        result = await interview_service.complete_interview(interview_id, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """Delete interview"""
    interview_service = InterviewService()
    try:
        await interview_service.delete_interview(interview_id, current_user.id)
        return {"message": "Interview deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# System Design endpoints
@router.post("/{interview_id}/screenshot")
async def save_screenshot(
    interview_id: str,
    screenshot_data: ScreenshotRequest,
    current_user = Depends(get_current_user)
):
    """Save screenshot from system design canvas"""
    interview_service = InterviewService()
    try:
        result = await interview_service.save_screenshot(interview_id, screenshot_data, current_user.id)
        return {"message": "Screenshot saved successfully", "id": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{interview_id}/progress")
async def save_progress(
    interview_id: str,
    progress_data: ProgressRequest,
    current_user = Depends(get_current_user)
):
    """Save progress data from system design canvas"""
    interview_service = InterviewService()
    try:
        result = await interview_service.save_progress(interview_id, progress_data, current_user.id)
        return {"message": "Progress saved successfully", "id": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{interview_id}/chat")
async def chat_with_ai(
    interview_id: str,
    chat_data: ChatRequest,
    current_user = Depends(get_current_user)
):
    """Chat with AI during system design"""
    interview_service = InterviewService()
    try:
        response = await interview_service.chat_with_ai(interview_id, chat_data, current_user.id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
