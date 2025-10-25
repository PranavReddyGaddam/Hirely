"""
Interview session schemas for creating, managing, and tracking interviews.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class InterviewStatus(str, Enum):
    """Interview session status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewType(str, Enum):
    """Interview type enumeration."""
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    MOCK_INTERVIEW = "mock_interview"
    MIXED = "mixed"
    CUSTOM = "custom"


class QuestionBase(BaseModel):
    """Base schema for interview questions."""
    question_text: str
    question_type: str
    difficulty_level: str = "medium"
    expected_duration: int = 120  # seconds


class QuestionCreate(QuestionBase):
    """Schema for creating new questions."""
    pass


class QuestionResponse(QuestionBase):
    """Schema for question data in responses."""
    id: str
    interview_id: str
    order_index: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResponseBase(BaseModel):
    """Base schema for interview responses."""
    question_id: str
    response_text: Optional[str] = None
    audio_duration: Optional[float] = None
    confidence_score: Optional[float] = None


class ResponseCreate(ResponseBase):
    """Schema for creating new responses."""
    pass


class ResponseResponse(ResponseBase):
    """Schema for response data in responses."""
    id: str
    interview_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewSetupRequest(BaseModel):
    """Schema for interview setup with customization options."""
    company_name: str
    position_title: str
    job_link: Optional[str] = None
    job_description: Optional[str] = None
    question_count: int = 5
    interview_type: str = "mixed"
    focus_areas: List[str] = []
    difficulty_level: str = "medium"


class InterviewCreate(BaseModel):
    """Schema for creating new interview sessions."""
    title: str
    description: Optional[str] = None
    interview_type: InterviewType = InterviewType.MOCK_INTERVIEW
    job_description: Optional[str] = None
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    duration_minutes: int = 30
    # TODO: Add custom question sets, evaluation criteria


class InterviewResponse(BaseModel):
    """Schema for interview data in responses."""
    id: str
    title: str
    description: Optional[str] = None
    interview_type: InterviewType
    job_description: Optional[str] = None
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    duration_minutes: int
    status: InterviewStatus
    user_id: str
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    questions: List[QuestionResponse] = []
    responses: List[ResponseResponse] = []
    
    class Config:
        from_attributes = True


class InterviewList(BaseModel):
    """Schema for paginated interview list responses."""
    interviews: List[InterviewResponse]
    total: int
    skip: int
    limit: int


class InterviewSession(BaseModel):
    """Schema for active interview session data."""
    interview_id: str
    current_question_index: int
    questions: List[QuestionResponse]
    responses: List[ResponseResponse]
    session_data: Dict[str, Any] = {}
    # TODO: Add real-time session state, voice interaction data
