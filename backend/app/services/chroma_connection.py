import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from fastapi import Depends
from dotenv import load_dotenv
import os

load_dotenv()

_client: ClientAPI | None = None
_collection: Collection | None = None

def get_chroma_client() -> ClientAPI:
    """Get or create ChromaDB client instance."""
    global _client
    if _client is None:
        # Use Chroma Cloud credentials exclusively
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT")
        database = os.getenv("CHROMA_DATABASE")

        if not (api_key and tenant and database):
            raise RuntimeError("Missing Chroma Cloud credentials. Set CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE")

        # Use HttpClient for Chroma Cloud with v2 API
        _client = chromadb.HttpClient(
            host="api.trychroma.com",
            port=443,
            ssl=True,
            tenant=tenant,
            database=database,
            headers={
                "X-Chroma-Token": api_key,
            }
        )
    return _client

def get_chroma_collection(client: ClientAPI = Depends(get_chroma_client)) -> Collection:
    """Get or create ChromaDB collection for interview data."""
    global _collection
    if _collection is None:
        _collection = client.get_or_create_collection(
            name="interview_responses",
            metadata={"description": "Interview responses and best practices"}
        )
    return _collection
