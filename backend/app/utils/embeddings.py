"""
Text embedding utilities using OpenAI for ChromaDB integration.
"""
from typing import List, Optional
import openai
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not configured")
            self.client = None
    
    async def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            model: OpenAI embedding model to use
            
        Returns:
            List[float]: Embedding vector or None if failed
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        try:
            # TODO: OPENAI - Implement actual embedding generation
            response = self.client.embeddings.create(
                input=text,
                model=model
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def generate_embeddings_batch(self, texts: List[str], model: str = "text-embedding-3-small") -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            model: OpenAI embedding model to use
            
        Returns:
            List[Optional[List[float]]]: List of embedding vectors
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return [None] * len(texts)
        
        try:
            # TODO: OPENAI - Implement batch embedding generation
            response = self.client.embeddings.create(
                input=texts,
                model=model
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)
    
    async def get_embedding_dimension(self, model: str = "text-embedding-3-small") -> int:
        """
        Get the dimension of embeddings for a model.
        
        Args:
            model: OpenAI embedding model
            
        Returns:
            int: Embedding dimension
        """
        # Model dimensions mapping
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        
        return dimensions.get(model, 1536)


# Global embedding service instance
embedding_service = EmbeddingService()
