from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, interviews, analysis, chroma, scraper, elevenlabs, cv_tracking, video_analysis, video_upload, interview_analysis  # voice disabled - missing vapi dependency

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(chroma.router, prefix="/chroma", tags=["chromadb"])
api_router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])
# api_router.include_router(voice.router, prefix="/voice", tags=["voice"])  # Disabled - VAPI not installed
api_router.include_router(elevenlabs.router, prefix="/elevenlabs", tags=["elevenlabs"])
api_router.include_router(cv_tracking.router, tags=["cv-tracking"])
api_router.include_router(video_analysis.router, tags=["video-analysis"])
api_router.include_router(video_upload.router, prefix="/video", tags=["video-upload"])
api_router.include_router(interview_analysis.router, prefix="/interview-analysis", tags=["interview-analysis"])
