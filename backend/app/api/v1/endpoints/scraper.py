"""
API endpoints for Crawl4AI scraper integration.
Provides endpoints for scraping interview questions from various sources.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.services.crawl4ai_service import Crawl4AIService
from app.core.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

class ScrapeRequest(BaseModel):
    """Request model for scraping questions"""
    category: str = "python"
    difficulty: str = "intermediate"
    max_questions: int = 50
    sources: Optional[List[str]] = None

class ScrapeResponse(BaseModel):
    """Response model for scraped questions"""
    success: bool
    total_questions: int
    questions: List[Dict[str, Any]]
    sources_used: List[str]
    scraped_at: str

@router.post("/scrape-questions", response_model=ScrapeResponse)
async def scrape_questions(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Scrape interview questions from various sources.
    
    Args:
        request: Scraping configuration
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Scraped questions with metadata
    """
    try:
        logger.info(f"User {current_user.id} requested scraping for category: {request.category}")
        
        async with Crawl4AIService() as service:
            # Get questions based on request parameters
            questions = await service.get_questions_for_interview(
                category=request.category,
                difficulty=request.difficulty,
                max_questions=request.max_questions
            )
            
            if not questions:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No questions found for category: {request.category}, difficulty: {request.difficulty}"
                )
            
            # Extract unique sources used
            sources_used = list(set([q['source'] for q in questions]))
            
            # Save questions to file in background
            background_tasks.add_task(
                service.save_questions_to_file,
                questions,
                f"user_{current_user.id}_questions_{request.category}_{request.difficulty}.json"
            )
            
            logger.info(f"Successfully scraped {len(questions)} questions for user {current_user.id}")
            
            return ScrapeResponse(
                success=True,
                total_questions=len(questions),
                questions=questions,
                sources_used=sources_used,
                scraped_at=questions[0]['scraped_at'] if questions else ""
            )
            
    except Exception as e:
        logger.error(f"Error scraping questions: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/scrape-status")
async def get_scrape_status(current_user = Depends(get_current_user)):
    """
    Get the status of available scraping sources.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Status of available sources
    """
    try:
        async with Crawl4AIService() as service:
            # Get available sources
            sources = service.question_sources
            
            return {
                "available_sources": len(sources),
                "sources": [
                    {
                        "name": source["name"],
                        "category": source["category"],
                        "difficulty": source["difficulty"],
                        "url": source["url"]
                    }
                    for source in sources
                ],
                "categories": list(set([source["category"] for source in sources])),
                "difficulties": list(set([source["difficulty"] for source in sources]))
            }
            
    except Exception as e:
        logger.error(f"Error getting scrape status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scrape status: {str(e)}")

@router.post("/scrape-specific-source")
async def scrape_specific_source(
    source_name: str,
    current_user = Depends(get_current_user)
):
    """
    Scrape questions from a specific source.
    
    Args:
        source_name: Name of the source to scrape
        current_user: Current authenticated user
        
    Returns:
        Questions from the specific source
    """
    try:
        async with Crawl4AIService() as service:
            # Find the source
            source = None
            for s in service.question_sources:
                if s["name"] == source_name:
                    source = s
                    break
            
            if not source:
                raise HTTPException(
                    status_code=404,
                    detail=f"Source '{source_name}' not found"
                )
            
            # Scrape from the specific source
            result = await service.scrape_questions_from_source(source)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to scrape from {source_name}: {result['error']}"
                )
            
            return {
                "success": True,
                "source": result["source"],
                "category": result["category"],
                "difficulty": result["difficulty"],
                "total_questions": result["total_questions"],
                "questions": result["questions"][:20],  # Return first 20 questions
                "scraped_at": result["scraped_at"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping specific source: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/categories")
async def get_available_categories(current_user = Depends(get_current_user)):
    """
    Get available question categories.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of available categories
    """
    try:
        async with Crawl4AIService() as service:
            categories = list(set([source["category"] for source in service.question_sources]))
            return {
                "categories": categories,
                "total_categories": len(categories)
            }
            
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.get("/difficulties")
async def get_available_difficulties(current_user = Depends(get_current_user)):
    """
    Get available difficulty levels.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of available difficulty levels
    """
    try:
        async with Crawl4AIService() as service:
            difficulties = list(set([source["difficulty"] for source in service.question_sources]))
            return {
                "difficulties": difficulties,
                "total_difficulties": len(difficulties)
            }
            
    except Exception as e:
        logger.error(f"Error getting difficulties: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get difficulties: {str(e)}")

@router.post("/test-scraping")
async def test_scraping(
    current_user = Depends(get_current_user)
):
    """
    Test the scraping functionality with a small sample.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Test results
    """
    try:
        logger.info(f"User {current_user.id} requested scraping test")
        
        async with Crawl4AIService() as service:
            # Test with a small sample
            questions = await service.get_questions_for_interview(
                category="python",
                difficulty="intermediate",
                max_questions=5
            )
            
            return {
                "success": True,
                "message": "Scraping test completed successfully",
                "questions_found": len(questions),
                "sample_questions": [
                    {
                        "question": q["question"][:100] + "..." if len(q["question"]) > 100 else q["question"],
                        "source": q["source"],
                        "category": q["category"],
                        "difficulty": q["difficulty"]
                    }
                    for q in questions[:3]
                ],
                "test_completed_at": questions[0]["scraped_at"] if questions else ""
            }
            
    except Exception as e:
        logger.error(f"Error in scraping test: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping test failed: {str(e)}")
