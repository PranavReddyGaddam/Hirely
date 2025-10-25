from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, interviews, analysis, chroma, scraper

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(chroma.router, prefix="/chroma", tags=["chromadb"])
api_router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])
# Voice endpoints depend on optional providers; include when available.
