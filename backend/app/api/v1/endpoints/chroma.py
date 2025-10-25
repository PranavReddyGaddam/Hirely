from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.services.chroma_service import ChromaService
from app.services.chroma_connection import get_chroma_collection
from app.core.auth import get_current_user

router = APIRouter()

# Pydantic models for request/response
class DocumentRequest(BaseModel):
    ids: List[str]
    documents: List[str]
    metadatas: List[Dict[str, Any]]

class InterviewResponseRequest(BaseModel):
    interview_id: str
    question_id: str
    response_text: str
    metadata: Dict[str, Any] = {}

class BestPracticeRequest(BaseModel):
    practice_id: str
    content: str
    category: str
    metadata: Dict[str, Any] = {}

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    filter_metadata: Optional[Dict[str, Any]] = None

@router.post("/documents/")
async def add_documents(
    request: DocumentRequest, 
    current_user = Depends(get_current_user)
):
    """Add multiple documents to ChromaDB in batch."""
    try:
        chroma_service = ChromaService()
        success = await chroma_service.batch_add_documents(
            ids=request.ids,
            documents=request.documents,
            metadatas=request.metadatas
        )
        
        if success:
            return {"message": "Documents added successfully", "ids": request.ids}
        else:
            raise HTTPException(status_code=500, detail="Failed to add documents")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview-response/")
async def add_interview_response(
    request: InterviewResponseRequest,
    current_user = Depends(get_current_user)
):
    """Add an interview response to ChromaDB."""
    try:
        chroma_service = ChromaService()
        success = await chroma_service.add_interview_response(
            interview_id=request.interview_id,
            question_id=request.question_id,
            response_text=request.response_text,
            metadata=request.metadata
        )
        
        if success:
            return {"message": "Interview response added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add interview response")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/best-practice/")
async def add_best_practice(
    request: BestPracticeRequest,
    current_user = Depends(get_current_user)
):
    """Add a best practice to ChromaDB."""
    try:
        chroma_service = ChromaService()
        success = await chroma_service.add_best_practices(
            practice_id=request.practice_id,
            content=request.content,
            category=request.category,
            metadata=request.metadata
        )
        
        if success:
            return {"message": "Best practice added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add best practice")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
async def search_similar_responses(
    request: SearchRequest,
    current_user = Depends(get_current_user)
):
    """Search for similar responses based on query."""
    try:
        chroma_service = ChromaService()
        results = await chroma_service.search_similar_responses(
            query=request.query,
            n_results=request.n_results,
            filter_metadata=request.filter_metadata
        )
        
        return {"results": results, "query": request.query}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interview/{interview_id}/responses")
async def get_interview_responses(
    interview_id: str,
    current_user = Depends(get_current_user)
):
    """Get all responses for a specific interview."""
    try:
        chroma_service = ChromaService()
        responses = await chroma_service.get_interview_responses(interview_id)
        
        return {"interview_id": interview_id, "responses": responses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/best-practices/{category}")
async def get_best_practices_by_category(
    category: str,
    current_user = Depends(get_current_user)
):
    """Get best practices for a specific category."""
    try:
        chroma_service = ChromaService()
        practices = await chroma_service.get_best_practices_by_category(category)
        
        return {"category": category, "practices": practices}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/document/{document_id}")
async def delete_document(
    document_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a specific document."""
    try:
        chroma_service = ChromaService()
        success = await chroma_service.delete_document(document_id)
        
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collection/info")
async def get_collection_info(
    current_user = Depends(get_current_user)
):
    """Get information about the ChromaDB collection."""
    try:
        chroma_service = ChromaService()
        info = await chroma_service.get_collection_info()
        
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for ChromaDB connection."""
    try:
        chroma_service = ChromaService()
        info = await chroma_service.get_collection_info()
        
        return {
            "status": "healthy",
            "collection": info.get("name", "unknown"),
            "document_count": info.get("count", 0)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
