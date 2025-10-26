# Hirely - AI-Powered Interview Analysis Platform

Hirely is a comprehensive interview analysis platform that combines AI-powered job market analysis with advanced interview preparation tools. The platform features real-time job scraping, skills analysis, and intelligent interview question generation.

## Features

### Job Market Analysis
- **Real-time Job Scraping**: Extract job postings from LinkedIn using BrightData MCP integration
- **Skills Analysis**: Comprehensive extraction and analysis of technical skills from job descriptions
- **Market Insights**: AI-powered analysis of job market trends and skill demand
- **Company Research**: Detailed analysis of specific companies and their hiring patterns

### Interview Preparation
- **Dynamic Question Generation**: Generate interview questions based on real job requirements
- **Skills-based Preparation**: Focus on the most in-demand skills for your target role
- **Study Guides**: Comprehensive study materials with practice plans
- **Career Recommendations**: AI-powered insights for career development

### Technical Capabilities
- **Multi-source Data**: Combines Crawl4AI and BrightData MCP for comprehensive data collection
- **AI Integration**: Powered by Groq for intelligent analysis and insights
- **RESTful API**: Complete API for frontend integration
- **Authentication**: Secure user authentication and authorization

## Architecture

```
Frontend (React/TypeScript)
    ↓
Backend API (FastAPI)
    ↓
Services Layer
    ├── Job Scraping (BrightData MCP + Crawl4AI)
    ├── Skills Analysis
    ├── AI Analysis (Groq)
    └── Interview Preparation
    ↓
Data Storage (Supabase + ChromaDB)
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- Supabase account
- BrightData MCP API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Calhacks/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Start the server**
   ```bash
   python start_server.py
   ```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`.

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Job Analysis
- `POST /api/v1/job-analysis/scrape-jobs` - Scrape job listings
- `POST /api/v1/job-analysis/scrape-jobs-with-skills` - Scrape jobs with skills analysis
- `POST /api/v1/job-analysis/analyze-job-market` - Comprehensive market analysis
- `POST /api/v1/job-analysis/generate-interview-prep` - Generate interview preparation
- `GET /api/v1/job-analysis/job-market-insights` - Get market insights

### Interview Management
- `POST /api/v1/interviews/create` - Create new interview
- `GET /api/v1/interviews/` - List user interviews
- `POST /api/v1/interview-analysis/analyze` - Analyze interview performance

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# AI Services
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# BrightData MCP
BRIGHTDATA_API_TOKEN=your_brightdata_token

# AWS (optional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your_s3_bucket

# Security
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### MCP Configuration

Configure BrightData MCP in `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "brightdata-mcp": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "your_brightdata_token"
      }
    }
  }
}
```

## Usage Examples

### Job Scraping with Skills Analysis

```python
from app.services.brightdata_mcp_service import BrightDataMCPService

service = BrightDataMCPService()
result = await service.scrape_jobs_with_skills_analysis(
    keywords="software engineer",
    location="San Francisco",
    max_results=10
)

# Get skills insights
insights = service.get_skills_insights(result['skills_analysis'])
print(f"Top skills: {insights['top_skills']}")
```

### Interview Preparation

```python
from app.services.job_market_analyzer import JobMarketAnalyzer

analyzer = JobMarketAnalyzer()
prep = await analyzer.generate_interview_prep(
    job_title="software engineer",
    location="San Francisco",
    prep_type="comprehensive"
)

print(f"Generated {prep['job_data']['total_questions']} questions")
```

### API Usage

```bash
# Get authentication token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_email&password=your_password"

# Scrape jobs with skills analysis
curl -X POST "http://localhost:8000/api/v1/job-analysis/scrape-jobs-with-skills" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "software engineer", "location": "San Francisco", "max_results": 10}'
```

## Testing

Run the test suite:

```bash
# Backend tests
cd backend
python -m pytest tests/

# Skills analysis tests
python test_skills_analysis.py

# Integration tests
python test_brightdata_integration.py
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core configuration
│   ├── services/             # Business logic services
│   ├── schemas/              # Pydantic models
│   └── utils/                # Utility functions
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
└── main.py                   # FastAPI application

frontend/
├── src/
│   ├── components/           # React components
│   ├── pages/               # Page components
│   ├── services/            # API services
│   └── contexts/            # React contexts
├── package.json             # Node.js dependencies
└── vite.config.ts           # Vite configuration
```

### Adding New Features

1. **Backend**: Add new services in `app/services/` and endpoints in `app/api/v1/endpoints/`
2. **Frontend**: Add new components in `src/components/` and pages in `src/pages/`
3. **Database**: Update schemas in `app/schemas/` and run migrations
4. **Testing**: Add tests in the `tests/` directory

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `http://localhost:8000/docs`
- Review the test files for usage examples
