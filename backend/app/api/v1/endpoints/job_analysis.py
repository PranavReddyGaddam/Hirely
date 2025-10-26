"""
Job Analysis API Endpoints
Provides endpoints for job scraping, market analysis, and interview preparation.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging

from app.schemas.job_analysis import JobAnalysisRequest, JobAnalysisResponse, InterviewPrepRequest, InterviewPrepResponse
from app.services.job_market_analyzer import JobMarketAnalyzer
from app.services.crawl4ai_service import Crawl4AIService
from app.core.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze-job-market", response_model=JobAnalysisResponse)
async def analyze_job_market(
    request: JobAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Analyze job market trends and provide AI-powered insights.
    
    Args:
        request: Job analysis configuration
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Comprehensive job market analysis
    """
    try:
        logger.info(f"User {current_user.id} requested job market analysis for: {request.keywords}")
        
        analyzer = JobMarketAnalyzer()
        
        # Perform job market analysis
        analysis = await analyzer.analyze_job_market(
            keywords=request.keywords,
            location=request.location or "",
            analysis_depth=request.analysis_depth or "comprehensive"
        )
        
        if not analysis['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Job market analysis failed: {analysis['error']}"
            )
        
        # Save analysis results in background
        background_tasks.add_task(
            _save_analysis_results,
            analysis,
            f"user_{current_user.id}_job_analysis_{request.keywords.replace(' ', '_')}.json"
        )
        
        logger.info(f"Successfully completed job market analysis for user {current_user.id}")
        
        return JobAnalysisResponse(
            success=True,
            keywords=analysis['keywords'],
            location=analysis['location'],
            total_jobs_analyzed=analysis['job_data']['total_jobs_analyzed'],
            insights=analysis['insights_report'],
            ai_analysis=analysis['ai_analysis'],
            generated_at=analysis['generated_at']
        )
        
    except Exception as e:
        logger.error(f"Error in job market analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/generate-interview-prep", response_model=InterviewPrepResponse)
async def generate_interview_prep(
    request: InterviewPrepRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate comprehensive interview preparation based on job market data.
    
    Args:
        request: Interview prep configuration
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Interview preparation materials and study guide
    """
    try:
        logger.info(f"User {current_user.id} requested interview prep for: {request.job_title}")
        
        analyzer = JobMarketAnalyzer()
        
        # Generate interview preparation
        prep = await analyzer.generate_interview_prep(
            job_title=request.job_title,
            location=request.location or "",
            prep_type=request.prep_type or "comprehensive"
        )
        
        if not prep['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Interview prep generation failed: {prep['error']}"
            )
        
        # Save preparation materials in background
        background_tasks.add_task(
            _save_prep_materials,
            prep,
            f"user_{current_user.id}_interview_prep_{request.job_title.replace(' ', '_')}.json"
        )
        
        logger.info(f"Successfully generated interview prep for user {current_user.id}")
        
        return InterviewPrepResponse(
            success=True,
            job_title=prep['job_title'],
            location=prep['location'],
            total_questions=prep['job_data']['total_questions'],
            study_guide=prep['study_guide'],
            practice_plan=prep['practice_plan'],
            ai_analysis=prep['ai_analysis'],
            generated_at=prep['generated_at']
        )
        
    except Exception as e:
        logger.error(f"Error generating interview prep: {e}")
        raise HTTPException(status_code=500, detail=f"Interview prep failed: {str(e)}")

@router.post("/scrape-jobs")
async def scrape_jobs(
    keywords: str,
    location: Optional[str] = None,
    max_results: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Scrape jobs from LinkedIn using BrightData MCP.
    
    Args:
        keywords: Job search keywords
        location: Location filter (optional)
        max_results: Maximum number of results
        current_user: Current authenticated user
        
    Returns:
        Scraped job data
    """
    try:
        logger.info(f"User {current_user.id} requested job scraping for: {keywords}")
        
        service = Crawl4AIService()
        
        # Scrape jobs using BrightData MCP
        job_data = await service.brightdata_service.scrape_linkedin_jobs(
            keywords=keywords,
            location=location or "",
            max_results=max_results
        )
        
        if not job_data['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Job scraping failed: {job_data['error']}"
            )
        
        logger.info(f"Successfully scraped {job_data['total_jobs']} jobs for user {current_user.id}")
        
        return {
            "success": True,
            "keywords": keywords,
            "location": location,
            "total_jobs": job_data['total_jobs'],
            "jobs": job_data['jobs'],
            "scraped_at": job_data['scraped_at']
        }
        
    except Exception as e:
        logger.error(f"Error scraping jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Job scraping failed: {str(e)}")

@router.post("/scrape-company-jobs")
async def scrape_company_jobs(
    company_name: str,
    generate_questions: bool = True,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Scrape jobs from a specific company.
    
    Args:
        company_name: Name of the company
        generate_questions: Whether to generate interview questions
        current_user: Current authenticated user
        
    Returns:
        Company job data and optional interview questions
    """
    try:
        logger.info(f"User {current_user.id} requested company job scraping for: {company_name}")
        
        service = Crawl4AIService()
        
        # Scrape company jobs
        company_data = await service.scrape_company_specific_jobs(
            company_name=company_name,
            generate_questions=generate_questions
        )
        
        if not company_data['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Company job scraping failed: {company_data['error']}"
            )
        
        logger.info(f"Successfully scraped {company_data['total_jobs']} jobs for {company_name}")
        
        return {
            "success": True,
            "company": company_name,
            "total_jobs": company_data['total_jobs'],
            "jobs": company_data['jobs'],
            "interview_questions": company_data.get('interview_questions', []),
            "total_questions": company_data.get('total_questions', 0),
            "scraped_at": company_data['scraped_at']
        }
        
    except Exception as e:
        logger.error(f"Error scraping company jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Company job scraping failed: {str(e)}")

@router.get("/job-market-insights")
async def get_job_market_insights(
    keywords: str = "software engineer",
    location: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get job market insights and trends.
    
    Args:
        keywords: Job search keywords
        location: Location filter (optional)
        current_user: Current authenticated user
        
    Returns:
        Job market insights and analysis
    """
    try:
        logger.info(f"User {current_user.id} requested job market insights for: {keywords}")
        
        service = Crawl4AIService()
        
        # Get job market insights
        insights = await service.get_job_market_insights(
            keywords=keywords,
            location=location or ""
        )
        
        if not insights['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Job market insights failed: {insights['error']}"
            )
        
        logger.info(f"Successfully generated job market insights for user {current_user.id}")
        
        return {
            "success": True,
            "keywords": keywords,
            "location": location,
            "total_jobs_analyzed": insights['total_jobs_analyzed'],
            "trends": insights['trends'],
            "skills_analysis": insights['skills_analysis'],
            "insights": insights['insights'],
            "generated_at": insights['generated_at']
        }
        
    except Exception as e:
        logger.error(f"Error getting job market insights: {e}")
        raise HTTPException(status_code=500, detail=f"Job market insights failed: {str(e)}")

@router.post("/scrape-jobs-with-skills")
async def scrape_jobs_with_skills(
    keywords: str,
    location: Optional[str] = None,
    max_results: int = 20,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Scrape jobs and extract detailed skills, requirements, and qualifications.
    
    Args:
        keywords: Job search keywords
        location: Location filter (optional)
        max_results: Maximum number of results
        current_user: Current authenticated user
        
    Returns:
        Detailed job data with skills analysis
    """
    try:
        logger.info(f"User {current_user.id} requested skills analysis for: {keywords}")
        
        service = Crawl4AIService()
        
        # Scrape jobs with skills analysis
        skills_data = await service.brightdata_service.scrape_jobs_with_skills_analysis(
            keywords=keywords,
            location=location or "",
            max_results=max_results
        )
        
        if not skills_data['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Skills analysis failed: {skills_data['error']}"
            )
        
        # Get detailed insights
        insights = service.brightdata_service.get_skills_insights(skills_data['skills_analysis'])
        
        logger.info(f"Successfully analyzed {skills_data['total_jobs_analyzed']} jobs for skills")
        
        return {
            "success": True,
            "keywords": keywords,
            "location": location,
            "total_jobs_analyzed": skills_data['total_jobs_analyzed'],
            "jobs": skills_data['jobs'],
            "skills_analysis": skills_data['skills_analysis'],
            "requirements_analysis": skills_data['requirements_analysis'],
            "qualifications_analysis": skills_data['qualifications_analysis'],
            "top_skills": skills_data['top_skills'],
            "skills_insights": insights,
            "scraped_at": skills_data['scraped_at']
        }
        
    except Exception as e:
        logger.error(f"Error in skills analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Skills analysis failed: {str(e)}")

@router.get("/scrape-status")
async def get_scrape_status(current_user: UserResponse = Depends(get_current_user)):
    """
    Get the status of recent scraping operations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Scraping status information
    """
    try:
        # This would typically check a database or cache for scraping status
        # For now, return a simple status
        return {
            "status": "active",
            "last_scrape": "2024-01-01T00:00:00Z",
            "total_scrapes_today": 0,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error getting scrape status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# Background task functions
async def _save_analysis_results(analysis: Dict[str, Any], filename: str):
    """Save analysis results to file"""
    try:
        import json
        from pathlib import Path
        
        # Create exports directory if it doesn't exist
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        file_path = exports_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis results saved to {file_path}")
        
    except Exception as e:
        logger.error(f"Error saving analysis results: {e}")

async def _save_prep_materials(prep: Dict[str, Any], filename: str):
    """Save interview prep materials to file"""
    try:
        import json
        from pathlib import Path
        
        # Create exports directory if it doesn't exist
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        file_path = exports_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(prep, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Interview prep materials saved to {file_path}")
        
    except Exception as e:
        logger.error(f"Error saving prep materials: {e}")
