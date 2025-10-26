"""
Job Analysis Schemas
Pydantic models for job scraping and analysis API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class JobAnalysisRequest(BaseModel):
    """Request model for job market analysis"""
    keywords: str = Field(..., description="Job search keywords")
    location: Optional[str] = Field(None, description="Location filter")
    analysis_depth: Optional[str] = Field("comprehensive", description="Analysis depth: basic, comprehensive, detailed")

class JobAnalysisResponse(BaseModel):
    """Response model for job market analysis"""
    success: bool
    keywords: str
    location: Optional[str]
    total_jobs_analyzed: int
    insights: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    generated_at: str

class InterviewPrepRequest(BaseModel):
    """Request model for interview preparation generation"""
    job_title: str = Field(..., description="Target job title")
    location: Optional[str] = Field(None, description="Location filter")
    prep_type: Optional[str] = Field("comprehensive", description="Preparation type: basic, comprehensive, detailed")

class InterviewPrepResponse(BaseModel):
    """Response model for interview preparation generation"""
    success: bool
    job_title: str
    location: Optional[str]
    total_questions: int
    study_guide: Dict[str, Any]
    practice_plan: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    generated_at: str

class JobScrapeRequest(BaseModel):
    """Request model for job scraping"""
    keywords: str = Field(..., description="Job search keywords")
    location: Optional[str] = Field(None, description="Location filter")
    max_results: int = Field(50, description="Maximum number of results")
    time_filter: Optional[str] = Field("r3600", description="Time filter (r3600=24h, r86400=1week)")

class JobScrapeResponse(BaseModel):
    """Response model for job scraping"""
    success: bool
    keywords: str
    location: Optional[str]
    total_jobs: int
    jobs: List[Dict[str, Any]]
    scraped_at: str

class CompanyJobRequest(BaseModel):
    """Request model for company job scraping"""
    company_name: str = Field(..., description="Name of the company")
    generate_questions: bool = Field(True, description="Whether to generate interview questions")
    max_results: int = Field(20, description="Maximum number of jobs to scrape")

class CompanyJobResponse(BaseModel):
    """Response model for company job scraping"""
    success: bool
    company: str
    total_jobs: int
    jobs: List[Dict[str, Any]]
    interview_questions: List[Dict[str, Any]]
    total_questions: int
    scraped_at: str

class JobMarketInsightsRequest(BaseModel):
    """Request model for job market insights"""
    keywords: str = Field("software engineer", description="Job search keywords")
    location: Optional[str] = Field(None, description="Location filter")

class JobMarketInsightsResponse(BaseModel):
    """Response model for job market insights"""
    success: bool
    keywords: str
    location: Optional[str]
    total_jobs_analyzed: int
    trends: Dict[str, Any]
    skills_analysis: Dict[str, int]
    insights: Dict[str, Any]
    generated_at: str

class JobData(BaseModel):
    """Model for individual job data"""
    title: str
    company: str
    location: str
    posted_time: str
    job_type: str
    url: str
    description: str
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    salary_range: Optional[str] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None

class InterviewQuestion(BaseModel):
    """Model for interview questions"""
    question: str
    category: str
    difficulty: str
    type: str  # technical, behavioral, etc.
    source: str
    answer_hints: Optional[List[str]] = None

class SkillsAnalysis(BaseModel):
    """Model for skills analysis results"""
    skill: str
    frequency: int
    percentage: float
    trend: str  # increasing, decreasing, stable

class MarketTrends(BaseModel):
    """Model for market trends analysis"""
    total_jobs: int
    job_types: Dict[str, int]
    top_locations: Dict[str, int]
    top_companies: Dict[str, int]
    skills_analysis: Dict[str, int]
    remote_vs_onsite: Dict[str, int]

class AIAnalysis(BaseModel):
    """Model for AI analysis results"""
    market_trends: str
    skills_analysis: str
    career_recommendations: str
    confidence_score: float
    key_findings: List[str]

class StudyGuide(BaseModel):
    """Model for study guide"""
    overview: Dict[str, Any]
    study_sections: Dict[str, Any]
    ai_recommendations: str
    resources: List[str]
    timeline: Dict[str, str]

class PracticePlan(BaseModel):
    """Model for practice plan"""
    weekly_schedule: Dict[str, str]
    daily_practice: Dict[str, str]
    resources: List[str]
    goals: List[str]
    milestones: List[str]

class ScrapeStatus(BaseModel):
    """Model for scraping status"""
    status: str
    last_scrape: str
    total_scrapes_today: int
    user_id: str
    active_scrapes: List[str] = []

# Error response models
class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ValidationErrorResponse(ErrorResponse):
    """Validation error response model"""
    error_code: str = "VALIDATION_ERROR"
    field_errors: Dict[str, List[str]] = {}

class ScrapingErrorResponse(ErrorResponse):
    """Scraping error response model"""
    error_code: str = "SCRAPING_ERROR"
    retry_after: Optional[int] = None  # seconds

class AIAnalysisErrorResponse(ErrorResponse):
    """AI analysis error response model"""
    error_code: str = "AI_ANALYSIS_ERROR"
    fallback_available: bool = False
