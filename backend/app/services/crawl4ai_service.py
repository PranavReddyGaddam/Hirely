"""
Crawl4AI Service for scraping interview questions from various sources.
This service provides a clean interface for integrating web scraping into the Hirely application.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class Crawl4AIService:
    """Service for scraping interview questions using Crawl4AI"""
    
    def __init__(self):
        self.crawler = None
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
