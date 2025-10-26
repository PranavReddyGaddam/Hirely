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
        print(f"[GET /interviews/{interview_id}] Current user: {current_user.id}")
        interview = await interview_service.get_interview(interview_id, current_user.id)
        if not interview:
            print(f"[GET /interviews/{interview_id}] Interview not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Interview not found")
        return interview
    except HTTPException:
        raise
    except Exception as e:
        print(f"[GET /interviews/{interview_id}] Error: {e}")
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
            "total_questions": question.get("total_questions", 5)  # Get actual total from service
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


@router.get("/{interview_id}/context")
async def get_interview_context(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get complete interview context for AI agent use.
    Returns interview metadata, questions, and current state.
    Used by ElevenLabs agent to understand interview structure.
    """
    interview_service = InterviewService()
    try:
        # Get base interview data
        interview = await interview_service.get_interview(interview_id, current_user.id)
        
        # Get active session data from memory
        session_data = interview_service.active_interviews.get(interview_id, {})
        
        # Build comprehensive context
        questions = session_data.get("questions", [])
        current_idx = session_data.get("current_question_index", 0)
        
        context = {
            "interview_id": interview_id,
            "interview_type": interview.interview_type,
            "company_name": interview.company_name or "Company",
            "position_title": interview.position_title or "Position",
            "job_description": interview.job_description or "",
            "duration_minutes": interview.duration_minutes,
            "status": interview.status,
            
            # Questions data
            "questions": [
                {
                    "id": f"q_{i}",
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "difficulty_level": q.difficulty_level,
                    "expected_duration": q.expected_duration,
                    "order_index": i + 1
                }
                for i, q in enumerate(questions)
            ],
            "total_questions": len(questions),
            
            # Current state
            "current_question_index": current_idx,
            "questions_asked": current_idx,
            "questions_remaining": len(questions) - current_idx,
            
            # Progress tracking
            "progress": {
                "started_at": session_data.get("created_at"),
                "responses_count": len(session_data.get("responses", []))
            }
        }
        
        return context
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{interview_id}/current-question-detail")
async def get_current_question_detail(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get detailed information about the current active question.
    Used by AI agent to know what to ask right now.
    """
    interview_service = InterviewService()
    try:
        session_data = interview_service.active_interviews.get(interview_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        questions = session_data.get("questions", [])
        current_index = session_data.get("current_question_index", 0)
        
        if current_index >= len(questions):
            return {
                "has_more_questions": False,
                "message": "All questions completed"
            }
        
        current_q = questions[current_index]
        
        return {
            "has_more_questions": True,
            "current_question": {
                "id": f"temp_{interview_id}_{current_index}",
                "question_text": current_q.question_text,
                "question_type": current_q.question_type,
                "difficulty_level": current_q.difficulty_level,
                "expected_duration": current_q.expected_duration,
                "order_index": current_index + 1
            },
            "progress": {
                "current": current_index + 1,
                "total": len(questions),
                "percentage": round((current_index + 1) / len(questions) * 100) if questions else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/navigate-question")
async def navigate_question(
    interview_id: str,
    navigation: dict,
    current_user = Depends(get_current_user)
):
    """
    Navigate between questions (next, previous, goto).
    Used by AI agent to control interview flow.
    """
    interview_service = InterviewService()
    try:
        session_data = interview_service.active_interviews.get(interview_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        action = navigation.get("action", "next")
        current_index = session_data.get("current_question_index", 0)
        questions = session_data.get("questions", [])
        
        if action == "next":
            new_index = min(current_index + 1, len(questions))
        elif action == "previous":
            new_index = max(current_index - 1, 0)
        elif action == "goto":
            target = navigation.get("question_index", current_index)
            new_index = max(0, min(target, len(questions) - 1))
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Update the index
        session_data["current_question_index"] = new_index
        
        # Get the new question
        if new_index < len(questions):
            new_question = questions[new_index]
            return {
                "success": True,
                "action": action,
                "new_index": new_index,
                "question": {
                    "id": f"temp_{interview_id}_{new_index}",
                    "question_text": new_question.question_text,
                    "question_type": new_question.question_type,
                    "difficulty_level": new_question.difficulty_level,
                    "order_index": new_index + 1,
                    "total_questions": len(questions)
                }
            }
        else:
            return {
                "success": True,
                "action": action,
                "message": "No more questions",
                "completed": True
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
