"""
BrightData MCP Service for LinkedIn job scraping.
This service provides advanced web scraping capabilities using BrightData's MCP integration.
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.core.config import settings

logger = logging.getLogger(__name__)

class BrightDataMCPService:
    """Service for LinkedIn job scraping using BrightData MCP"""
    
    def __init__(self):
        self.api_token = settings.BRIGHTDATA_API_TOKEN
        self.base_linkedin_url = "https://www.linkedin.com/jobs/search/"
        self.job_sources = [
            {
                "name": "LinkedIn Software Engineer",
                "keywords": "software engineer",
                "category": "engineering",
                "difficulty": "intermediate"
            },
            {
                "name": "LinkedIn Data Scientist", 
                "keywords": "data scientist",
                "category": "data",
                "difficulty": "intermediate"
            },
            {
                "name": "LinkedIn Product Manager",
                "keywords": "product manager",
                "category": "product",
                "difficulty": "intermediate"
            },
            {
                "name": "LinkedIn Frontend Developer",
                "keywords": "frontend developer",
                "category": "engineering",
                "difficulty": "intermediate"
            },
            {
                "name": "LinkedIn Backend Developer",
                "keywords": "backend developer", 
                "category": "engineering",
                "difficulty": "intermediate"
            }
        ]
    
    async def scrape_linkedin_jobs(self, 
                                 keywords: str = "software engineer",
                                 location: str = "",
                                 time_filter: str = "r3600",  # Last 24 hours
                                 max_results: int = 50) -> Dict[str, Any]:
        """
        Scrape LinkedIn jobs using BrightData MCP
        
        Args:
            keywords: Job search keywords
            location: Location filter (optional)
            time_filter: Time filter (r3600 = last 24 hours, r86400 = last week)
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with scraped job data and metadata
        """
        try:
            # Build LinkedIn search URL
            search_url = self._build_linkedin_search_url(keywords, location, time_filter)
            
            logger.info(f"Scraping LinkedIn jobs: {keywords} in {location or 'any location'}")
            
            # Note: In actual implementation, this would call the MCP function
            # For now, we'll simulate the structure that would be returned
            # In Cursor, you would use: mcp_brightdata-mcp_scrape_as_markdown(url=search_url)
            
            # This is a placeholder - the actual MCP call would be made in Cursor
            # The MCP function would return markdown content that we then parse
            mock_scraped_data = await self._simulate_mcp_scrape(search_url)
            
            # Parse the scraped markdown content
            jobs = self._parse_linkedin_jobs(mock_scraped_data)
            
            # Limit results
            if len(jobs) > max_results:
                jobs = jobs[:max_results]
            
            logger.info(f"Successfully scraped {len(jobs)} jobs for '{keywords}'")
            
            return {
                'keywords': keywords,
                'location': location,
                'time_filter': time_filter,
                'total_jobs': len(jobs),
                'jobs': jobs,
                'scraped_at': datetime.now().isoformat(),
                'source': 'linkedin',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn jobs: {e}")
            return {
                'keywords': keywords,
                'success': False,
                'error': str(e),
                'jobs': [],
                'total_jobs': 0,
                'scraped_at': datetime.now().isoformat()
            }
    
    async def scrape_job_details(self, job_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape detailed information from individual job postings
        
        Args:
            job_urls: List of LinkedIn job URLs to scrape
            
        Returns:
            List of detailed job information
        """
        detailed_jobs = []
        
        for url in job_urls:
            try:
                logger.info(f"Scraping job details from: {url}")
                
                # Note: This would use mcp_brightdata-mcp_scrape_as_markdown(url=url)
                # For now, we'll simulate the response
                mock_details = await self._simulate_job_details_scrape(url)
                
                job_details = self._parse_job_details(mock_details, url)
                detailed_jobs.append(job_details)
                
                # Add delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping job details from {url}: {e}")
                continue
        
        return detailed_jobs
    
    async def scrape_jobs_with_skills_analysis(self, 
                                             keywords: str = "software engineer",
                                             location: str = "",
                                             max_results: int = 20) -> Dict[str, Any]:
        """
        Scrape jobs and extract detailed skills, requirements, and qualifications
        
        Args:
            keywords: Job search keywords
            location: Location filter (optional)
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with jobs and detailed skills analysis
        """
        try:
            logger.info(f"Scraping jobs with skills analysis: {keywords}")
            
            # First, scrape job listings
            job_listings = await self.scrape_linkedin_jobs(
                keywords=keywords,
                location=location,
                max_results=max_results
            )
            
            if not job_listings['success']:
                return {
                    'success': False,
                    'error': job_listings['error'],
                    'jobs': [],
                    'skills_analysis': {}
                }
            
            # Extract job URLs for detailed scraping
            job_urls = [job.get('url', '') for job in job_listings['jobs'] if job.get('url')]
            
            # Scrape detailed job information
            detailed_jobs = await self.scrape_job_details(job_urls[:10])  # Limit to 10 for performance
            
            # Extract skills from all job descriptions
            all_skills = []
            all_requirements = []
            all_qualifications = []
            
            for job in detailed_jobs:
                if job.get('requirements'):
                    all_requirements.extend(job['requirements'])
                if job.get('qualifications'):
                    all_qualifications.extend(job['qualifications'])
                
                # Extract skills from job description
                description = job.get('description', '')
                if description:
                    skills = self._extract_skills_from_description(description)
                    all_skills.extend(skills)
            
            # Analyze skills frequency and importance
            skills_analysis = self._analyze_skills_frequency(all_skills)
            requirements_analysis = self._analyze_requirements_frequency(all_requirements)
            qualifications_analysis = self._analyze_qualifications_frequency(all_qualifications)
            
            logger.info(f"Extracted {len(skills_analysis)} unique skills from {len(detailed_jobs)} job postings")
            
            return {
                'success': True,
                'keywords': keywords,
                'location': location,
                'total_jobs_analyzed': len(detailed_jobs),
                'jobs': detailed_jobs,
                'skills_analysis': skills_analysis,
                'requirements_analysis': requirements_analysis,
                'qualifications_analysis': qualifications_analysis,
                'top_skills': list(skills_analysis.keys())[:20],
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in skills analysis scraping: {e}")
            return {
                'success': False,
                'error': str(e),
                'jobs': [],
                'skills_analysis': {}
            }
    
    async def scrape_company_jobs(self, 
                                company_name: str,
                                max_results: int = 20) -> Dict[str, Any]:
        """
        Scrape all jobs from a specific company
        
        Args:
            company_name: Name of the company
            max_results: Maximum number of jobs to return
            
        Returns:
            Dictionary with company job data
        """
        try:
            # Build company-specific search URL
            company_url = f"{self.base_linkedin_url}?keywords=&f_C={company_name}&f_TPR=r86400"
            
            logger.info(f"Scraping jobs for company: {company_name}")
            
            # Note: This would use mcp_brightdata-mcp_scrape_as_markdown(url=company_url)
            mock_company_data = await self._simulate_company_scrape(company_url)
            
            jobs = self._parse_linkedin_jobs(mock_company_data)
            
            if len(jobs) > max_results:
                jobs = jobs[:max_results]
            
            return {
                'company': company_name,
                'total_jobs': len(jobs),
                'jobs': jobs,
                'scraped_at': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping company jobs for {company_name}: {e}")
            return {
                'company': company_name,
                'success': False,
                'error': str(e),
                'jobs': [],
                'total_jobs': 0
            }
    
    async def scrape_all_job_categories(self) -> List[Dict[str, Any]]:
        """
        Scrape jobs from all configured categories
        
        Returns:
            List of job data from all categories
        """
        results = []
        
        for source in self.job_sources:
            result = await self.scrape_linkedin_jobs(
                keywords=source['keywords'],
                max_results=20
            )
            result['category'] = source['category']
            result['difficulty'] = source['difficulty']
            results.append(result)
            
            # Add delay between requests
            await asyncio.sleep(2)
        
        return results
    
    def _build_linkedin_search_url(self, 
                                 keywords: str, 
                                 location: str = "", 
                                 time_filter: str = "r3600") -> str:
        """Build LinkedIn job search URL with parameters"""
        params = {
            'keywords': keywords.replace(' ', '%20'),
            'f_TPR': time_filter
        }
        
        if location:
            params['location'] = location.replace(' ', '%20')
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_linkedin_url}?{query_string}"
    
    def _parse_linkedin_jobs(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Parse LinkedIn job data from markdown content"""
        jobs = []
        
        # This would parse the actual markdown content returned by MCP
        # For now, we'll create mock data based on the structure we saw earlier
        
        # Mock job data based on the LinkedIn scraping we did earlier
        mock_jobs = [
            {
                'title': 'Senior Full-Stack Developer',
                'company': 'Just Badge',
                'location': 'United States',
                'posted_time': '1 hour ago',
                'job_type': 'Full-time',
                'url': 'https://www.linkedin.com/jobs/view/senior-full-stack-developer-at-just-badge-4318857741',
                'description': 'Looking for a senior full-stack developer with experience in modern web technologies...'
            },
            {
                'title': 'Software Engineer (Java)',
                'company': 'OPENLANE',
                'location': 'Carmel, IN',
                'posted_time': '1 hour ago',
                'job_type': 'Full-time',
                'url': 'https://www.linkedin.com/jobs/view/software-engineer-java-at-openlane-4318856840',
                'description': 'Java software engineer position with focus on backend development...'
            },
            {
                'title': 'Full Stack Engineer (Java/React)',
                'company': 'OPENLANE',
                'location': 'Carmel, IN',
                'posted_time': '1 hour ago',
                'job_type': 'Full-time',
                'url': 'https://www.linkedin.com/jobs/view/full-stack-engineer-java-react-at-openlane-4318849801',
                'description': 'Full stack development role requiring Java and React expertise...'
            }
        ]
        
        return mock_jobs
    
    def _parse_job_details(self, markdown_content: str, job_url: str) -> Dict[str, Any]:
        """Parse detailed job information from markdown content"""
        # This would parse the actual job details page
        # For now, return mock data with realistic job descriptions
        mock_jobs = [
            {
                'url': job_url,
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc',
                'location': 'San Francisco, CA',
                'description': '''
                We are looking for a Senior Software Engineer to join our team. 
                You will be responsible for developing and maintaining our web applications using Python, Django, React, and AWS.
                
                Requirements:
                - 5+ years of experience with Python and Django
                - Strong knowledge of React.js and JavaScript
                - Experience with AWS services (EC2, S3, Lambda)
                - Knowledge of SQL databases (PostgreSQL, MySQL)
                - Experience with Docker and Kubernetes
                - Understanding of RESTful APIs and microservices
                - Bachelor's degree in Computer Science or related field
                - Experience with Git version control
                - Knowledge of testing frameworks (pytest, Jest)
                - Strong problem-solving and communication skills
                ''',
                'requirements': ['Python', 'Django', 'React', 'JavaScript', 'AWS', 'PostgreSQL', 'Docker', 'Kubernetes'],
                'qualifications': ['Bachelor\'s degree in Computer Science', '5+ years experience', 'RESTful APIs', 'Microservices'],
                'benefits': ['Health insurance', '401k', 'Remote work', 'Stock options'],
                'salary_range': '$140,000 - $200,000',
                'experience_level': 'Senior',
                'employment_type': 'Full-time',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'url': job_url,
                'title': 'Full Stack Developer',
                'company': 'StartupXYZ',
                'location': 'New York, NY',
                'description': '''
                Join our fast-growing startup as a Full Stack Developer. You'll work on both frontend and backend development.
                
                Technical Requirements:
                - Proficiency in JavaScript, TypeScript, and Node.js
                - Experience with React.js and Redux
                - Backend development with Express.js or NestJS
                - Database design with MongoDB or PostgreSQL
                - Experience with cloud platforms (AWS, Google Cloud, or Azure)
                - Knowledge of CI/CD pipelines
                - Experience with testing (Jest, Mocha, Chai)
                - Understanding of Agile development methodologies
                
                Nice to have:
                - Experience with GraphQL
                - Knowledge of containerization (Docker)
                - Experience with serverless architectures
                - Previous startup experience
                ''',
                'requirements': ['JavaScript', 'TypeScript', 'Node.js', 'React', 'Redux', 'Express.js', 'MongoDB', 'AWS'],
                'qualifications': ['Agile methodologies', 'CI/CD', 'Testing frameworks', 'GraphQL', 'Docker'],
                'benefits': ['Health insurance', 'Flexible hours', 'Equity', 'Learning budget'],
                'salary_range': '$100,000 - $150,000',
                'experience_level': 'Mid-level',
                'employment_type': 'Full-time',
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        # Return a random mock job for testing
        import random
        return random.choice(mock_jobs)
    
    async def _simulate_mcp_scrape(self, url: str) -> str:
        """Simulate MCP scraping - replace with actual MCP call in Cursor"""
        # This is where you would call: mcp_brightdata-mcp_scrape_as_markdown(url=url)
        # For now, return mock markdown content
        return f"Mock scraped content from {url}"
    
    async def _simulate_job_details_scrape(self, url: str) -> str:
        """Simulate job details scraping - replace with actual MCP call in Cursor"""
        return f"Mock job details from {url}"
    
    async def _simulate_company_scrape(self, url: str) -> str:
        """Simulate company scraping - replace with actual MCP call in Cursor"""
        return f"Mock company jobs from {url}"
    
    def extract_skills_from_jobs(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract and count skills mentioned in job postings"""
        skill_counts = {}
        
        # Common technical skills to look for
        common_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'sql', 'mongodb', 'postgresql', 'git', 'linux',
            'typescript', 'angular', 'vue', 'django', 'flask', 'spring',
            'microservices', 'api', 'rest', 'graphql', 'redis', 'elasticsearch'
        ]
        
        for job in jobs:
            description = job.get('description', '').lower()
            requirements = job.get('requirements', [])
            
            # Count skills in description
            for skill in common_skills:
                if skill in description:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            # Count skills in requirements
            for req in requirements:
                if isinstance(req, str):
                    req_lower = req.lower()
                    for skill in common_skills:
                        if skill in req_lower:
                            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))
    
    def analyze_job_trends(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in job postings"""
        if not jobs:
            return {}
        
        # Analyze job types
        job_types = {}
        locations = {}
        companies = {}
        
        for job in jobs:
            # Job type analysis
            job_type = job.get('job_type', 'Unknown')
            job_types[job_type] = job_types.get(job_type, 0) + 1
            
            # Location analysis
            location = job.get('location', 'Unknown')
            locations[location] = locations.get(location, 0) + 1
            
            # Company analysis
            company = job.get('company', 'Unknown')
            companies[company] = companies.get(company, 0) + 1
        
        return {
            'total_jobs': len(jobs),
            'job_types': dict(sorted(job_types.items(), key=lambda x: x[1], reverse=True)),
            'top_locations': dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_companies': dict(sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]),
            'skills_analysis': self.extract_skills_from_jobs(jobs)
        }
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract technical skills from job description text"""
        if not description:
            return []
        
        # Comprehensive list of technical skills to look for
        technical_skills = [
            # Programming Languages
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin',
            'scala', 'r', 'matlab', 'perl', 'haskell', 'clojure', 'elixir', 'dart', 'lua', 'bash', 'powershell',
            
            # Web Technologies
            'html', 'css', 'sass', 'scss', 'less', 'bootstrap', 'tailwind', 'jquery', 'ajax', 'json', 'xml',
            'rest', 'graphql', 'soap', 'websocket', 'http', 'https', 'ssl', 'tls',
            
            # Frontend Frameworks
            'react', 'vue', 'angular', 'ember', 'svelte', 'next.js', 'nuxt.js', 'gatsby', 'sveltekit',
            'redux', 'mobx', 'zustand', 'recoil', 'context api', 'hooks',
            
            # Backend Frameworks
            'django', 'flask', 'fastapi', 'express', 'nestjs', 'koa', 'hapi', 'sails', 'meteor',
            'spring', 'spring boot', 'quarkus', 'micronaut', 'vert.x', 'play framework',
            'rails', 'sinatra', 'hanami', 'grape', 'padrino',
            'laravel', 'symfony', 'codeigniter', 'cakephp', 'yii', 'zend',
            'asp.net', 'asp.net core', 'blazor', 'web api',
            
            # Databases
            'mysql', 'postgresql', 'sqlite', 'oracle', 'sql server', 'mariadb', 'cockroachdb',
            'mongodb', 'cassandra', 'redis', 'elasticsearch', 'couchdb', 'dynamodb',
            'neo4j', 'arangodb', 'orientdb', 'influxdb', 'timescaledb',
            
            # Cloud Platforms
            'aws', 'azure', 'gcp', 'google cloud', 'digital ocean', 'heroku', 'vercel', 'netlify',
            'ec2', 's3', 'lambda', 'rds', 'dynamodb', 'cloudfront', 'route53', 'iam',
            'azure functions', 'azure app service', 'azure sql', 'azure storage',
            'google cloud functions', 'google app engine', 'google cloud sql', 'firebase',
            
            # DevOps & Tools
            'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'circleci', 'travis ci',
            'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'packer',
            'prometheus', 'grafana', 'elk stack', 'splunk', 'datadog', 'new relic',
            
            # Mobile Development
            'ios', 'android', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
            'swift', 'objective-c', 'kotlin', 'java android', 'dart',
            
            # Data Science & ML
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv',
            'jupyter', 'matplotlib', 'seaborn', 'plotly', 'd3.js', 'tableau', 'power bi',
            'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'snowflake',
            
            # Testing
            'pytest', 'unittest', 'jest', 'mocha', 'chai', 'cypress', 'selenium', 'playwright',
            'junit', 'testng', 'mockito', 'wiremock', 'postman', 'newman',
            
            # Version Control
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
            
            # Other Technologies
            'microservices', 'serverless', 'api', 'sdk', 'cli', 'gui', 'tui',
            'blockchain', 'ethereum', 'solidity', 'web3', 'defi', 'nft',
            'iot', 'arduino', 'raspberry pi', 'mqtt', 'coap',
            'machine learning', 'artificial intelligence', 'deep learning', 'nlp', 'computer vision'
        ]
        
        # Convert description to lowercase for matching
        description_lower = description.lower()
        found_skills = []
        
        # Look for skills in the description
        for skill in technical_skills:
            if skill in description_lower:
                found_skills.append(skill)
        
        # Also look for skills with common variations
        skill_variations = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'db': 'database',
            'ui': 'user interface',
            'ux': 'user experience',
            'api': 'rest api',
            'sql': 'sql database',
            'nosql': 'no sql database',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'dl': 'deep learning',
            'cv': 'computer vision',
            'nlp': 'natural language processing'
        }
        
        for variation, full_name in skill_variations.items():
            if variation in description_lower and full_name not in found_skills:
                found_skills.append(full_name)
        
        return list(set(found_skills))  # Remove duplicates
    
    def _analyze_skills_frequency(self, skills_list: List[str]) -> Dict[str, int]:
        """Analyze frequency of skills across job postings"""
        if not skills_list:
            return {}
        
        skill_counts = {}
        for skill in skills_list:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by frequency (descending)
        return dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_requirements_frequency(self, requirements_list: List[str]) -> Dict[str, int]:
        """Analyze frequency of requirements across job postings"""
        if not requirements_list:
            return {}
        
        req_counts = {}
        for req in requirements_list:
            req_lower = req.lower().strip()
            if req_lower:
                req_counts[req_lower] = req_counts.get(req_lower, 0) + 1
        
        return dict(sorted(req_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_qualifications_frequency(self, qualifications_list: List[str]) -> Dict[str, int]:
        """Analyze frequency of qualifications across job postings"""
        if not qualifications_list:
            return {}
        
        qual_counts = {}
        for qual in qualifications_list:
            qual_lower = qual.lower().strip()
            if qual_lower:
                qual_counts[qual_lower] = qual_counts.get(qual_lower, 0) + 1
        
        return dict(sorted(qual_counts.items(), key=lambda x: x[1], reverse=True))
    
    def get_skills_insights(self, skills_analysis: Dict[str, int], top_n: int = 20) -> Dict[str, Any]:
        """Generate insights from skills analysis"""
        if not skills_analysis:
            return {}
        
        total_skills = sum(skills_analysis.values())
        top_skills = list(skills_analysis.items())[:top_n]
        
        # Categorize skills
        skill_categories = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_platforms': [],
            'devops_tools': [],
            'other': []
        }
        
        for skill, count in top_skills:
            skill_lower = skill.lower()
            if any(lang in skill_lower for lang in ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin']):
                skill_categories['programming_languages'].append((skill, count))
            elif any(fw in skill_lower for fw in ['react', 'vue', 'angular', 'django', 'flask', 'express', 'spring', 'rails', 'laravel']):
                skill_categories['frameworks'].append((skill, count))
            elif any(db in skill_lower for db in ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle']):
                skill_categories['databases'].append((skill, count))
            elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes']):
                skill_categories['cloud_platforms'].append((skill, count))
            elif any(devops in skill_lower for devops in ['jenkins', 'git', 'terraform', 'ansible', 'ci/cd', 'monitoring']):
                skill_categories['devops_tools'].append((skill, count))
            else:
                skill_categories['other'].append((skill, count))
        
        return {
            'total_skills_found': len(skills_analysis),
            'total_skill_mentions': total_skills,
            'top_skills': top_skills,
            'skill_categories': skill_categories,
            'most_demanded_skill': top_skills[0] if top_skills else None,
            'skills_diversity_score': len(skills_analysis) / max(total_skills, 1)
        }

# Example usage and testing
async def test_brightdata_service():
    """Test the BrightData MCP service"""
    print("🧪 Testing BrightData MCP Service")
    print("=" * 50)
    
    service = BrightDataMCPService()
    
    # Test basic job scraping
    print("📚 Testing LinkedIn job scraping...")
    jobs = await service.scrape_linkedin_jobs("software engineer", max_results=5)
    
    if jobs['success']:
        print(f"✅ Scraped {jobs['total_jobs']} jobs")
        for job in jobs['jobs'][:3]:
            print(f"   - {job['title']} at {job['company']}")
    else:
        print(f"❌ Scraping failed: {jobs['error']}")
    
    # Test trend analysis
    if jobs['success'] and jobs['jobs']:
        print("\n📊 Testing trend analysis...")
        trends = service.analyze_job_trends(jobs['jobs'])
        print(f"   - Top skills: {list(trends['skills_analysis'].keys())[:5]}")
        print(f"   - Job types: {trends['job_types']}")
    
    # Test skills analysis
    print("\n🔍 Testing skills analysis...")
    skills_analysis = await service.scrape_jobs_with_skills_analysis(
        keywords="software engineer",
        location="San Francisco",
        max_results=5
    )
    
    if skills_analysis['success']:
        print(f"✅ Analyzed {skills_analysis['total_jobs_analyzed']} jobs for skills")
        print(f"   - Top skills: {skills_analysis['top_skills'][:10]}")
        
        # Get detailed insights
        insights = service.get_skills_insights(skills_analysis['skills_analysis'])
        print(f"   - Total skills found: {insights['total_skills_found']}")
        print(f"   - Most demanded: {insights['most_demanded_skill']}")
        
        # Show skill categories
        categories = insights['skill_categories']
        for category, skills in categories.items():
            if skills:
                print(f"   - {category}: {[skill[0] for skill in skills[:3]]}")
    else:
        print(f"❌ Skills analysis failed: {skills_analysis['error']}")

if __name__ == "__main__":
    asyncio.run(test_brightdata_service())
