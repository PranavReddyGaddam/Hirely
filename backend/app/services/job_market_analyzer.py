"""
AI-Powered Job Market Analyzer
Combines job scraping with AI analysis for comprehensive market insights.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import our services
from .crawl4ai_service import Crawl4AIService
from .groq_service import GroqService

logger = logging.getLogger(__name__)

class JobMarketAnalyzer:
    """AI-powered job market analyzer using scraped data and AI analysis"""
    
    def __init__(self):
        self.crawl4ai_service = Crawl4AIService()
        self.groq_service = GroqService()
        self.analysis_prompts = self._create_analysis_prompts()
    
    async def analyze_job_market(self, 
                               keywords: str = "software engineer",
                               location: str = "",
                               analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Perform comprehensive job market analysis
        
        Args:
            keywords: Job search keywords
            location: Location filter (optional)
            analysis_depth: Analysis depth (basic, comprehensive, detailed)
            
        Returns:
            Dictionary with comprehensive market analysis
        """
        try:
            logger.info(f"Starting job market analysis for: {keywords}")
            
            # Step 1: Scrape job data
            print("🔍 Step 1: Scraping job data...")
            job_insights = await self.crawl4ai_service.get_job_market_insights(
                keywords=keywords,
                location=location
            )
            
            if not job_insights['success']:
                return {
                    'success': False,
                    'error': job_insights['error'],
                    'analysis': {}
                }
            
            # Step 2: AI Analysis
            print("🤖 Step 2: AI Analysis...")
            ai_analysis = await self._perform_ai_analysis(job_insights, analysis_depth)
            
            # Step 3: Generate insights report
            print("📊 Step 3: Generating insights report...")
            insights_report = self._generate_insights_report(job_insights, ai_analysis)
            
            logger.info(f"Completed job market analysis for {keywords}")
            
            return {
                'success': True,
                'keywords': keywords,
                'location': location,
                'analysis_depth': analysis_depth,
                'job_data': job_insights,
                'ai_analysis': ai_analysis,
                'insights_report': insights_report,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in job market analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': {}
            }
    
    async def generate_interview_prep(self, 
                                    job_title: str = "software engineer",
                                    location: str = "",
                                    prep_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate comprehensive interview preparation based on job market data
        
        Args:
            job_title: Target job title
            location: Location filter (optional)
            prep_type: Type of preparation (basic, comprehensive, detailed)
            
        Returns:
            Dictionary with interview preparation materials
        """
        try:
            logger.info(f"Generating interview prep for: {job_title}")
            
            # Step 1: Scrape jobs and generate questions
            print("📚 Step 1: Scraping jobs and generating questions...")
            job_prep_data = await self.crawl4ai_service.scrape_jobs_for_interview_prep(
                job_title=job_title,
                location=location,
                max_jobs=30
            )
            
            if not job_prep_data['success']:
                return {
                    'success': False,
                    'error': job_prep_data['error'],
                    'preparation': {}
                }
            
            # Step 2: AI-enhanced question analysis
            print("🧠 Step 2: AI-enhanced question analysis...")
            ai_question_analysis = await self._analyze_questions_with_ai(
                job_prep_data['interview_questions'],
                job_prep_data['skills_analysis']
            )
            
            # Step 3: Generate study guide
            print("📖 Step 3: Generating study guide...")
            study_guide = await self._generate_study_guide(
                job_prep_data,
                ai_question_analysis
            )
            
            # Step 4: Create practice recommendations
            print("🎯 Step 4: Creating practice recommendations...")
            practice_plan = self._create_practice_plan(
                job_prep_data,
                ai_question_analysis
            )
            
            logger.info(f"Generated interview prep for {job_title}")
            
            return {
                'success': True,
                'job_title': job_title,
                'location': location,
                'prep_type': prep_type,
                'job_data': job_prep_data,
                'ai_analysis': ai_question_analysis,
                'study_guide': study_guide,
                'practice_plan': practice_plan,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating interview prep: {e}")
            return {
                'success': False,
                'error': str(e),
                'preparation': {}
            }
    
    async def analyze_company_jobs(self, 
                                 company_name: str,
                                 include_ai_analysis: bool = True) -> Dict[str, Any]:
        """
        Analyze jobs from a specific company with AI insights
        
        Args:
            company_name: Name of the company to analyze
            include_ai_analysis: Whether to include AI analysis
            
        Returns:
            Dictionary with company job analysis
        """
        try:
            logger.info(f"Analyzing jobs for company: {company_name}")
            
            # Scrape company jobs
            company_data = await self.crawl4ai_service.scrape_company_specific_jobs(
                company_name=company_name,
                generate_questions=True
            )
            
            if not company_data['success']:
                return {
                    'success': False,
                    'error': company_data['error'],
                    'analysis': {}
                }
            
            result = {
                'success': True,
                'company': company_name,
                'job_data': company_data,
                'generated_at': datetime.now().isoformat()
            }
            
            # Add AI analysis if requested
            if include_ai_analysis and company_data.get('jobs'):
                print("🤖 Performing AI analysis...")
                ai_analysis = await self._analyze_company_with_ai(company_data)
                result['ai_analysis'] = ai_analysis
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing company jobs: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': {}
            }
    
    async def _perform_ai_analysis(self, job_insights: Dict[str, Any], analysis_depth: str) -> Dict[str, Any]:
        """Perform AI analysis on job market data"""
        try:
            # Prepare data for AI analysis
            analysis_data = {
                'total_jobs': job_insights['total_jobs_analyzed'],
                'skills_analysis': job_insights['skills_analysis'],
                'trends': job_insights['trends'],
                'insights': job_insights['insights']
            }
            
            # Market trends analysis
            trends_prompt = self.analysis_prompts['market_trends'].format(
                job_data=json.dumps(analysis_data, indent=2)
            )
            
            trends_analysis = await self._call_groq_analysis(trends_prompt)
            
            # Skills analysis
            skills_prompt = self.analysis_prompts['skill_analysis'].format(
                job_data=json.dumps(analysis_data, indent=2)
            )
            
            skills_analysis = await self._call_groq_analysis(skills_prompt)
            
            # Career recommendations
            career_prompt = self.analysis_prompts['career_recommendations'].format(
                job_data=json.dumps(analysis_data, indent=2)
            )
            
            career_analysis = await self._call_groq_analysis(career_prompt)
            
            return {
                'market_trends': trends_analysis,
                'skills_analysis': skills_analysis,
                'career_recommendations': career_analysis,
                'analysis_depth': analysis_depth,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                'error': str(e),
                'analysis': {}
            }
    
    async def _analyze_questions_with_ai(self, 
                                       questions: List[Dict[str, Any]], 
                                       skills_analysis: Dict[str, int]) -> Dict[str, Any]:
        """Analyze interview questions with AI to provide insights"""
        try:
            # Prepare question data for analysis
            question_data = {
                'total_questions': len(questions),
                'questions_by_category': self._categorize_questions(questions),
                'top_skills': list(skills_analysis.keys())[:10],
                'skills_demand': skills_analysis
            }
            
            # Create analysis prompt
            prompt = f"""
            Analyze these interview questions and provide insights:
            
            Question Data: {json.dumps(question_data, indent=2)}
            
            Please provide:
            1. Question difficulty distribution
            2. Most important skills to focus on
            3. Question types and their frequency
            4. Study recommendations
            5. Practice priorities
            """
            
            analysis = await self._call_groq_analysis(prompt)
            
            return {
                'question_analysis': analysis,
                'total_questions': len(questions),
                'categories': self._categorize_questions(questions),
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing questions with AI: {e}")
            return {
                'error': str(e),
                'analysis': {}
            }
    
    async def _analyze_company_with_ai(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company-specific job data with AI"""
        try:
            # Prepare company data for analysis
            company_analysis_data = {
                'company': company_data['company'],
                'total_jobs': company_data['total_jobs'],
                'jobs': company_data['jobs'][:10],  # Limit for analysis
                'interview_questions': company_data.get('interview_questions', [])[:20]
            }
            
            prompt = f"""
            Analyze this company's job postings and provide insights:
            
            Company Data: {json.dumps(company_analysis_data, indent=2)}
            
            Please provide:
            1. Company hiring patterns
            2. Required skills and technologies
            3. Interview question analysis
            4. Application recommendations
            5. Company culture insights (if available)
            """
            
            analysis = await self._call_groq_analysis(prompt)
            
            return {
                'company_analysis': analysis,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing company with AI: {e}")
            return {
                'error': str(e),
                'analysis': {}
            }
    
    async def _call_groq_analysis(self, prompt: str) -> str:
        """Call Groq service for AI analysis"""
        try:
            if self.groq_service and self.groq_service.client:
                # Use existing Groq service
                response = await self.groq_service.generate_analysis(prompt)
                return response
            else:
                # Fallback to mock analysis
                return self._generate_mock_analysis(prompt)
        except Exception as e:
            logger.error(f"Error calling Groq analysis: {e}")
            return self._generate_mock_analysis(prompt)
    
    def _generate_mock_analysis(self, prompt: str) -> str:
        """Generate mock analysis when AI service is not available"""
        return f"Mock AI analysis for: {prompt[:100]}..."
    
    def _categorize_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize questions by type and difficulty"""
        categories = {}
        
        for question in questions:
            category = question.get('category', 'general')
            difficulty = question.get('difficulty', 'intermediate')
            q_type = question.get('type', 'technical')
            
            key = f"{category}_{difficulty}_{q_type}"
            if key not in categories:
                categories[key] = []
            categories[key].append(question)
        
        return categories
    
    def _generate_insights_report(self, 
                                job_insights: Dict[str, Any], 
                                ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive insights report"""
        return {
            'executive_summary': {
                'total_jobs_analyzed': job_insights['total_jobs_analyzed'],
                'top_skills': list(job_insights['skills_analysis'].keys())[:5],
                'market_trends': ai_analysis.get('market_trends', ''),
                'key_insights': [
                    f"Analyzed {job_insights['total_jobs_analyzed']} job postings",
                    f"Top skill: {list(job_insights['skills_analysis'].keys())[0] if job_insights['skills_analysis'] else 'N/A'}",
                    "Remote work opportunities are increasing",
                    "Full-stack development skills are in high demand"
                ]
            },
            'detailed_analysis': {
                'skills_breakdown': job_insights['skills_analysis'],
                'job_trends': job_insights['trends'],
                'ai_insights': ai_analysis
            },
            'recommendations': [
                "Focus on the most in-demand skills",
                "Consider remote work opportunities",
                "Develop both technical and soft skills",
                "Stay updated with emerging technologies"
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    async def _generate_study_guide(self, 
                                  job_prep_data: Dict[str, Any], 
                                  ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive study guide"""
        return {
            'overview': {
                'job_title': job_prep_data['job_title'],
                'total_questions': job_prep_data['total_questions'],
                'top_skills': list(job_prep_data['skills_analysis'].keys())[:10]
            },
            'study_sections': {
                'technical_skills': self._create_technical_study_section(job_prep_data),
                'behavioral_questions': self._create_behavioral_study_section(job_prep_data),
                'company_research': self._create_company_research_section(job_prep_data)
            },
            'ai_recommendations': ai_analysis.get('question_analysis', ''),
            'generated_at': datetime.now().isoformat()
        }
    
    def _create_technical_study_section(self, job_prep_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create technical skills study section"""
        skills = job_prep_data['skills_analysis']
        questions = [q for q in job_prep_data['interview_questions'] if q.get('type') == 'technical']
        
        return {
            'top_skills': list(skills.keys())[:5],
            'skill_questions': {skill: [q for q in questions if q.get('category') == skill] for skill in list(skills.keys())[:5]},
            'study_resources': [
                "Official documentation for each technology",
                "Online coding practice platforms",
                "Technical blogs and tutorials",
                "Open source project contributions"
            ]
        }
    
    def _create_behavioral_study_section(self, job_prep_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create behavioral questions study section"""
        behavioral_questions = [q for q in job_prep_data['interview_questions'] if q.get('type') == 'behavioral']
        
        return {
            'common_questions': behavioral_questions[:10],
            'preparation_tips': [
                "Use the STAR method (Situation, Task, Action, Result)",
                "Prepare specific examples from your experience",
                "Practice explaining technical concepts to non-technical people",
                "Be ready to discuss challenges and how you overcame them"
            ]
        }
    
    def _create_company_research_section(self, job_prep_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company research study section"""
        companies = list(set(job['company'] for job in job_prep_data['jobs']))
        
        return {
            'target_companies': companies[:10],
            'research_areas': [
                "Company mission and values",
                "Recent news and developments",
                "Technology stack and products",
                "Company culture and work environment",
                "Interview process and expectations"
            ]
        }
    
    def _create_practice_plan(self, 
                            job_prep_data: Dict[str, Any], 
                            ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured practice plan"""
        return {
            'weekly_schedule': {
                'week_1': "Focus on top 3 technical skills",
                'week_2': "Practice behavioral questions and coding problems",
                'week_3': "Mock interviews and company research",
                'week_4': "Final review and preparation"
            },
            'daily_practice': {
                'technical': "2-3 hours of coding practice",
                'behavioral': "30 minutes of question practice",
                'research': "30 minutes of company research"
            },
            'resources': [
                "LeetCode for coding practice",
                "Glassdoor for company insights",
                "LinkedIn for networking",
                "Company websites for research"
            ],
            'goals': [
                "Master top 5 technical skills",
                "Prepare 10+ behavioral examples",
                "Research 5+ target companies",
                "Complete 20+ practice problems"
            ]
        }
    
    def _create_analysis_prompts(self) -> Dict[str, str]:
        """Create AI analysis prompts"""
        return {
            'market_trends': """
            Analyze the following job market data and provide insights on:
            1. Most in-demand skills and technologies
            2. Salary trends and compensation patterns
            3. Company types and sizes hiring
            4. Geographic distribution of opportunities
            5. Job level distribution (entry, mid, senior)
            6. Remote vs on-site work trends
            7. Emerging technologies and future trends
            
            Job Data: {job_data}
            
            Provide a comprehensive analysis with specific recommendations.
            """,
            
            'skill_analysis': """
            Based on these job postings, analyze the technical skills landscape:
            1. Top 10 most mentioned technical skills
            2. Emerging technologies and frameworks
            3. Required vs preferred qualifications
            4. Skill combinations that appear together frequently
            5. Skills that are becoming obsolete
            6. Industry-specific skill requirements
            7. Learning recommendations for each skill
            
            Job Data: {job_data}
            
            Provide detailed insights with learning paths and resources.
            """,
            
            'career_recommendations': """
            Provide career advice based on current job market analysis:
            1. Which roles are growing fastest and why
            2. What skills should someone learn for career advancement
            3. Which companies are actively hiring and what they look for
            4. Geographic opportunities and remote work trends
            5. Salary expectations and negotiation tips
            6. Career progression paths
            7. Industry trends and future outlook
            
            Job Data: {job_data}
            
            Provide actionable career recommendations with specific next steps.
            """
        }

# Example usage and testing
async def test_job_market_analyzer():
    """Test the Job Market Analyzer"""
    print("🧪 Testing Job Market Analyzer")
    print("=" * 50)
    
    analyzer = JobMarketAnalyzer()
    
    # Test job market analysis
    print("📊 Testing job market analysis...")
    analysis = await analyzer.analyze_job_market("software engineer", analysis_depth="comprehensive")
    
    if analysis['success']:
        print(f"✅ Analysis completed: {analysis['insights_report']['executive_summary']['total_jobs_analyzed']} jobs analyzed")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")
    
    # Test interview prep generation
    print("\n🎯 Testing interview prep generation...")
    prep = await analyzer.generate_interview_prep("software engineer", prep_type="comprehensive")
    
    if prep['success']:
        print(f"✅ Interview prep generated: {prep['job_data']['total_questions']} questions")
    else:
        print(f"❌ Interview prep failed: {prep['error']}")

if __name__ == "__main__":
    asyncio.run(test_job_market_analyzer())
