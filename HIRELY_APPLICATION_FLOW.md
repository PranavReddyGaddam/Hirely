# Hirely Application Flow - ASCII Diagram

## 🏗️ **Complete System Architecture & User Flow**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                HIRELY PLATFORM                                 │
│                         AI-Powered Interview Preparation                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   FRONTEND                                     │
│                              React + TypeScript                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                USER JOURNEY                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

1. LANDING PAGE (/)
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │  • Hero Section: "Own the Interview, Every Time"                          │
   │  • Video Demo: Interview Clip 2.mp4 (800x500px)                          │
   │  • CTA Buttons: "Try Hirely" → /login (if not auth) or /interview/setup   │
   │  • Company Logos: Anthropic, Amazon, Google, Apple, etc.                 │
   │  • Navigation: Home, Demo, How it works                                   │
   └─────────────────────────────────────────────────────────────────────────────┘
   │
   ├─ Not Authenticated ──────────────────────────────────────────────────────────┐
   │  ┌─────────────────────────────────────────────────────────────────────────┐ │
   │  │ 2. AUTHENTICATION FLOW                                                 │ │
   │  │                                                                         │ │
   │  │ 2a. SIGNUP (/signup)                                                   │ │
   │  │    • Email, Password, Full Name                                        │ │
   │  │    • Show/Hide Password Toggle                                         │ │
   │  │    • POST /api/v1/auth/register                                        │ │
   │  │    • Redirect to /login after success                                  │ │
   │  │                                                                         │ │
   │  │ 2b. LOGIN (/login)                                                     │ │
   │  │    • Email, Password                                                  │ │
   │  │    • Show/Hide Password Toggle                                         │ │
   │  │    • POST /api/v1/auth/login                                           │ │
   │  │    • Store token in localStorage                                       │ │
   │  │    • Redirect to /interview/setup                                      │ │
   │  │                                                                         │ │
   │  │ 2c. FORGOT PASSWORD (/forgot-password)                                 │ │
   │  │    • Email input                                                      │ │
   │  │    • POST /api/v1/auth/forgot-password                                │ │
   │  │    • Supabase password reset email                                     │ │
   │  └─────────────────────────────────────────────────────────────────────────┘ │
   └─────────────────────────────────────────────────────────────────────────────┘
   │
   └─ Authenticated ──────────────────────────────────────────────────────────────┐
      ┌─────────────────────────────────────────────────────────────────────────┐ │
      │ 3. INTERVIEW SETUP (/interview/setup)                                  │ │
      │    • Company Name, Position Title                                      │ │
      │    • Job Description (optional)                                        │ │
      │    • Interview Type: behavioral, technical, mixed, etc.                 │ │
      │    • Focus Areas: Communication, Problem Solving, etc.                 │ │
      │    • Difficulty Level: easy, medium, hard                             │ │
      │    • Question Count: 5 (default)                                      │ │
      │    • POST /api/v1/interviews/setup                                     │ │
      │    • Redirect to /interview/{interviewId}                               │ │
      └─────────────────────────────────────────────────────────────────────────┘ │
      │                                                                           │
      │ ┌─────────────────────────────────────────────────────────────────────┐   │
      │ │ 4. INTERVIEW SESSION (/interview/{interviewId})                    │   │
      │ │                                                                     │   │
      │ │ 4a. QUESTION DISPLAY                                                │   │
      │ │    • Left Side: Question text, timers, controls                    │   │
      │ │    • Right Side: Camera feed (WebRTC)                              │   │
      │ │    • Preparation Timer: 20 seconds                                 │   │
      │ │    • Answer Timer: 90 seconds                                      │   │
      │ │                                                                     │   │
      │ │ 4b. QUESTION FLOW                                                   │   │
      │ │    • GET /api/v1/interviews/{id}/next_question                      │   │
      │ │    • Display question with timers                                  │   │
      │ │    • User answers (voice/video recording)                          │   │
      │ │    • POST /api/v1/interviews/{id}/submit_answer                    │   │
      │ │    • Move to next question                                          │   │
      │ │                                                                     │   │
      │ │ 4c. COMPLETION                                                      │   │
      │ │    • POST /api/v1/interviews/{id}/complete                          │   │
      │ │    • Redirect to /interview/{id}/report                            │   │
      │ └─────────────────────────────────────────────────────────────────────┘   │
      │                                                                           │
      │ ┌─────────────────────────────────────────────────────────────────────┐   │
      │ │ 5. INTERVIEW REPORT (/interview/{interviewId}/report)              │   │
      │ │    • "Interview completed successfully!"                            │   │
      │ │    • "Analysis coming soon" message                                │   │
      │ │    • Navigation: Start New Interview, Back to Home                 │   │
      │ └─────────────────────────────────────────────────────────────────────┘   │
      │                                                                           │
      │ ┌─────────────────────────────────────────────────────────────────────┐   │
      │ │ 6. PROFILE DASHBOARD (/profile)                                    │   │
      │ │                                                                     │   │
      │ │ 6a. PROFILE TAB                                                     │   │
      │ │    • User Information Display                                      │   │
      │ │    • Password Change Form                                          │   │
      │ │    • Account Settings                                              │   │
      │ │                                                                     │   │
      │ │ 6b. ANALYTICS TAB                                                   │   │
      │ │    • Total Interviews: 12                                          │   │
      │ │    • Average Score: 87%                                            │   │
      │ │    • Improvement Rate: 15%                                         │   │
      │ │    • Time Spent: 180 minutes                                       │   │
      │ │    • Strengths: Communication, Problem Solving                     │   │
      │ │    • Areas for Improvement: Time Management, Confidence           │   │
      │ │    • Recent Interviews Table                                       │   │
      │ │                                                                     │   │
      │ │ 6c. SETTINGS TAB                                                    │   │
      │ │    • Password Change (with validation)                             │   │
      │ │    • Account Information                                           │   │
      │ │    • Preferences                                                   │   │
      │ └─────────────────────────────────────────────────────────────────────┘   │
      └───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   BACKEND                                      │
│                              FastAPI + Python                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                API ENDPOINTS                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

AUTHENTICATION (/api/v1/auth/)
├─ POST /register          → Create new user account
├─ POST /login            → Authenticate user, return JWT token
├─ POST /logout           → Invalidate user session
├─ POST /forgot-password  → Send password reset email
└─ POST /change-password  → Update user password

USERS (/api/v1/users/)
├─ GET  /me              → Get current user profile
├─ PUT  /me              → Update user profile
└─ DELETE /me            → Delete user account

INTERVIEWS (/api/v1/interviews/)
├─ POST /setup           → Create interview with custom parameters
├─ GET  /                → List user interviews
├─ GET  /{id}            → Get specific interview
├─ DELETE /{id}          → Delete interview
├─ GET  /{id}/next_question     → Get next question
├─ POST /{id}/submit_answer     → Submit answer
├─ POST /{id}/complete          → Mark interview complete
├─ POST /{id}/upload           → Upload interview video
└─ GET  /{id}/debug            → Debug interview data

ANALYSIS (/api/v1/analysis/)
├─ POST /start            → Start AI analysis
├─ GET  /{id}             → Get analysis results
├─ GET  /interview/{id}/latest → Get latest analysis for interview
└─ POST /{id}/regenerate  → Regenerate analysis

CHROMADB (/api/v1/chroma/)
├─ POST /documents/       → Add documents to vector DB
├─ POST /interview-response/ → Store interview responses
├─ POST /best-practice/   → Add best practices
├─ POST /search/          → Search similar responses
├─ GET  /interview/{id}/responses → Get interview responses
├─ GET  /best-practices/{category} → Get best practices by category
├─ DELETE /document/{id}  → Delete document
├─ GET  /collection/info  → Get collection info
└─ GET  /health           → ChromaDB health check

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                SERVICES                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

AUTHENTICATION SERVICE
├─ Supabase Integration
├─ JWT Token Management
├─ Password Hashing
├─ Email Verification
└─ Password Reset

INTERVIEW SERVICE
├─ Question Generation (Groq LLM)
├─ Interview Session Management
├─ In-Memory Storage (active interviews)
├─ Question Flow Control
└─ Response Collection

GROQ SERVICE
├─ LLM Integration (gpt-oss-20b)
├─ Question Generation
├─ Structured Output Parsing
├─ Follow-up Questions
└─ Context-Aware Responses

CHROMADB SERVICE
├─ Vector Database Operations
├─ Document Storage
├─ Similarity Search
├─ Best Practices Storage
└─ Interview Response Analysis

SUPABASE SERVICE
├─ Database Operations
├─ User Management
├─ Row Level Security (RLS)
├─ Email Services
└─ Authentication

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                         │
└─────────────────────────────────────────────────────────────────────────────────┘

INTERVIEW CREATION FLOW
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. User fills interview setup form                                             │
│ 2. POST /api/v1/interviews/setup                                              │
│ 3. InterviewService.create_interview()                                        │
│ 4. Store interview in Supabase DB                                             │
│ 5. GroqService.generate_initial_questions()                                   │
│ 6. Store questions in memory (active_interviews)                              │
│ 7. Return interview with questions                                             │
│ 8. Redirect to interview session                                               │
└─────────────────────────────────────────────────────────────────────────────────┘

INTERVIEW SESSION FLOW
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. GET /api/v1/interviews/{id}/next_question                                  │
│ 2. Retrieve question from memory (active_interviews)                          │
│ 3. Display question with timers                                               │
│ 4. User answers (voice/video)                                                 │
│ 5. POST /api/v1/interviews/{id}/submit_answer                                     │
│ 6. Store response in memory                                                   │
│ 7. Increment question index                                                    │
│ 8. Repeat until all questions answered                                         │
│ 9. POST /api/v1/interviews/{id}/complete                                       │
│ 10. Store all questions/responses in DB for analytics                          │
│ 11. Remove from active_interviews                                              │
│ 12. Redirect to report page                                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY & MONITORING                            │
└─────────────────────────────────────────────────────────────────────────────────┘

AUTHENTICATION & AUTHORIZATION
├─ JWT Token-based authentication
├─ Protected routes (ProtectedRoute component)
├─ Token validation on each request
├─ Automatic logout on token expiry
└─ Row Level Security (RLS) in Supabase

BACKEND HEALTH MONITORING
├─ Health check endpoint (/health)
├─ Frontend monitoring (every 10 seconds)
├─ Automatic logout on backend restart
├─ User notifications for server issues
└─ Connection status tracking

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FUTURE FEATURES                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

VAPI INTEGRATION (Planned)
├─ Conversational AI interviews
├─ Natural topic transitions
├─ Voice-first interface
├─ Real-time conversation flow
└─ Seamless user experience

VIDEO/AUDIO INTERFACE (Planned)
├─ Camera access and display
├─ Audio recording capabilities
├─ Real-time video processing
├─ Interview session recording
└─ Analysis integration

ADVANCED ANALYTICS (Planned)
├─ Interactive charts and graphs
├─ Performance trend analysis
├─ Detailed feedback reports
├─ Progress tracking
└─ Personalized recommendations

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TECHNICAL STACK                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

FRONTEND
├─ React 18 + TypeScript
├─ React Router DOM
├─ Tailwind CSS
├─ Lucide React (icons)
├─ Custom hooks (useAuth)
├─ Context providers (Auth, Notification)
└─ Responsive design

BACKEND
├─ FastAPI (Python)
├─ Uvicorn ASGI server
├─ Pydantic models
├─ SQLAlchemy (planned)
├─ JWT authentication
└─ CORS middleware

DATABASES
├─ Supabase (PostgreSQL)
├─ ChromaDB (Vector database)
├─ Row Level Security
└─ Real-time subscriptions

AI/ML SERVICES
├─ Groq LLM (gpt-oss-20b)
├─ Question generation
├─ Response analysis
├─ Vector embeddings
└─ Similarity search

EXTERNAL SERVICES
├─ Supabase Auth
├─ Supabase Database
├─ Groq API
├─ ChromaDB Cloud
└─ Email services

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CURRENT STATUS                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

✅ COMPLETED FEATURES
├─ User authentication (signup, login, logout)
├─ Password reset functionality
├─ Interview setup and customization
├─ Question generation with Groq
├─ Interview session management
├─ Profile dashboard with analytics
├─ Password change functionality
├─ Backend health monitoring
├─ Automatic logout on server restart
├─ ChromaDB integration
├─ Glassmorphic UI design
└─ Responsive layout

🚧 IN PROGRESS
├─ Interview video/audio interface
├─ VAPI conversational integration
├─ Advanced analytics dashboard
└─ Real-time features

📋 PLANNED
├─ Video analysis and feedback
├─ Advanced reporting
├─ Performance optimization
├─ Mobile app development
└─ Enterprise features

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DEPLOYMENT                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

DEVELOPMENT
├─ Frontend: npm run dev (localhost:5173)
├─ Backend: python start_server.py (localhost:8000)
├─ Hot reload enabled
├─ CORS configured
└─ Environment variables

PRODUCTION (Planned)
├─ Frontend: Vercel/Netlify deployment
├─ Backend: Railway/Heroku deployment
├─ Database: Supabase Cloud
├─ Vector DB: ChromaDB Cloud
└─ CDN for static assets

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FILE STRUCTURE                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

frontend/
├─ src/
│  ├─ components/          # Reusable UI components
│  │  ├─ Header.tsx        # Navigation header
│  │  ├─ Footer.tsx        # Footer component
│  │  ├─ InterviewReport.tsx # Interview completion page
│  │  └─ Notification.tsx  # Toast notifications
│  ├─ pages/              # Main application pages
│  │  ├─ Login.tsx         # User login
│  │  ├─ Signup.tsx        # User registration
│  │  ├─ ForgotPassword.tsx # Password reset
│  │  ├─ InterviewSetup.tsx # Interview configuration
│  │  ├─ InterviewSession.tsx # Active interview
│  │  └─ Profile.tsx       # User dashboard
│  ├─ hooks/              # Custom React hooks
│  │  └─ useAuth.ts        # Authentication logic
│  ├─ contexts/           # React contexts
│  │  ├─ AuthContext.tsx  # Authentication state
│  │  └─ NotificationContext.tsx # Notifications
│  ├─ lib/                # Utility functions
│  │  └─ utils.ts         # Helper functions
│  └─ App.tsx             # Main application component
├─ public/                # Static assets
│  ├─ Interview Clip 1.mp4 # Demo video 1
│  ├─ Interview Clip 2.mp4 # Demo video 2
│  ├─ mountains.png        # Background image
│  └─ logos/              # Company logos
└─ package.json           # Dependencies

backend/
├─ app/
│  ├─ api/v1/endpoints/   # API route handlers
│  │  ├─ auth.py          # Authentication endpoints
│  │  ├─ users.py         # User management
│  │  ├─ interviews.py    # Interview operations
│  │  ├─ analysis.py      # AI analysis
│  │  └─ chroma.py        # Vector database
│  ├─ services/           # Business logic
│  │  ├─ auth_service.py  # Authentication logic
│  │  ├─ interview_service.py # Interview management
│  │  ├─ groq_service.py  # LLM integration
│  │  ├─ chroma_service.py # Vector DB operations
│  │  └─ supabase_service.py # Database operations
│  ├─ core/               # Core functionality
│  │  ├─ config.py        # Configuration
│  │  └─ auth.py          # Authentication utilities
│  ├─ schemas/            # Pydantic models
│  └─ utils/              # Utility functions
├─ main.py                # FastAPI application
├─ start_server.py        # Server startup script
└─ requirements.txt       # Python dependencies

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              INTEGRATION POINTS                               │
└─────────────────────────────────────────────────────────────────────────────────┘

SUPABASE INTEGRATION
├─ Authentication (signup, login, password reset)
├─ Database operations (CRUD)
├─ Row Level Security (RLS)
├─ Real-time subscriptions
└─ Email services

GROQ INTEGRATION
├─ Question generation
├─ Structured output parsing
├─ Context-aware responses
├─ Follow-up questions
└─ Interview customization

CHROMADB INTEGRATION
├─ Vector storage
├─ Similarity search
├─ Best practices storage
├─ Interview response analysis
└─ Cloud connectivity

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ERROR HANDLING                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

FRONTEND ERROR HANDLING
├─ Network error detection
├─ Authentication error handling
├─ Form validation
├─ User-friendly error messages
└─ Automatic retry mechanisms

BACKEND ERROR HANDLING
├─ HTTP status codes
├─ Detailed error messages
├─ Logging and monitoring
├─ Graceful degradation
└─ Health check endpoints

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TESTING STRATEGY                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

FRONTEND TESTING
├─ Component testing
├─ Integration testing
├─ User flow testing
├─ Responsive design testing
└─ Cross-browser compatibility

BACKEND TESTING
├─ API endpoint testing
├─ Authentication testing
├─ Database integration testing
├─ Service layer testing
└─ Error scenario testing

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PERFORMANCE OPTIMIZATION                         │
└─────────────────────────────────────────────────────────────────────────────────┘

FRONTEND OPTIMIZATION
├─ Code splitting
├─ Lazy loading
├─ Image optimization
├─ Bundle size optimization
└─ Caching strategies

BACKEND OPTIMIZATION
├─ Database query optimization
├─ Caching mechanisms
├─ Connection pooling
├─ Async operations
└─ Resource management

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY MEASURES                                │
└─────────────────────────────────────────────────────────────────────────────────┘

AUTHENTICATION SECURITY
├─ JWT token expiration
├─ Secure token storage
├─ Password hashing
├─ CSRF protection
└─ Rate limiting

DATA SECURITY
├─ Input validation
├─ SQL injection prevention
├─ XSS protection
├─ HTTPS enforcement
└─ Data encryption

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MONITORING & ANALYTICS                           │
└─────────────────────────────────────────────────────────────────────────────────┘

APPLICATION MONITORING
├─ Backend health checks
├─ Performance metrics
├─ Error tracking
├─ User activity monitoring
└─ System resource monitoring

BUSINESS ANALYTICS
├─ User engagement metrics
├─ Interview completion rates
├─ Performance trends
├─ Feature usage statistics
└─ Conversion tracking

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SCALABILITY CONSIDERATIONS                       │
└─────────────────────────────────────────────────────────────────────────────────┘

HORIZONTAL SCALING
├─ Stateless backend design
├─ Database connection pooling
├─ Load balancing
├─ CDN integration
└─ Microservices architecture

VERTICAL SCALING
├─ Resource optimization
├─ Caching strategies
├─ Database indexing
├─ Query optimization
└─ Memory management

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MAINTENANCE & UPDATES                            │
└─────────────────────────────────────────────────────────────────────────────────┘

CODE MAINTENANCE
├─ Regular dependency updates
├─ Security patches
├─ Performance optimizations
├─ Bug fixes
└─ Feature enhancements

DEPLOYMENT UPDATES
├─ Zero-downtime deployments
├─ Database migrations
├─ Feature flags
├─ Rollback strategies
└─ Monitoring and alerting

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DOCUMENTATION                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

TECHNICAL DOCUMENTATION
├─ API documentation (Swagger/OpenAPI)
├─ Code comments and docstrings
├─ Architecture diagrams
├─ Deployment guides
└─ Troubleshooting guides

USER DOCUMENTATION
├─ User guides
├─ FAQ sections
├─ Video tutorials
├─ Best practices
└─ Support resources

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONCLUSION                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

The Hirely platform is a comprehensive AI-powered interview preparation system with:

✅ COMPLETE USER AUTHENTICATION FLOW
✅ INTERVIEW SETUP AND CUSTOMIZATION
✅ AI-POWERED QUESTION GENERATION
✅ INTERACTIVE INTERVIEW SESSIONS
✅ USER PROFILE AND ANALYTICS
✅ VECTOR DATABASE INTEGRATION
✅ BACKEND HEALTH MONITORING
✅ AUTOMATIC SESSION MANAGEMENT

🚧 PLANNED ENHANCEMENTS
├─ VAPI conversational interviews
├─ Video/audio interface
├─ Advanced analytics
├─ Real-time features
└─ Performance optimizations

The system is built with modern technologies, follows best practices, and is designed for scalability and maintainability.
