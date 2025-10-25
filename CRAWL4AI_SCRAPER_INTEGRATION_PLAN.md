# Crawl4AI Scraper Integration Plan - Interview Questions Collection

## Overview
This document outlines the integration of Crawl4AI to scrape and collect relevant interview questions for similar roles from various sources over the past year. This will enhance our question database with real-world, up-to-date interview questions.

## Current State vs Desired State

### Current State ❌
- Limited question database (only Groq-generated questions)
- No real-world interview question data
- Static question patterns
- Limited industry-specific insights

### Desired State ✅
- Comprehensive question database from real interviews
- Industry-specific question collections
- Historical question trends
- Enhanced question relevance and authenticity

## Hackathon Day Tasks

### 1. Crawl4AI Setup and Configuration

#### 1.1 Crawl4AI Installation and Setup
**Priority: HIGH**
- **Task**: Install and configure Crawl4AI
- **Requirements**:
  - Crawl4AI package installation
  - Browser automation setup
  - Proxy configuration (if needed)
  - Rate limiting configuration

#### 1.2 Scraper Service Implementation
**Priority: HIGH**
- **Task**: Create scraper service for interview questions
- **Location**: `backend/app/services/scraper_service.py`
- **Implementation**:
  ```python
  import asyncio
  from crawl4ai import AsyncWebCrawler
  from typing import List, Dict, Any
  import logging
  from datetime import datetime, timedelta
  import re
  from bs4 import BeautifulSoup

  class InterviewQuestionScraper:
      def __init__(self):
          self.crawler = AsyncWebCrawler()
          self.target_sites = [
              "https://leetcode.com/discuss/interview-question/",
              "https://www.glassdoor.com/Interview/",
              "https://www.indeed.com/career-advice/interviewing/",
              "https://www.interviewbit.com/",
              "https://www.hackerrank.com/interview/interview-preparation-kit",
              "https://www.geeksforgeeks.org/",
              "https://www.careercup.com/",
              "https://www.interviewcake.com/"
          ]
          self.question_patterns = [
              r"Tell me about yourself",
              r"Describe a time when",
              r"How would you handle",
              r"What is your greatest",
              r"Explain the difference between",
              r"Write a function to",
              r"Design a system",
              r"How do you approach"
          ]
      
      async def scrape_questions_for_role(self, role: str, company: str = None) -> List[Dict[str, Any]]:
          """Scrape interview questions for a specific role"""
          questions = []
          
          for site in self.target_sites:
              try:
                  # Construct search URLs
                  search_urls = self._build_search_urls(site, role, company)
                  
                  for url in search_urls:
                      result = await self.crawler.arun(url=url)
                      if result.success:
                          extracted_questions = self._extract_questions(result.html, role)
                          questions.extend(extracted_questions)
                          
              except Exception as e:
                  logging.error(f"Error scraping {site}: {e}")
                  continue
          
          return self._deduplicate_and_rank_questions(questions)
  ```

#### 1.3 Question Extraction and Processing
**Priority: HIGH**
- **Task**: Extract and process interview questions from scraped content
- **Implementation**:
  ```python
  def _extract_questions(self, html_content: str, role: str) -> List[Dict[str, Any]]:
      """Extract interview questions from HTML content"""
      soup = BeautifulSoup(html_content, 'html.parser')
      questions = []
      
      # Find question containers
      question_containers = soup.find_all(['div', 'p', 'li'], class_=re.compile(r'question|interview|ask'))
      
      for container in question_containers:
          text = container.get_text().strip()
          if self._is_valid_question(text):
              question_data = {
                  'question_text': text,
                  'role': role,
                  'source': self._extract_source(container),
                  'date_posted': self._extract_date(container),
                  'difficulty': self._classify_difficulty(text),
                  'category': self._classify_category(text),
                  'company': self._extract_company(container),
                  'scraped_at': datetime.utcnow().isoformat()
              }
              questions.append(question_data)
      
      return questions
  ```

### 2. Data Storage and Management

#### 2.1 Database Schema Updates
**Priority: HIGH**
- **Task**: Create tables for scraped questions
- **Location**: `backend/app/schemas/scraper.py`
- **Implementation**:
  ```python
  from pydantic import BaseModel
  from typing import Optional, List
  from datetime import datetime
  from enum import Enum

  class QuestionCategory(str, Enum):
      BEHAVIORAL = "behavioral"
      TECHNICAL = "technical"
      SYSTEM_DESIGN = "system_design"
      CODING = "coding"
      LEADERSHIP = "leadership"
      CULTURAL = "cultural"

  class QuestionDifficulty(str, Enum):
      EASY = "easy"
      MEDIUM = "medium"
      HARD = "hard"

  class ScrapedQuestion(BaseModel):
      id: Optional[str] = None
      question_text: str
      role: str
      company: Optional[str] = None
      source: str
      date_posted: Optional[datetime] = None
      difficulty: QuestionDifficulty
      category: QuestionCategory
      scraped_at: datetime
      is_verified: bool = False
      usage_count: int = 0
      relevance_score: float = 0.0

  class ScrapingJob(BaseModel):
      id: str
      role: str
      company: Optional[str] = None
      status: str  # pending, running, completed, failed
      questions_found: int = 0
      started_at: datetime
      completed_at: Optional[datetime] = None
      error_message: Optional[str] = None
  ```

#### 2.2 Supabase Integration
**Priority: HIGH**
- **Task**: Store scraped questions in Supabase
- **Location**: `backend/app/services/scraper_service.py`
- **Implementation**:
  ```python
  class ScraperService:
      def __init__(self):
          self.supabase_service = SupabaseService()
          self.scraper = InterviewQuestionScraper()
      
      async def scrape_and_store_questions(self, role: str, company: str = None) -> Dict[str, Any]:
          """Scrape questions and store in database"""
          try:
              # Start scraping job
              job_id = str(uuid.uuid4())
              await self._create_scraping_job(job_id, role, company)
              
              # Scrape questions
              questions = await self.scraper.scrape_questions_for_role(role, company)
              
              # Store questions in database
              stored_count = 0
              for question in questions:
                  success = await self._store_question(question)
                  if success:
                      stored_count += 1
              
              # Update job status
              await self._update_scraping_job(job_id, "completed", stored_count)
              
              return {
                  "job_id": job_id,
                  "questions_found": len(questions),
                  "questions_stored": stored_count,
                  "status": "completed"
              }
              
          except Exception as e:
              logging.error(f"Scraping job failed: {e}")
              await self._update_scraping_job(job_id, "failed", 0, str(e))
              raise
  ```

### 3. API Integration

#### 3.1 Scraper API Endpoints
**Priority: HIGH**
- **Task**: Create API endpoints for scraper operations
- **Location**: `backend/app/api/v1/endpoints/scraper.py`
- **Implementation**:
  ```python
  from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
  from pydantic import BaseModel
  from typing import Optional
  from app.services.scraper_service import ScraperService
  from app.core.auth import get_current_user

  router = APIRouter()

  class ScrapingRequest(BaseModel):
      role: str
      company: Optional[str] = None
      max_questions: int = 100

  class ScrapingResponse(BaseModel):
      job_id: str
      status: str
      message: str

  @router.post("/start", response_model=ScrapingResponse)
  async def start_scraping(
      request: ScrapingRequest,
      background_tasks: BackgroundTasks,
      current_user = Depends(get_current_user)
  ):
      """Start scraping interview questions for a role"""
      try:
          scraper_service = ScraperService()
          
          # Start background scraping task
          background_tasks.add_task(
              scraper_service.scrape_and_store_questions,
              request.role,
              request.company
          )
          
          return ScrapingResponse(
              job_id=str(uuid.uuid4()),
              status="started",
              message="Scraping job started in background"
          )
          
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))

  @router.get("/jobs/{job_id}")
  async def get_scraping_job_status(
      job_id: str,
      current_user = Depends(get_current_user)
  ):
      """Get scraping job status"""
      try:
          scraper_service = ScraperService()
          job_status = await scraper_service.get_scraping_job_status(job_id)
          return job_status
      except Exception as e:
          raise HTTPException(status_code=404, detail="Job not found")

  @router.get("/questions/{role}")
  async def get_scraped_questions(
      role: str,
      company: Optional[str] = None,
      limit: int = 50,
      current_user = Depends(get_current_user)
  ):
      """Get scraped questions for a role"""
      try:
          scraper_service = ScraperService()
          questions = await scraper_service.get_questions_for_role(role, company, limit)
          return {"questions": questions, "total": len(questions)}
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  ```

### 4. Integration with Existing System

#### 4.1 Enhanced Question Generation
**Priority: MEDIUM**
- **Task**: Integrate scraped questions with Groq generation
- **Location**: `backend/app/services/groq_service.py`
- **Implementation**:
  ```python
  class EnhancedGroqService:
      def __init__(self):
          self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
          self.scraper_service = ScraperService()
      
      async def generate_enhanced_questions(
          self,
          interview_type: str,
          job_description: str,
          position_title: str,
          company_name: str,
          num_questions: int = 5,
          focus_areas: List[str] = None,
          difficulty_level: str = "medium"
      ) -> List[Dict[str, Any]]:
          """Generate questions using both Groq and scraped data"""
          
          # Get scraped questions for the role
          scraped_questions = await self.scraper_service.get_questions_for_role(
              position_title, company_name, limit=20
          )
          
          # Create enhanced prompt with scraped context
          prompt = self._build_enhanced_prompt(
              interview_type, job_description, position_title,
              company_name, scraped_questions, focus_areas, difficulty_level
          )
          
          # Generate questions with Groq
          response = await self.groq_client.chat.completions.create(
              model="gpt-oss-20b",
              messages=[{"role": "user", "content": prompt}],
              temperature=0.7
          )
          
          return self._parse_enhanced_questions(response.choices[0].message.content)
  ```

#### 4.2 Question Ranking and Selection
**Priority: MEDIUM**
- **Task**: Implement intelligent question selection
- **Implementation**:
  ```python
  class QuestionRanker:
      def __init__(self):
          self.ranking_factors = {
              'relevance': 0.3,
              'difficulty': 0.2,
              'recency': 0.2,
              'usage_frequency': 0.1,
              'company_match': 0.1,
              'category_balance': 0.1
          }
      
      def rank_questions(self, questions: List[Dict], criteria: Dict) -> List[Dict]:
          """Rank questions based on multiple factors"""
          for question in questions:
              score = 0
              
              # Relevance score
              score += self._calculate_relevance(question, criteria) * 0.3
              
              # Difficulty match
              score += self._calculate_difficulty_match(question, criteria) * 0.2
              
              # Recency score
              score += self._calculate_recency(question) * 0.2
              
              # Usage frequency
              score += self._calculate_usage_frequency(question) * 0.1
              
              # Company match
              score += self._calculate_company_match(question, criteria) * 0.1
              
              # Category balance
              score += self._calculate_category_balance(question, criteria) * 0.1
              
              question['relevance_score'] = score
          
          return sorted(questions, key=lambda x: x['relevance_score'], reverse=True)
  ```

### 5. Frontend Integration

#### 5.1 Scraper Management Interface
**Priority: MEDIUM**
- **Task**: Create admin interface for scraper management
- **Location**: `frontend/src/pages/ScraperAdmin.tsx`
- **Implementation**:
  ```typescript
  import React, { useState, useEffect } from 'react';
  import { useAuth } from '../hooks/useAuth';

  interface ScrapingJob {
    id: string;
    role: string;
    company?: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    questions_found: number;
    started_at: string;
    completed_at?: string;
    error_message?: string;
  }

  const ScraperAdmin: React.FC = () => {
    const [jobs, setJobs] = useState<ScrapingJob[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [newJob, setNewJob] = useState({ role: '', company: '' });

    const startScraping = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/api/v1/scraper/start', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('hirely_token')}`
          },
          body: JSON.stringify(newJob)
        });
        
        if (response.ok) {
          const result = await response.json();
          alert(`Scraping job started: ${result.job_id}`);
          fetchJobs(); // Refresh job list
        }
      } catch (error) {
        console.error('Error starting scraping job:', error);
      } finally {
        setIsLoading(false);
      }
    };

    const fetchJobs = async () => {
      try {
        const response = await fetch('/api/v1/scraper/jobs', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hirely_token')}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setJobs(data.jobs);
        }
      } catch (error) {
        console.error('Error fetching jobs:', error);
      }
    };

    useEffect(() => {
      fetchJobs();
      const interval = setInterval(fetchJobs, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }, []);

    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white shadow rounded-lg p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">
              Interview Question Scraper
            </h1>
            
            {/* Start New Scraping Job */}
            <div className="mb-8 p-4 bg-gray-50 rounded-lg">
              <h2 className="text-lg font-semibold mb-4">Start New Scraping Job</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role
                  </label>
                  <input
                    type="text"
                    value={newJob.role}
                    onChange={(e) => setNewJob({...newJob, role: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Software Engineer, Data Scientist"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company (Optional)
                  </label>
                  <input
                    type="text"
                    value={newJob.company}
                    onChange={(e) => setNewJob({...newJob, company: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Google, Microsoft"
                  />
                </div>
              </div>
              <button
                onClick={startScraping}
                disabled={isLoading || !newJob.role}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {isLoading ? 'Starting...' : 'Start Scraping'}
              </button>
            </div>

            {/* Scraping Jobs List */}
            <div>
              <h2 className="text-lg font-semibold mb-4">Scraping Jobs</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Job ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Role
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Questions Found
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Started At
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {jobs.map((job) => (
                      <tr key={job.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {job.id.substring(0, 8)}...
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {job.role}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {job.company || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            job.status === 'completed' ? 'bg-green-100 text-green-800' :
                            job.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                            job.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {job.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {job.questions_found}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(job.started_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  export default ScraperAdmin;
  ```

### 6. Data Quality and Validation

#### 6.1 Question Validation
**Priority: MEDIUM**
- **Task**: Implement question quality validation
- **Implementation**:
  ```python
  class QuestionValidator:
      def __init__(self):
          self.min_length = 10
          self.max_length = 500
          self.spam_keywords = ['click here', 'buy now', 'free download']
      
      def validate_question(self, question: Dict) -> Dict[str, Any]:
          """Validate question quality and relevance"""
          validation_result = {
              'is_valid': True,
              'issues': [],
              'quality_score': 0.0
          }
          
          # Check question length
          if len(question['question_text']) < self.min_length:
              validation_result['is_valid'] = False
              validation_result['issues'].append('Question too short')
          
          if len(question['question_text']) > self.max_length:
              validation_result['is_valid'] = False
              validation_result['issues'].append('Question too long')
          
          # Check for spam
          if any(keyword in question['question_text'].lower() for keyword in self.spam_keywords):
              validation_result['is_valid'] = False
              validation_result['issues'].append('Contains spam keywords')
          
          # Check for question format
          if not question['question_text'].endswith('?'):
              validation_result['issues'].append('Missing question mark')
          
          # Calculate quality score
          validation_result['quality_score'] = self._calculate_quality_score(question)
          
          return validation_result
  ```

#### 6.2 Duplicate Detection
**Priority: MEDIUM**
- **Task**: Implement duplicate question detection
- **Implementation**:
  ```python
  from difflib import SequenceMatcher
  
  class DuplicateDetector:
      def __init__(self):
          self.similarity_threshold = 0.8
      
      def find_duplicates(self, questions: List[Dict]) -> List[List[Dict]]:
          """Find duplicate questions using similarity matching"""
          duplicates = []
          processed = set()
          
          for i, question1 in enumerate(questions):
              if i in processed:
                  continue
              
              duplicate_group = [question1]
              processed.add(i)
              
              for j, question2 in enumerate(questions[i+1:], i+1):
                  if j in processed:
                      continue
                  
                  similarity = self._calculate_similarity(
                      question1['question_text'],
                      question2['question_text']
                  )
                  
                  if similarity >= self.similarity_threshold:
                      duplicate_group.append(question2)
                      processed.add(j)
              
              if len(duplicate_group) > 1:
                  duplicates.append(duplicate_group)
          
          return duplicates
      
      def _calculate_similarity(self, text1: str, text2: str) -> float:
          """Calculate similarity between two texts"""
          return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
  ```

### 7. Performance and Scalability

#### 7.1 Rate Limiting and Throttling
**Priority: HIGH**
- **Task**: Implement rate limiting to avoid being blocked
- **Implementation**:
  ```python
  import asyncio
  from datetime import datetime, timedelta
  
  class RateLimiter:
      def __init__(self, max_requests: int = 10, time_window: int = 60):
          self.max_requests = max_requests
          self.time_window = time_window
          self.requests = []
      
      async def wait_if_needed(self):
          """Wait if rate limit is exceeded"""
          now = datetime.utcnow()
          
          # Remove old requests
          self.requests = [req_time for req_time in self.requests 
                          if now - req_time < timedelta(seconds=self.time_window)]
          
          if len(self.requests) >= self.max_requests:
              sleep_time = self.time_window - (now - self.requests[0]).seconds
              if sleep_time > 0:
                  await asyncio.sleep(sleep_time)
          
          self.requests.append(now)
  ```

#### 7.2 Caching and Optimization
**Priority: MEDIUM**
- **Task**: Implement caching for scraped data
- **Implementation**:
  ```python
  import redis
  from typing import Optional
  
  class ScraperCache:
      def __init__(self):
          self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
          self.cache_ttl = 3600  # 1 hour
      
      async def get_cached_questions(self, role: str, company: str = None) -> Optional[List[Dict]]:
          """Get cached questions for a role"""
          cache_key = f"questions:{role}:{company or 'all'}"
          cached_data = self.redis_client.get(cache_key)
          
          if cached_data:
              return json.loads(cached_data)
          return None
      
      async def cache_questions(self, role: str, questions: List[Dict], company: str = None):
          """Cache questions for a role"""
          cache_key = f"questions:{role}:{company or 'all'}"
          self.redis_client.setex(
              cache_key, 
              self.cache_ttl, 
              json.dumps(questions, default=str)
          )
  ```

### 8. Monitoring and Analytics

#### 8.1 Scraping Analytics
**Priority: LOW**
- **Task**: Track scraping performance and success rates
- **Implementation**:
  ```python
  class ScrapingAnalytics:
      def __init__(self):
          self.metrics = {
              'total_jobs': 0,
              'successful_jobs': 0,
              'failed_jobs': 0,
              'total_questions_scraped': 0,
              'average_questions_per_job': 0,
              'top_sources': {},
              'success_rate': 0.0
          }
      
      def record_job_completion(self, job: Dict):
          """Record job completion metrics"""
          self.metrics['total_jobs'] += 1
          
          if job['status'] == 'completed':
              self.metrics['successful_jobs'] += 1
              self.metrics['total_questions_scraped'] += job['questions_found']
          else:
              self.metrics['failed_jobs'] += 1
          
          self._update_derived_metrics()
      
      def _update_derived_metrics(self):
          """Update derived metrics"""
          if self.metrics['total_jobs'] > 0:
              self.metrics['success_rate'] = (
                  self.metrics['successful_jobs'] / self.metrics['total_jobs']
              )
              self.metrics['average_questions_per_job'] = (
                  self.metrics['total_questions_scraped'] / self.metrics['successful_jobs']
              )
  ```

### 9. Integration with ChromaDB

#### 9.1 Vector Storage of Questions
**Priority: MEDIUM**
- **Task**: Store scraped questions in ChromaDB for similarity search
- **Implementation**:
  ```python
  class ScrapedQuestionVectorizer:
      def __init__(self):
          self.chroma_service = ChromaService()
      
      async def store_questions_as_vectors(self, questions: List[Dict]):
          """Store questions as vectors in ChromaDB"""
          for question in questions:
              # Create embedding from question text
              embedding = await self._create_embedding(question['question_text'])
              
              # Store in ChromaDB
              await self.chroma_service.add_document(
                  id=f"scraped_{question['id']}",
                  document=question['question_text'],
                  metadata={
                      'role': question['role'],
                      'company': question.get('company'),
                      'source': question['source'],
                      'difficulty': question['difficulty'],
                      'category': question['category'],
                      'scraped_at': question['scraped_at'],
                      'type': 'scraped_question'
                  },
                  embedding=embedding
              )
      
      async def find_similar_questions(self, query: str, role: str, limit: int = 10) -> List[Dict]:
          """Find similar questions using vector similarity"""
          results = await self.chroma_service.search_similar_responses(
              query=query,
              n_results=limit,
              filter_metadata={
                  'role': role,
                  'type': 'scraped_question'
              }
          )
          
          return results
  ```

### 10. Testing and Quality Assurance

#### 10.1 Unit Tests
**Priority: MEDIUM**
- **Task**: Create comprehensive unit tests
- **Location**: `backend/tests/test_scraper_service.py`
- **Implementation**:
  ```python
  import pytest
  from unittest.mock import AsyncMock, patch
  from app.services.scraper_service import ScraperService
  
  class TestScraperService:
      @pytest.fixture
      def scraper_service(self):
          return ScraperService()
      
      @pytest.mark.asyncio
      async def test_scrape_questions_for_role(self, scraper_service):
          """Test question scraping for a role"""
          with patch('app.services.scraper_service.AsyncWebCrawler') as mock_crawler:
              mock_crawler.return_value.arun.return_value = AsyncMock(
                  success=True,
                  html="<div>Tell me about yourself</div>"
              )
              
              questions = await scraper_service.scrape_questions_for_role("Software Engineer")
              
              assert len(questions) > 0
              assert all('question_text' in q for q in questions)
      
      @pytest.mark.asyncio
      async def test_question_validation(self, scraper_service):
          """Test question validation"""
          valid_question = {
              'question_text': 'Tell me about a challenging project you worked on?',
              'role': 'Software Engineer',
              'source': 'test.com'
          }
          
          result = scraper_service.validate_question(valid_question)
          assert result['is_valid'] == True
          assert result['quality_score'] > 0.5
  ```

#### 10.2 Integration Tests
**Priority: MEDIUM**
- **Task**: Test end-to-end scraping workflow
- **Implementation**:
  ```python
  @pytest.mark.asyncio
  async def test_end_to_end_scraping():
      """Test complete scraping workflow"""
      scraper_service = ScraperService()
      
      # Start scraping job
      result = await scraper_service.scrape_and_store_questions(
          role="Data Scientist",
          company="Google"
      )
      
      assert result['status'] == 'completed'
      assert result['questions_stored'] > 0
      
      # Verify questions were stored
      questions = await scraper_service.get_questions_for_role("Data Scientist", "Google")
      assert len(questions) > 0
  ```

## Implementation Priority Order

### Day 1 (Morning)
1. **Crawl4AI Setup** - Install and configure Crawl4AI
2. **Basic Scraper Service** - Create core scraping functionality
3. **Database Schema** - Create tables for scraped questions

### Day 1 (Afternoon)
4. **API Endpoints** - Create scraper API endpoints
5. **Question Validation** - Implement quality validation
6. **Basic Frontend** - Create admin interface

### Day 2 (If Time Permits)
7. **ChromaDB Integration** - Store questions as vectors
8. **Enhanced Question Generation** - Integrate with Groq
9. **Analytics and Monitoring** - Track scraping performance

## Technical Requirements

### Dependencies
```txt
crawl4ai>=0.3.0
beautifulsoup4>=4.12.0
redis>=4.5.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

### Environment Variables
```env
CRAWL4AI_BROWSER_PATH=/usr/bin/chromium
CRAWL4AI_HEADLESS=true
REDIS_URL=redis://localhost:6379
SCRAPER_RATE_LIMIT=10
SCRAPER_TIME_WINDOW=60
```

## Success Metrics

### Technical Metrics
- Scraping success rate: >80%
- Question quality score: >0.7
- Duplicate detection accuracy: >90%
- Processing time: <5 minutes per role

### Business Metrics
- Questions per role: >50
- Source diversity: >5 sources per role
- Question relevance: >85%
- User satisfaction: >4.0/5.0

## Troubleshooting Guide

### Common Issues
1. **Scraping Blocked**: Implement rate limiting and proxy rotation
2. **Low Quality Questions**: Improve validation and filtering
3. **Duplicate Questions**: Enhance similarity detection
4. **Performance Issues**: Implement caching and optimization

### Debug Commands
```bash
# Test Crawl4AI connection
python -c "from crawl4ai import AsyncWebCrawler; print('Crawl4AI working')"

# Check Redis connection
redis-cli ping

# Monitor scraping jobs
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/scraper/jobs
```

## Resources

### Documentation
- [Crawl4AI Documentation](https://docs.crawl4ai.com/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Redis Documentation](https://redis.io/docs/)

### Code References
- `backend/app/services/scraper_service.py` - Core scraping logic
- `backend/app/api/v1/endpoints/scraper.py` - API endpoints
- `frontend/src/pages/ScraperAdmin.tsx` - Admin interface

## Notes for Hackathon Day

### Quick Start Checklist
- [ ] Install Crawl4AI and dependencies
- [ ] Configure browser automation
- [ ] Test basic scraping functionality
- [ ] Create database schema
- [ ] Implement API endpoints

### Emergency Fallbacks
- If Crawl4AI fails, use requests + BeautifulSoup
- If rate limited, implement exponential backoff
- If quality issues, enhance validation rules
- If performance issues, implement caching

### Demo Preparation
- Prepare test roles for scraping
- Test on different websites
- Prepare sample questions for demo
- Test integration with existing system

---

**Last Updated**: October 23, 2024
**Status**: Ready for Hackathon Implementation
**Next Review**: Hackathon Day Morning
