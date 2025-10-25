import logging
from typing import List, Dict, Any, Optional
from chromadb.api.models.Collection import Collection
from .chroma_connection import get_chroma_client

logger = logging.getLogger(__name__)

class ChromaService:
    """Service for ChromaDB operations related to interview data."""
    
    def __init__(self):
        """Initialize ChromaDB service."""
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(
            name="interview_responses",
            metadata={"description": "Interview responses and best practices"}
        )
        logger.info("ChromaService initialized successfully")
    
    async def add_interview_response(
        self, 
        interview_id: str, 
        question_id: str, 
        response_text: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """Add an interview response to ChromaDB."""
        try:
            document_id = f"{interview_id}_{question_id}"
            
            self.collection.add(
                ids=[document_id],
                documents=[response_text],
                metadatas=[{
                    "interview_id": interview_id,
                    "question_id": question_id,
                    "response_type": "interview_response",
                    **metadata
                }]
            )
            
            logger.info(f"Successfully added interview response: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding interview response: {e}")
            return False
    
    async def add_best_practices(
        self, 
        practice_id: str, 
        content: str, 
        category: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Add best practices content to ChromaDB."""
        try:
            self.collection.add(
                ids=[practice_id],
                documents=[content],
                metadatas=[{
                    "practice_id": practice_id,
                    "category": category,
                    "response_type": "best_practice",
                    **metadata
                }]
            )
            
            logger.info(f"Successfully added best practice: {practice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding best practice: {e}")
            return False
    
    async def search_similar_responses(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar responses based on query."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        "id": doc_id,
                        "document": results['documents'][0][i] if results['documents'] else "",
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            logger.info(f"Found {len(formatted_results)} similar responses")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar responses: {e}")
            return []
    
    async def get_interview_responses(
        self, 
        interview_id: str
    ) -> List[Dict[str, Any]]:
        """Get all responses for a specific interview."""
        try:
            results = self.collection.get(
                where={"$and": [
                    {"interview_id": {"$eq": interview_id}},
                    {"response_type": {"$eq": "interview_response"}}
                ]}
            )
            
            formatted_results = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    formatted_results.append({
                        "id": doc_id,
                        "document": results['documents'][i] if results['documents'] else "",
                        "metadata": results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} responses for interview {interview_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error getting interview responses: {e}")
            return []
    
    async def get_best_practices_by_category(
        self, 
        category: str
    ) -> List[Dict[str, Any]]:
        """Get best practices for a specific category."""
        try:
            results = self.collection.get(
                where={"$and": [
                    {"category": {"$eq": category}},
                    {"response_type": {"$eq": "best_practice"}}
                ]}
            )
            
            formatted_results = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    formatted_results.append({
                        "id": doc_id,
                        "document": results['documents'][i] if results['documents'] else "",
                        "metadata": results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} best practices for category {category}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error getting best practices: {e}")
            return []
    
    async def batch_add_documents(
        self, 
        ids: List[str], 
        documents: List[str], 
        metadatas: List[Dict[str, Any]]
    ) -> bool:
        """Add multiple documents in batch."""
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(ids)} documents in batch")
            return True
            
        except Exception as e:
            logger.error(f"Error in batch add documents: {e}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a specific document."""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Successfully deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                "name": self.collection.name,
                "count": count,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}