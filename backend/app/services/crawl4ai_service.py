"""
Crawl4AI Service for scraping interview questions from various sources.
This service provides a clean interface for integrating web scraping into the Hirely application.
Enhanced with BrightData MCP integration for job scraping capabilities.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup

# Import our new BrightData service
from .brightdata_mcp_service import BrightDataMCPService

logger = logging.getLogger(__name__)

class Crawl4AIService:
    """Service for scraping interview questions using Crawl4AI with job scraping capabilities"""
    
    def __init__(self):
        self.crawler = None
        self.brightdata_service = BrightDataMCPService()
        self.question_sources = [
            {
                "name": "InterviewBit Python",
                "url": "https://www.interviewbit.com/python-interview-questions/",
                "category": "python",
                "difficulty": "intermediate"
            },
            {
                "name": "InterviewBit Java",
                "url": "https://www.interviewbit.com/java-interview-questions/",
                "category": "java",
                "difficulty": "intermediate"
            },
            {
                "name": "GeeksforGeeks Programming",
                "url": "https://www.geeksforgeeks.org/commonly-asked-programming-interview-questions/",
                "category": "programming",
                "difficulty": "beginner"
            },
            {
                "name": "LeetCode Discussion",
                "url": "https://leetcode.com/discuss/interview-question/",
                "category": "algorithms",
                "difficulty": "advanced"
            }
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.crawler = AsyncWebCrawler()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.crawler:
            await self.crawler.close()
    
    async def scrape_questions_from_source(self, source: Dict[str, str]) -> Dict[str, Any]:
        """
        Scrape questions from a specific source
        
        Args:
            source: Dictionary containing source information (name, url, category, difficulty)
            
        Returns:
            Dictionary with scraped questions and metadata
        """
        try:
            logger.info(f"Scraping questions from {source['name']}")
            
            result = await self.crawler.arun(url=source['url'])
            
            if not result.success:
                logger.error(f"Failed to scrape {source['name']}: {result.error if hasattr(result, 'error') else 'Unknown error'}")
                return {
                    'source': source['name'],
                    'success': False,
                    'error': 'Scraping failed',
                    'questions': []
                }
            
            # Extract questions from the scraped content
            questions = self._extract_questions(result)
            
            # Clean and format questions
            cleaned_questions = self._clean_questions(questions)
            
            logger.info(f"Successfully scraped {len(cleaned_questions)} questions from {source['name']}")
            
            return {
                'source': source['name'],
                'url': source['url'],
                'category': source['category'],
                'difficulty': source['difficulty'],
                'success': True,
                'questions': cleaned_questions,
                'total_questions': len(cleaned_questions),
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")
            return {
                'source': source['name'],
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    async def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """
        Scrape questions from all configured sources
        
        Returns:
            List of dictionaries containing scraped questions from each source
        """
        results = []
        
        for source in self.question_sources:
            result = await self.scrape_questions_from_source(source)
            results.append(result)
            
            # Add a small delay between requests to be respectful
            await asyncio.sleep(1)
        
        return results
    
    async def scrape_questions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Scrape questions from sources matching a specific category
        
        Args:
            category: Category to filter sources (e.g., 'python', 'java', 'programming')
            
        Returns:
            List of dictionaries containing scraped questions from matching sources
        """
        matching_sources = [source for source in self.question_sources if source['category'] == category]
        
        if not matching_sources:
            logger.warning(f"No sources found for category: {category}")
            return []
        
        results = []
        for source in matching_sources:
            result = await self.scrape_questions_from_source(source)
            results.append(result)
            await asyncio.sleep(1)
        
        return results
    
    def _extract_questions(self, result) -> List[str]:
        """Extract questions from scraped content"""
        questions = []
        
        # Method 1: Parse HTML with BeautifulSoup
        if result.html:
            soup = BeautifulSoup(result.html, 'html.parser')
            questions.extend(self._extract_from_soup(soup))
        
        # Method 2: Parse cleaned HTML
        if result.cleaned_html:
            soup = BeautifulSoup(result.cleaned_html, 'html.parser')
            questions.extend(self._extract_from_soup(soup))
        
        # Method 3: Parse markdown content
        if result.markdown:
            questions.extend(self._extract_from_markdown(result.markdown))
        
        return questions
    
    def _extract_from_soup(self, soup: BeautifulSoup) -> List[str]:
        """Extract questions from BeautifulSoup object"""
        questions = []
        
        # Look for common question patterns
        selectors = [
            'p', 'li', 'h1', 'h2', 'h3', 'h4', 'div.question', 'div.qa-item',
            'span.question', 'div.answer', 'div.content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if self._is_question(text):
                    questions.append(text)
        
        return questions
    
    def _extract_from_markdown(self, markdown_content: str) -> List[str]:
        """Extract questions from markdown content"""
        questions = []
        lines = markdown_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if self._is_question(line):
                questions.append(line)
        
        return questions
    
    def _is_question(self, text: str) -> bool:
        """Check if text looks like a question"""
        if not text or len(text) < 10 or len(text) > 500:
            return False
        
        # Must end with question mark
        if not text.endswith('?'):
            return False
        
        # Must contain question keywords
        question_keywords = [
            'what', 'how', 'why', 'when', 'where', 'which', 'who',
            'tell', 'describe', 'explain', 'difference', 'advantage',
            'disadvantage', 'implement', 'design', 'solve', 'approach',
            'create', 'write', 'define', 'list', 'name', 'give'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in question_keywords)
    
    def _clean_questions(self, questions: List[str]) -> List[str]:
        """Clean and format scraped questions"""
        cleaned = []
        
        for question in questions:
            # Remove extra whitespace and newlines
            cleaned_question = ' '.join(question.split())
            
            # Remove common prefixes
            prefixes_to_remove = [
                'Q:', 'Question:', 'Q.', 'Q-', '1.', '2.', '3.', '4.', '5.',
                '6.', '7.', '8.', '9.', '10.', 'a.', 'b.', 'c.', 'd.'
            ]
            
            for prefix in prefixes_to_remove:
                if cleaned_question.startswith(prefix):
                    cleaned_question = cleaned_question[len(prefix):].strip()
            
            # Skip if too short or too long
            if 15 <= len(cleaned_question) <= 300:
                cleaned.append(cleaned_question)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_questions = []
        for question in cleaned:
            if question not in seen:
                seen.add(question)
                unique_questions.append(question)
        
        return unique_questions
    
    async def get_questions_for_interview(self, 
                                        category: str = "python", 
                                        difficulty: str = "intermediate",
                                        max_questions: int = 50) -> List[Dict[str, Any]]:
        """
        Get questions suitable for an interview based on category and difficulty
        
        Args:
            category: Question category (python, java, programming, algorithms)
            difficulty: Difficulty level (beginner, intermediate, advanced)
            max_questions: Maximum number of questions to return
            
        Returns:
            List of question dictionaries with metadata
        """
        try:
            # Scrape questions from matching sources
            results = await self.scrape_questions_by_category(category)
            
            all_questions = []
            for result in results:
                if result['success']:
                    for question in result['questions']:
                        all_questions.append({
                            'question': question,
                            'source': result['source'],
                            'category': result['category'],
                            'difficulty': result['difficulty'],
                            'scraped_at': result['scraped_at']
                        })
            
            # Filter by difficulty if specified
            if difficulty != "all":
                all_questions = [q for q in all_questions if q['difficulty'] == difficulty]
            
            # Limit to max_questions
            if len(all_questions) > max_questions:
                all_questions = all_questions[:max_questions]
            
            logger.info(f"Retrieved {len(all_questions)} questions for category: {category}, difficulty: {difficulty}")
            
            return all_questions
            
        except Exception as e:
            logger.error(f"Error getting questions for interview: {e}")
            return []
    
    def save_questions_to_file(self, questions: List[Dict[str, Any]], filename: str = None):
        """Save scraped questions to a JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_questions_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Questions saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving questions to file: {e}")
            return None
    
    # ===== NEW JOB SCRAPING METHODS =====
    
    async def scrape_jobs_for_interview_prep(self, 
                                           job_title: str = "software engineer",
                                           location: str = "",
                                           max_jobs: int = 20) -> Dict[str, Any]:
        """
        Scrape jobs and generate interview questions based on job requirements
        
        Args:
            job_title: Job title to search for
            location: Location filter (optional)
            max_jobs: Maximum number of jobs to scrape
            
        Returns:
            Dictionary with jobs and generated interview questions
        """
        try:
            logger.info(f"Scraping jobs for interview prep: {job_title}")
            
            # Scrape jobs using BrightData MCP
            job_data = await self.brightdata_service.scrape_linkedin_jobs(
                keywords=job_title,
                location=location,
                max_results=max_jobs
            )
            
            if not job_data['success']:
                return {
                    'success': False,
                    'error': job_data['error'],
                    'jobs': [],
                    'questions': []
                }
            
            # Extract skills and requirements from jobs
            skills_analysis = self.brightdata_service.extract_skills_from_jobs(job_data['jobs'])
            
            # Generate relevant interview questions based on job requirements
            interview_questions = await self._generate_job_based_questions(
                job_data['jobs'], 
                skills_analysis
            )
            
            logger.info(f"Generated {len(interview_questions)} interview questions from {len(job_data['jobs'])} jobs")
            
            return {
                'success': True,
                'job_title': job_title,
                'location': location,
                'total_jobs': len(job_data['jobs']),
                'jobs': job_data['jobs'],
                'skills_analysis': skills_analysis,
                'interview_questions': interview_questions,
                'total_questions': len(interview_questions),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in job-based interview prep: {e}")
            return {
                'success': False,
                'error': str(e),
                'jobs': [],
                'questions': []
            }
    
    async def get_job_market_insights(self, 
                                    keywords: str = "software engineer",
                                    location: str = "") -> Dict[str, Any]:
        """
        Get comprehensive job market insights by scraping and analyzing job data
        
        Args:
            keywords: Job search keywords
            location: Location filter (optional)
            
        Returns:
            Dictionary with job market insights and analysis
        """
        try:
            logger.info(f"Generating job market insights for: {keywords}")
            
            # Scrape jobs from multiple categories
            all_jobs = await self.brightdata_service.scrape_all_job_categories()
            
            # Combine all jobs
            combined_jobs = []
            for category_data in all_jobs:
                if category_data['success']:
                    combined_jobs.extend(category_data['jobs'])
            
            # Analyze job trends
            trends = self.brightdata_service.analyze_job_trends(combined_jobs)
            
            # Extract skills analysis
            skills_analysis = self.brightdata_service.extract_skills_from_jobs(combined_jobs)
            
            # Generate market insights
            insights = self._generate_market_insights(trends, skills_analysis)
            
            logger.info(f"Generated insights from {len(combined_jobs)} total jobs")
            
            return {
                'success': True,
                'keywords': keywords,
                'location': location,
                'total_jobs_analyzed': len(combined_jobs),
                'trends': trends,
                'skills_analysis': skills_analysis,
                'insights': insights,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating job market insights: {e}")
            return {
                'success': False,
                'error': str(e),
                'insights': {}
            }
    
    async def scrape_company_specific_jobs(self, 
                                         company_name: str,
                                         generate_questions: bool = True) -> Dict[str, Any]:
        """
        Scrape jobs from a specific company and optionally generate interview questions
        
        Args:
            company_name: Name of the company to scrape
            generate_questions: Whether to generate interview questions based on jobs
            
        Returns:
            Dictionary with company jobs and optional interview questions
        """
        try:
            logger.info(f"Scraping jobs for company: {company_name}")
            
            # Scrape company jobs
            company_data = await self.brightdata_service.scrape_company_jobs(company_name)
            
            if not company_data['success']:
                return {
                    'success': False,
                    'error': company_data['error'],
                    'company': company_name,
                    'jobs': [],
                    'questions': []
                }
            
            result = {
                'success': True,
                'company': company_name,
                'total_jobs': company_data['total_jobs'],
                'jobs': company_data['jobs'],
                'scraped_at': company_data['scraped_at']
            }
            
            # Generate interview questions if requested
            if generate_questions and company_data['jobs']:
                skills_analysis = self.brightdata_service.extract_skills_from_jobs(company_data['jobs'])
                questions = await self._generate_job_based_questions(
                    company_data['jobs'], 
                    skills_analysis
                )
                result['interview_questions'] = questions
                result['total_questions'] = len(questions)
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping company jobs for {company_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'company': company_name,
                'jobs': [],
                'questions': []
            }
    
    async def _generate_job_based_questions(self, 
                                          jobs: List[Dict[str, Any]], 
                                          skills_analysis: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate interview questions based on job requirements and skills"""
        questions = []
        
        # Get top skills from analysis
        top_skills = list(skills_analysis.keys())[:10]
        
        # Generate questions for each top skill
        for skill in top_skills:
            skill_questions = self._generate_skill_specific_questions(skill, jobs)
            questions.extend(skill_questions)
        
        # Generate general behavioral questions based on job types
        job_types = set(job.get('job_type', 'Full-time') for job in jobs)
        for job_type in job_types:
            behavioral_questions = self._generate_behavioral_questions(job_type)
            questions.extend(behavioral_questions)
        
        # Remove duplicates and limit
        unique_questions = []
        seen = set()
        for q in questions:
            if q['question'] not in seen:
                seen.add(q['question'])
                unique_questions.append(q)
        
        return unique_questions[:50]  # Limit to 50 questions
    
    def _generate_skill_specific_questions(self, skill: str, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate questions specific to a particular skill"""
        skill_questions = {
            'python': [
                "Explain the difference between Python 2 and Python 3.",
                "What are Python decorators and how do you use them?",
                "How do you handle exceptions in Python?",
                "What is the difference between list and tuple in Python?",
                "Explain Python's GIL (Global Interpreter Lock)."
            ],
            'javascript': [
                "What is the difference between var, let, and const?",
                "Explain closures in JavaScript.",
                "What is the event loop in JavaScript?",
                "How do you handle asynchronous operations in JavaScript?",
                "What is the difference between == and === in JavaScript?"
            ],
            'java': [
                "Explain the difference between abstract class and interface in Java.",
                "What is the difference between checked and unchecked exceptions?",
                "Explain Java's memory model.",
                "What are generics in Java?",
                "How does garbage collection work in Java?"
            ],
            'react': [
                "What is the difference between state and props in React?",
                "Explain the React component lifecycle.",
                "What are React hooks and how do you use them?",
                "How do you handle state management in React?",
                "What is the virtual DOM in React?"
            ],
            'aws': [
                "Explain the difference between EC2 and Lambda.",
                "What is the purpose of S3 and how do you use it?",
                "How do you handle security in AWS?",
                "What is CloudFormation and how do you use it?",
                "Explain AWS VPC and its components."
            ]
        }
        
        questions = skill_questions.get(skill.lower(), [])
        return [
            {
                'question': q,
                'category': skill,
                'difficulty': 'intermediate',
                'type': 'technical',
                'source': 'job_analysis'
            }
            for q in questions
        ]
    
    def _generate_behavioral_questions(self, job_type: str) -> List[Dict[str, Any]]:
        """Generate behavioral questions based on job type"""
        behavioral_questions = [
            "Tell me about a challenging project you worked on and how you overcame obstacles.",
            "Describe a time when you had to work with a difficult team member.",
            "How do you prioritize tasks when you have multiple deadlines?",
            "Tell me about a time when you had to learn a new technology quickly.",
            "Describe a situation where you had to make a difficult technical decision.",
            "How do you stay updated with the latest industry trends?",
            "Tell me about a time when you had to explain a complex technical concept to a non-technical person.",
            "Describe a project where you had to collaborate with multiple teams.",
            "How do you handle code reviews and feedback?",
            "Tell me about a time when you had to debug a complex issue."
        ]
        
        return [
            {
                'question': q,
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'type': 'behavioral',
                'source': 'job_analysis'
            }
            for q in behavioral_questions
        ]
    
    def _generate_market_insights(self, trends: Dict[str, Any], skills_analysis: Dict[str, int]) -> Dict[str, Any]:
        """Generate market insights from job trends and skills analysis"""
        insights = {
            'market_summary': f"Analyzed {trends.get('total_jobs', 0)} job postings",
            'top_skills': list(skills_analysis.keys())[:10],
            'skill_demand': skills_analysis,
            'job_type_distribution': trends.get('job_types', {}),
            'location_distribution': trends.get('top_locations', {}),
            'company_distribution': trends.get('top_companies', {}),
            'recommendations': []
        }
        
        # Generate recommendations based on analysis
        if skills_analysis:
            top_skill = list(skills_analysis.keys())[0]
            insights['recommendations'].append(f"Focus on {top_skill} - highest demand skill")
        
        if trends.get('job_types'):
            most_common_type = list(trends['job_types'].keys())[0]
            insights['recommendations'].append(f"Most common job type: {most_common_type}")
        
        insights['recommendations'].extend([
            "Consider remote work opportunities for broader job market access",
            "Develop both technical and soft skills for better market positioning",
            "Stay updated with emerging technologies and frameworks"
        ])
        
        return insights

# Example usage and testing
async def test_crawl4ai_service():
    """Test the Crawl4AI service"""
    print("🧪 Testing Crawl4AI Service")
    print("=" * 50)
    
    async with Crawl4AIService() as service:
        # Test scraping all sources
        print("📚 Testing scraping all sources...")
        results = await service.scrape_all_sources()
        
        for result in results:
            if result['success']:
                print(f"✅ {result['source']}: {result['total_questions']} questions")
            else:
                print(f"❌ {result['source']}: {result['error']}")
        
        # Test getting questions for interview
        print("\n🎯 Testing interview question retrieval...")
        questions = await service.get_questions_for_interview(
            category="python",
            difficulty="intermediate",
            max_questions=10
        )
        
        print(f"📝 Retrieved {len(questions)} questions for Python interview:")
        for i, question in enumerate(questions[:5], 1):
            print(f"   {i}. {question['question'][:100]}...")
        
        # Save to file
        if questions:
            filename = service.save_questions_to_file(questions)
            print(f"💾 Questions saved to {filename}")

if __name__ == "__main__":
    asyncio.run(test_crawl4ai_service())
