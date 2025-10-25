"""
Analysis schemas for interview evaluation and feedback generation.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FeedbackCategory(str, Enum):
    """Feedback category enumeration."""
    COMMUNICATION = "communication"
    TECHNICAL_SKILLS = "technical_skills"
    PROBLEM_SOLVING = "problem_solving"
    CONFIDENCE = "confidence"
    CLARITY = "clarity"
    STRUCTURE = "structure"


class FeedbackItem(BaseModel):
    """Schema for individual feedback items."""
    category: FeedbackCategory
    score: float  # 0.0 to 1.0
    feedback_text: str
    suggestions: List[str] = []
    strengths: List[str] = []
    areas_for_improvement: List[str] = []


class AnalysisRequest(BaseModel):
    """Schema for requesting interview analysis."""
    interview_id: str
    analysis_type: str = "comprehensive"  # comprehensive, quick, detailed
    include_voice_analysis: bool = True
    include_behavioral_analysis: bool = True
    custom_criteria: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """Schema for analysis initiation response."""
    id: str
    interview_id: str
    status: AnalysisStatus
    analysis_type: str
    created_at: datetime
    estimated_completion_time: Optional[int] = None  # seconds
    
    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    """Schema for complete analysis results."""
    id: str
    interview_id: str
    status: AnalysisStatus
    overall_score: float  # 0.0 to 1.0
    feedback_items: List[FeedbackItem]
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    detailed_analysis: Dict[str, Any] = {}
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VoiceAnalysis(BaseModel):
    """Schema for voice-specific analysis results."""
    speech_clarity: float
    speaking_pace: float
    confidence_level: float
    filler_words_count: int
    pauses_analysis: Dict[str, Any]
    emotion_detection: Dict[str, float]


class BehavioralAnalysis(BaseModel):
    """Schema for behavioral analysis results."""
    eye_contact_score: float
    posture_score: float
    gesture_analysis: Dict[str, Any]
    engagement_level: float
    stress_indicators: List[str]


class ReportRequest(BaseModel):
    """Schema for generating analysis reports."""
    analysis_id: str
    report_format: str = "pdf"  # pdf, json, html
    include_detailed_breakdown: bool = True
    include_recommendations: bool = True
