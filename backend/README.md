# Hirely Backend API

AI-Powered Interview Analysis Platform Backend built with FastAPI.

## Features

- **Authentication & Authorization** - JWT-based user authentication with Supabase
- **Interview Management** - Create, manage, and track interview sessions
- **Real-Time Voice Interaction** - Dual voice processing options:
  - **WebSocket Streaming** - Deepgram for real-time transcription
  - **Phone Integration** - Vapi for voice AI phone calls
- **AI Analysis** - Multi-modal analysis using:
  - **Speech Analysis** - Deepgram for transcription and speech patterns
  - **Content Analysis** - Groq for intelligent feedback and question generation
  - **Hybrid Question Generation** - Initial questions + dynamic follow-ups
- **Vector Database** - ChromaDB for dual-purpose embeddings:
  - **User History** - Store and retrieve user's past interview responses
  - **Best Practices** - Semantic search for interview guidance
- **Personalized Feedback** - AI-powered recommendations using user history
- **Report Generation** - PDF, HTML, and JSON reports with analysis results

## Tech Stack

- **FastAPI** - Modern, fast web framework with WebSocket support
- **ChromaDB** - Vector database for embeddings and semantic search
- **Supabase** - PostgreSQL database and authentication
- **Groq** - Fast LLM inference for question generation and analysis
- **OpenAI** - Text embeddings for ChromaDB integration
- **Deepgram** - Real-time speech-to-text transcription
- **Vapi** - Voice AI platform for phone-based interviews
- **ReportLab** - PDF report generation
- **Jinja2** - HTML template rendering

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run the Server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/     # API route handlers
│   │   │   ├── auth.py    # Authentication endpoints
│   │   │   ├── users.py   # User management endpoints
│   │   │   ├── interviews.py # Interview session endpoints
│   │   │   ├── analysis.py   # Analysis endpoints
│   │   │   └── voice.py      # Voice interaction endpoints
│   │   └── api.py        # Router configuration
│   ├── core/             # Core configuration
│   │   ├── config.py     # Environment variables and settings
│   │   └── auth.py       # JWT authentication utilities
│   ├── schemas/          # Pydantic schemas
│   │   ├── auth.py       # Authentication schemas
│   │   ├── user.py       # User schemas
│   │   ├── interview.py  # Interview schemas
│   │   ├── analysis.py   # Analysis schemas
│   │   └── voice.py      # Voice interaction schemas
│   ├── services/         # Business logic services
│   │   ├── supabase_service.py    # Database operations
│   │   ├── auth_service.py        # Authentication logic
│   │   ├── user_service.py        # User management
│   │   ├── interview_service.py   # Interview management
│   │   ├── analysis_service.py    # Analysis orchestration
│   │   ├── groq_service.py        # Groq LLM integration
│   │   ├── chroma_service.py      # ChromaDB operations
│   │   ├── deepgram_service.py    # Deepgram voice processing
│   │   ├── vapi_service.py        # Vapi voice AI integration
│   │   └── report_service.py      # Report generation
│   └── utils/            # Utility functions
│       ├── logger.py     # Centralized logging
│       └── embeddings.py # OpenAI embeddings utility
├── tests/                # Test files
├── main.py              # FastAPI application
└── requirements.txt     # Dependencies
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `DELETE /api/v1/users/me` - Delete user account

### Interviews
- `POST /api/v1/interviews/` - Create new interview
- `GET /api/v1/interviews/` - Get user interviews
- `GET /api/v1/interviews/{id}` - Get specific interview
- `POST /api/v1/interviews/{id}/upload` - Upload interview video
- `DELETE /api/v1/interviews/{id}` - Delete interview

### Analysis
- `POST /api/v1/analysis/start` - Start interview analysis
- `GET /api/v1/analysis/{id}` - Get analysis results
- `GET /api/v1/analysis/interview/{id}/latest` - Get latest analysis
- `POST /api/v1/analysis/{id}/regenerate` - Regenerate analysis

### Voice Interaction
- `WebSocket /api/v1/voice/stream/{session_id}` - Real-time voice streaming
- `POST /api/v1/voice/session/start` - Start voice session
- `POST /api/v1/voice/vapi/call` - Create Vapi phone call
- `GET /api/v1/voice/vapi/call/{id}/status` - Get call status
- `POST /api/v1/voice/vapi/call/{id}/end` - End call
- `GET /api/v1/voice/vapi/call/{id}/transcript` - Get call transcript
- `GET /api/v1/voice/vapi/call/{id}/recording` - Get call recording

## Development

- **Run Tests**: `pytest`
- **Code Formatting**: `black .`
- **Type Checking**: `mypy .`
