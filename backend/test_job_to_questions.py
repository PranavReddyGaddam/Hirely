#!/usr/bin/env python3
"""
Job Posting to Interview Questions Test Tool.
Integrates Groq service with scraper service to generate interview questions from job postings.
"""

import asyncio
import sys
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import re

# Import our services
from app.services.groq_service import GroqService
from app.services.crawl4ai_service import Crawl4AIService

class JobToQuestionsGenerator:
    """Generate interview questions from real interview experiences using job postings as context"""
    
    def __init__(self):
        try:
            self.groq_service = GroqService()
            if not self.groq_service.client:
                print("⚠️  Groq service not available - questions will be generated using fallback method")
        except Exception as e:
            print(f"⚠️  Failed to initialize Groq service: {e}")
            self.groq_service = None
        self.crawler = None
        
        # Interview experience websites to scrape
        self.interview_sources = [
            {
                "name": "LeetCode Discuss",
                "base_url": "https://leetcode.com/discuss/interview-question/",
                "search_patterns": ["company", "position", "level"]
            },
            {
                "name": "Glassdoor Interviews",
                "base_url": "https://www.glassdoor.com/Interview/",
                "search_patterns": ["company", "position"]
            },
            {
                "name": "Indeed Interview Reviews",
                "base_url": "https://www.indeed.com/cmp/",
                "search_patterns": ["company", "interviews"]
            },
            {
                "name": "Blind Interview Experiences",
                "base_url": "https://www.teamblind.com/",
                "search_patterns": ["interview", "company"]
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
    
    async def generate_questions_from_job_posting(self, job_url: str):
        """Generate interview questions from real interview experiences using job posting as context"""
        print(f"💼 Processing Job Posting: {job_url}")
        print("=" * 80)
        
        try:
            # Step 1: Scrape job posting to understand role/company/level
            print("🕷️  Step 1: Analyzing job posting...")
            job_info = await self._scrape_job_posting(job_url)
            
            if not job_info:
                print("❌ Failed to scrape job posting")
                return None
            
            print(f"✅ Job posting analyzed successfully")
            print(f"   - Company: {job_info.get('company', 'Unknown')}")
            print(f"   - Position: {job_info.get('position', 'Unknown')}")
            print(f"   - Level: {job_info['experience_level']}")
            print(f"   - Skills: {len(job_info['required_skills'])}")
            
            # Step 2: Find similar job postings and extract company info
            print(f"\n🔍 Step 2: Finding similar roles and company info...")
            company_info = await self._extract_company_info(job_info)
            
            # Step 3: Scrape real interview experiences
            print(f"\n📚 Step 3: Scraping real interview experiences...")
            interview_experiences = await self._scrape_interview_experiences(job_info, company_info)
            
            # Step 4: Extract questions from real experiences
            print(f"\n❓ Step 4: Extracting questions from real interviews...")
            real_questions = await self._extract_questions_from_experiences(interview_experiences)
            
            # Step 5: Generate additional questions based on patterns
            print(f"\n🤖 Step 5: Generating additional questions based on patterns...")
            generated_questions = await self._generate_questions_from_patterns(job_info, real_questions)
            
            # Step 6: Combine and format results
            print(f"\n📋 Step 6: Formatting results...")
            results = {
                "job_url": job_url,
                "scraped_at": datetime.now().isoformat(),
                "job_info": job_info,
                "company_info": company_info,
                "interview_experiences": interview_experiences,
                "real_questions": real_questions,
                "generated_questions": generated_questions,
                "total_questions": len(real_questions) + len(generated_questions)
            }
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_interview_questions_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filename}")
            print(f"📋 Each question includes source URL for verification")
            
            # Display results
            self._display_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            return None
    
    async def _scrape_job_posting(self, url: str):
        """Scrape job posting and extract requirements"""
        try:
            # Try to scrape with timeout handling
            try:
                result = await self.crawler.arun(url=url)
            except Exception as e:
                print(f"⚠️  Crawler error: {e}")
                print("🔄 Using fallback method with generic job requirements...")
                return self._create_fallback_job_info(url)
            
            if not result.success:
                print(f"❌ Failed to scrape URL: {result.error if hasattr(result, 'error') else 'Unknown error'}")
                print("🔄 Using fallback method with generic job requirements...")
                return self._create_fallback_job_info(url)
            
            # Parse HTML content
            soup = BeautifulSoup(result.html, 'html.parser') if result.html else BeautifulSoup("", 'html.parser')
            all_text = soup.get_text().lower()
            
            # Extract job information
            job_info = {
                "url": url,
                "required_skills": self._extract_skills(soup, all_text),
                "technologies": self._extract_technologies(soup, all_text),
                "experience_level": self._extract_experience_level(all_text),
                "education": self._extract_education(all_text),
                "location": self._extract_location(soup, all_text),
                "job_type": self._extract_job_type(all_text),
                "salary_range": self._extract_salary_range(all_text),
                "responsibilities": self._extract_responsibilities(soup, all_text),
                "qualifications": self._extract_qualifications(soup, all_text)
            }
            
            # Intelligently filter and prioritize skills
            job_info = self._prioritize_skills(job_info)
            
            return job_info
            
        except Exception as e:
            print(f"❌ Error scraping job posting: {e}")
            return None
    
    async def _generate_technical_questions(self, job_info):
        """Generate technical questions based on job requirements"""
        try:
            # Check if Groq service is available
            if not self.groq_service or not self.groq_service.client:
                print("🔄 Using fallback method for technical questions")
                return self._generate_fallback_technical_questions(job_info)
            
            # Prepare context for Groq using prioritized skills
            primary_skills = job_info.get('primary_skills', [])
            secondary_skills = job_info.get('secondary_skills', [])
            experience = job_info['experience_level']
            
            # Create prompt for technical questions
            prompt = f"""
            Generate 5 technical interview questions for a {experience} position. Focus on CORE PROGRAMMING CONCEPTS rather than specific technologies.
            
            Job Context: Primary Languages: {', '.join(primary_skills)} | Frameworks: {', '.join(secondary_skills)}
            
            IMPORTANT: Most candidates specialize in 1-2 languages, not all listed technologies. Create questions that:
            1. Test fundamental programming concepts (OOP, algorithms, data structures)
            2. Focus on problem-solving approach, not specific syntax
            3. Allow candidates to use their preferred language/framework
            4. Cover system design and architecture thinking
            5. Test debugging and optimization skills
            6. Are language-agnostic where possible
            
            Avoid questions that require knowledge of specific frameworks or tools.
            Focus on transferable skills and core computer science concepts.
            
            Format the response as a JSON array with this structure:
            [
                {{
                    "question": "Question text here",
                    "category": "Technical",
                    "difficulty": "Medium/Hard",
                    "skill_focus": "Core concept being tested",
                    "expected_answer_type": "Code/Explanation/Design"
                }}
            ]
            
            Return only the JSON array, no additional text.
            """
            
            # Generate questions using Groq
            response = await self.groq_service.generate_questions(
                prompt=prompt,
                num_questions=5,
                difficulty="medium"
            )
            
            # Parse the response
            questions = self._parse_groq_response(response)
            
            print(f"✅ Generated {len(questions)} technical questions")
            return questions
            
        except Exception as e:
            print(f"❌ Error generating technical questions: {e}")
            print("🔄 Using fallback method")
            return self._generate_fallback_technical_questions(job_info)
    
    async def _generate_behavioral_questions(self, job_info):
        """Generate behavioral questions based on job requirements"""
        try:
            # Check if Groq service is available
            if not self.groq_service or not self.groq_service.client:
                print("🔄 Using fallback method for behavioral questions")
                return self._generate_fallback_behavioral_questions(job_info)
            
            # Prepare context for Groq
            skills_text = ", ".join(job_info['required_skills'][:10])
            experience = job_info['experience_level']
            responsibilities = job_info['responsibilities'][:5]  # Top 5 responsibilities
            
            # Create prompt for behavioral questions
            prompt = f"""
            Generate 5 behavioral interview questions for a {experience} position with these requirements:
            
            Required Skills: {skills_text}
            Key Responsibilities: {', '.join(responsibilities)}
            
            The questions should be:
            1. Relevant to the role and responsibilities
            2. Appropriate for the experience level ({experience})
            3. Focus on soft skills, leadership, teamwork, problem-solving
            4. Cover different behavioral aspects (leadership, conflict resolution, time management, etc.)
            5. Use the STAR method (Situation, Task, Action, Result)
            
            Format the response as a JSON array with this structure:
            [
                {{
                    "question": "Question text here",
                    "category": "Behavioral",
                    "difficulty": "Medium",
                    "skill_focus": "Leadership/Teamwork/Problem-solving",
                    "expected_answer_type": "STAR Method Example"
                }}
            ]
            
            Return only the JSON array, no additional text.
            """
            
            # Generate questions using Groq
            response = await self.groq_service.generate_questions(
                prompt=prompt,
                num_questions=5,
                difficulty="medium"
            )
            
            # Parse the response
            questions = self._parse_groq_response(response)
            
            print(f"✅ Generated {len(questions)} behavioral questions")
            return questions
            
        except Exception as e:
            print(f"❌ Error generating behavioral questions: {e}")
            print("🔄 Using fallback method")
            return self._generate_fallback_behavioral_questions(job_info)
    
    def _parse_groq_response(self, response):
        """Parse Groq response and extract questions"""
        try:
            # Try to parse as JSON
            if isinstance(response, str):
                # Clean the response
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.endswith('```'):
                    response = response[:-3]
                response = response.strip()
                
                questions = json.loads(response)
                
                # Ensure it's a list
                if isinstance(questions, dict):
                    questions = [questions]
                
                return questions
            else:
                return []
                
        except json.JSONDecodeError:
            print(f"⚠️  Failed to parse Groq response as JSON")
            print(f"Response: {response[:200]}...")
            return []
        except Exception as e:
            print(f"❌ Error parsing Groq response: {e}")
            return []
    
    def _display_results(self, results):
        """Display the generated questions"""
        print(f"\n🎯 Real Interview Questions Analysis")
        print("=" * 80)
        
        print(f"\n📊 Summary:")
        print(f"   - Total Questions: {results['total_questions']}")
        print(f"   - Real Interview Questions: {len(results.get('real_questions', []))}")
        print(f"   - Generated Questions: {len(results.get('generated_questions', []))}")
        print(f"   - Interview Experiences: {len(results.get('interview_experiences', []))}")
        
        if results.get('real_questions'):
            print(f"\n📚 Real Interview Questions (from actual experiences):")
            for i, q in enumerate(results['real_questions'][:5], 1):
                print(f"   {i}. {q.get('question', 'N/A')}")
                print(f"      Source: {q.get('source', 'N/A')} | Company: {q.get('company', 'N/A')}")
                print(f"      Category: {q.get('category', 'N/A')} | Difficulty: {q.get('difficulty', 'N/A')}")
                print(f"      🔗 Source URL: {q.get('source_url', 'N/A')}")
        
        if results.get('generated_questions'):
            print(f"\n🤖 Generated Questions (based on patterns):")
            for i, q in enumerate(results['generated_questions'], 1):
                print(f"   {i}. {q.get('question', 'N/A')}")
                print(f"      Skill: {q.get('skill_focus', 'N/A')} | Difficulty: {q.get('difficulty', 'N/A')}")
        
        if results.get('interview_experiences'):
            print(f"\n📖 Interview Experience Sources:")
            sources = {}
            for exp in results['interview_experiences']:
                source = exp.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            for source, count in sources.items():
                print(f"   - {source}: {count} experiences")
    
    # Helper methods for job scraping (simplified versions)
    def _extract_skills(self, soup, text):
        """Extract required skills from job posting"""
        skills = []
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'postgresql', 'mysql', 'mongodb', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'git', 'agile', 'scrum', 'machine learning',
            'ai', 'data science', 'analytics', 'communication', 'leadership',
            'project management', 'problem solving', 'teamwork', 'collaboration'
        ]
        
        for skill in skill_keywords:
            if skill in text and skill not in skills:
                skills.append(skill.title())
        
        return skills
    
    def _extract_technologies(self, soup, text):
        """Extract technologies from job posting"""
        technologies = []
        tech_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'express', 'django', 'flask', 'spring', 'laravel', 'php',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'linux', 'windows', 'macos', 'html', 'css', 'bootstrap', 'tailwind',
            'graphql', 'rest', 'api', 'microservices', 'serverless'
        ]
        
        for tech in tech_keywords:
            if tech in text and tech not in technologies:
                technologies.append(tech.title())
        
        return technologies
    
    def _extract_experience_level(self, text):
        """Extract experience level from job posting"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*experience',
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'senior\s+(\w+)',
            r'junior\s+(\w+)',
            r'entry\s+level',
            r'mid\s+level',
            r'lead\s+(\w+)',
            r'principal\s+(\w+)'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).title()
        
        return "Not specified"
    
    def _extract_education(self, text):
        """Extract education requirements"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'diploma', 'certification',
            'computer science', 'engineering', 'mathematics', 'statistics'
        ]
        
        for keyword in education_keywords:
            if keyword in text:
                return keyword.title()
        
        return "Not specified"
    
    def _extract_location(self, soup, text):
        """Extract job location"""
        location_elements = soup.find_all(['span', 'div', 'p'], 
                                        string=lambda text: text and any(
                                            keyword in text.lower() for keyword in 
                                            ['location', 'based', 'office', 'remote', 'hybrid']
                                        ))
        
        for element in location_elements:
            element_text = element.get_text().strip()
            if len(element_text) < 100:
                return element_text
        
        return "Not specified"
    
    def _extract_job_type(self, text):
        """Extract job type"""
        job_types = ['full-time', 'part-time', 'contract', 'freelance', 'remote', 'hybrid']
        
        for job_type in job_types:
            if job_type in text:
                return job_type.title()
        
        return "Not specified"
    
    def _extract_salary_range(self, text):
        """Extract salary range"""
        salary_patterns = [
            r'\$[\d,]+(?:k|K)?\s*-\s*\$[\d,]+(?:k|K)?',
            r'\$[\d,]+(?:k|K)?\s*per\s*year',
            r'\$[\d,]+(?:k|K)?\s*annually'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return "Not specified"
    
    def _extract_responsibilities(self, soup, text):
        """Extract job responsibilities"""
        responsibilities = []
        resp_sections = soup.find_all(['div', 'section', 'ul'], 
                                     string=lambda text: text and any(
                                         keyword in text.lower() for keyword in 
                                         ['responsibilities', 'duties', 'what you will do']
                                     ))
        
        for section in resp_sections:
            items = section.find_all('li')
            for item in items:
                resp_text = item.get_text().strip()
                if len(resp_text) > 10 and len(resp_text) < 200:
                    responsibilities.append(resp_text)
        
        return responsibilities[:10]
    
    def _extract_qualifications(self, soup, text):
        """Extract qualifications"""
        qualifications = []
        qual_sections = soup.find_all(['div', 'section', 'ul'], 
                                     string=lambda text: text and any(
                                         keyword in text.lower() for keyword in 
                                         ['qualifications', 'requirements', 'must have']
                                     ))
        
        for section in qual_sections:
            items = section.find_all('li')
            for item in items:
                qual_text = item.get_text().strip()
                if len(qual_text) > 10 and len(qual_text) < 200:
                    qualifications.append(qual_text)
        
        return qualifications[:10]
    
    def _prioritize_skills(self, job_info):
        """Intelligently filter and prioritize skills based on job requirements"""
        # Core programming languages (most important)
        core_languages = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby']
        
        # Frameworks and libraries (secondary)
        frameworks = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 'rails']
        
        # Tools and platforms (tertiary)
        tools = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins', 'linux', 'windows']
        
        # Soft skills (important but not for technical questions)
        soft_skills = ['communication', 'leadership', 'teamwork', 'problem solving', 'collaboration', 'project management']
        
        # Filter and categorize skills
        prioritized_skills = {
            'core_languages': [],
            'frameworks': [],
            'tools': [],
            'soft_skills': [],
            'other': []
        }
        
        all_skills = job_info['required_skills'] + job_info['technologies']
        
        for skill in all_skills:
            skill_lower = skill.lower()
            if skill_lower in core_languages:
                prioritized_skills['core_languages'].append(skill)
            elif skill_lower in frameworks:
                prioritized_skills['frameworks'].append(skill)
            elif skill_lower in tools:
                prioritized_skills['tools'].append(skill)
            elif skill_lower in soft_skills:
                prioritized_skills['soft_skills'].append(skill)
            else:
                prioritized_skills['other'].append(skill)
        
        # Remove duplicates and limit to most important
        for category in prioritized_skills:
            prioritized_skills[category] = list(set(prioritized_skills[category]))[:3]  # Top 3 per category
        
        # Update job_info with prioritized skills
        job_info['prioritized_skills'] = prioritized_skills
        job_info['primary_skills'] = prioritized_skills['core_languages'][:2]  # Top 2 core languages
        job_info['secondary_skills'] = prioritized_skills['frameworks'][:2]  # Top 2 frameworks
        
        print(f"🎯 Prioritized Skills Analysis:")
        print(f"   - Primary Languages: {job_info['primary_skills']}")
        print(f"   - Secondary Frameworks: {job_info['secondary_skills']}")
        print(f"   - Tools & Platforms: {prioritized_skills['tools'][:3]}")
        
        return job_info
    
    def _create_fallback_job_info(self, url):
        """Create fallback job info when scraping fails"""
        print("🔄 Creating fallback job information...")
        
        # Extract company from URL
        company = self._extract_company_name({"url": url})
        
        # Create realistic fallback job requirements
        fallback_skills = [
            "Python", "JavaScript", "Java", "C++", "SQL", "Git", "Docker", 
            "AWS", "React", "Node.js", "Spring Boot", "REST APIs"
        ]
        
        fallback_technologies = [
            "Python", "JavaScript", "Java", "React", "Node.js", "Spring Boot",
            "Docker", "Kubernetes", "AWS", "SQL", "MongoDB", "Redis"
        ]
        
        return {
            "url": url,
            "required_skills": fallback_skills,
            "technologies": fallback_technologies,
            "experience_level": "Entry Level",
            "education": "Bachelor's Degree",
            "location": "Remote",
            "job_type": "Full-time",
            "salary_range": "$80,000 - $120,000",
            "responsibilities": [
                "Develop and maintain software applications",
                "Collaborate with cross-functional teams",
                "Write clean, efficient code",
                "Participate in code reviews"
            ],
            "qualifications": [
                "Bachelor's degree in Computer Science or related field",
                "Strong programming skills",
                "Experience with modern development tools",
                "Good problem-solving abilities"
            ]
        }
    
    async def _extract_company_info(self, job_info):
        """Extract company information from job posting"""
        try:
            # Extract company name from job posting
            company_name = self._extract_company_name(job_info)
            position_title = self._extract_position_title(job_info)
            
            company_info = {
                "company_name": company_name,
                "position_title": position_title,
                "industry": self._extract_industry(job_info),
                "company_size": self._extract_company_size(job_info),
                "location": job_info.get('location', 'Unknown')
            }
            
            print(f"🏢 Company Info: {company_name} - {position_title}")
            return company_info
            
        except Exception as e:
            print(f"❌ Error extracting company info: {e}")
            return {"company_name": "Unknown", "position_title": "Unknown"}
    
    async def _scrape_interview_experiences(self, job_info, company_info):
        """Scrape real interview experiences from various sources"""
        interview_experiences = []
        
        company_name = company_info.get('company_name', '').lower()
        position_title = company_info.get('position_title', '').lower()
        
        print(f"🔍 Searching for interview experiences at {company_name} for {position_title}")
        
        for source in self.interview_sources:
            try:
                print(f"📚 Checking {source['name']}...")
                
                # Construct search URLs based on source
                search_urls = self._construct_search_urls(source, company_name, position_title)
                
                for url in search_urls:
                    try:
                        result = await self.crawler.arun(url=url)
                        if result.success:
                            experiences = self._extract_interview_experiences_from_page(result, source['name'])
                            interview_experiences.extend(experiences)
                            print(f"   ✅ Found {len(experiences)} experiences from {source['name']}")
                    except Exception as e:
                        print(f"   ⚠️  Error scraping {source['name']}: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error with {source['name']}: {e}")
                continue
        
        print(f"📊 Total interview experiences found: {len(interview_experiences)}")
        return interview_experiences
    
    async def _generate_questions_from_patterns(self, job_info, real_questions):
        """Generate additional questions based on patterns found in real experiences"""
        try:
            if not self.groq_service or not self.groq_service.client:
                print("🔄 Using fallback method for pattern-based questions")
                return self._generate_fallback_technical_questions(job_info)
            
            # Analyze patterns in real questions
            question_patterns = self._analyze_question_patterns(real_questions)
            
            # Create prompt based on patterns
            prompt = f"""
            Based on these real interview questions from {job_info.get('company', 'the company')}:
            
            {self._format_questions_for_prompt(real_questions[:5])}
            
            Generate 3 additional interview questions that:
            1. Follow the same style and difficulty level
            2. Are relevant to the role and company
            3. Test similar skills and concepts
            4. Are realistic and practical
            
            Format as JSON array with question, category, difficulty, and skill_focus.
            """
            
            response = await self.groq_service.generate_questions(
                prompt=prompt,
                num_questions=3,
                difficulty="medium"
            )
            
            questions = self._parse_groq_response(response)
            print(f"✅ Generated {len(questions)} pattern-based questions")
            return questions
            
        except Exception as e:
            print(f"❌ Error generating pattern-based questions: {e}")
            return self._generate_fallback_technical_questions(job_info)
    
    def _generate_fallback_technical_questions(self, job_info):
        """Generate fallback technical questions when Groq is not available"""
        # Focus on core programming concepts rather than specific technologies
        # This approach is more realistic for interviews
        
        question_templates = [
            {
                "question": "Explain the difference between a class and an object in object-oriented programming. Can you give me a practical example?",
                "category": "Technical",
                "difficulty": "Medium",
                "skill_focus": "Programming Fundamentals",
                "expected_answer_type": "Explanation with Example"
            },
            {
                "question": "How would you approach debugging a performance issue in a web application? Walk me through your debugging process.",
                "category": "Technical",
                "difficulty": "Medium",
                "skill_focus": "Problem Solving & Debugging",
                "expected_answer_type": "Process/Explanation"
            },
            {
                "question": "Describe a time when you had to optimize code for better performance. What was the bottleneck and how did you solve it?",
                "category": "Technical",
                "difficulty": "Medium",
                "skill_focus": "Performance Optimization",
                "expected_answer_type": "STAR Method + Technical Details"
            },
            {
                "question": "How would you design a simple REST API? What endpoints would you create and what data would they return?",
                "category": "Technical",
                "difficulty": "Medium",
                "skill_focus": "API Design",
                "expected_answer_type": "Design/Architecture"
            },
            {
                "question": "Explain the concept of version control. Why is it important, and how would you handle a merge conflict?",
                "category": "Technical",
                "difficulty": "Easy",
                "skill_focus": "Version Control",
                "expected_answer_type": "Explanation + Process"
            }
        ]
        
        return question_templates
    
    def _generate_fallback_behavioral_questions(self, job_info):
        """Generate fallback behavioral questions when Groq is not available"""
        experience = job_info['experience_level']
        responsibilities = job_info['responsibilities'][:3]  # Top 3 responsibilities
        
        # Template questions based on common behavioral scenarios
        question_templates = [
            {
                "question": f"Tell me about a time when you had to learn a new technology quickly for a project. How did you approach it?",
                "category": "Behavioral",
                "difficulty": "Medium",
                "skill_focus": "Learning/Adaptability",
                "expected_answer_type": "STAR Method Example"
            },
            {
                "question": f"Describe a situation where you had to work with a difficult team member. How did you handle it?",
                "category": "Behavioral",
                "difficulty": "Medium",
                "skill_focus": "Teamwork/Conflict Resolution",
                "expected_answer_type": "STAR Method Example"
            },
            {
                "question": f"Give me an example of a time when you had to meet a tight deadline. What was your approach?",
                "category": "Behavioral",
                "difficulty": "Medium",
                "skill_focus": "Time Management",
                "expected_answer_type": "STAR Method Example"
            },
            {
                "question": f"Tell me about a project where you had to take initiative to solve a problem. What was the outcome?",
                "category": "Behavioral",
                "difficulty": "Medium",
                "skill_focus": "Initiative/Problem Solving",
                "expected_answer_type": "STAR Method Example"
            },
            {
                "question": f"Describe a time when you had to explain a complex technical concept to a non-technical audience. How did you approach it?",
                "category": "Behavioral",
                "difficulty": "Medium",
                "skill_focus": "Communication",
                "expected_answer_type": "STAR Method Example"
            }
        ]
        
        return question_templates
    
    def _extract_company_name(self, job_info):
        """Extract company name from job posting"""
        # Try to extract from URL or content
        # For Apple job posting, extract from URL
        if 'apple.com' in str(job_info.get('url', '')):
            return "Apple"
        elif 'google.com' in str(job_info.get('url', '')):
            return "Google"
        elif 'microsoft.com' in str(job_info.get('url', '')):
            return "Microsoft"
        elif 'amazon.com' in str(job_info.get('url', '')):
            return "Amazon"
        elif 'meta.com' in str(job_info.get('url', '')):
            return "Meta"
        else:
            return "Unknown Company"
    
    def _extract_position_title(self, job_info):
        """Extract position title from job posting"""
        # This would need to be implemented based on the job posting structure
        return "Software Engineer"
    
    def _extract_industry(self, job_info):
        """Extract industry from job posting"""
        return "Technology"
    
    def _extract_company_size(self, job_info):
        """Extract company size from job posting"""
        return "Medium"
    
    def _construct_search_urls(self, source, company_name, position_title):
        """Construct search URLs for different interview experience sources"""
        urls = []
        
        if source['name'] == "LeetCode Discuss":
            # LeetCode discuss URLs
            urls.append(f"https://leetcode.com/discuss/interview-question/?currentPage=1&orderBy=hot&query={company_name}")
        elif source['name'] == "Glassdoor Interviews":
            # Glassdoor interview URLs
            urls.append(f"https://www.glassdoor.com/Interview/{company_name}-interview-questions-SRCH_KO0,{len(company_name)}.htm")
        elif source['name'] == "Indeed Interview Reviews":
            # Indeed company pages
            urls.append(f"https://www.indeed.com/cmp/{company_name}/reviews")
        
        return urls
    
    def _extract_interview_experiences_from_page(self, result, source_name):
        """Extract interview experiences from a scraped page"""
        experiences = []
        
        # This would need to be implemented based on the specific source structure
        # For now, return a placeholder with source URL
        experiences.append({
            "content": "Sample interview experience content",
            "source": source_name,
            "source_url": result.url if hasattr(result, 'url') else "Unknown URL",
            "company": "Sample Company",
            "position": "Software Engineer"
        })
        
        return experiences
    
    async def _extract_questions_from_experiences(self, interview_experiences):
        """Extract actual interview questions from real experiences"""
        real_questions = []
        
        for experience in interview_experiences:
            # Extract questions from the experience text
            questions = self._parse_questions_from_text(experience.get('content', ''))
            
            for question in questions:
                real_questions.append({
                    "question": question,
                    "source": experience.get('source', 'Unknown'),
                    "source_url": experience.get('source_url', 'Unknown URL'),
                    "company": experience.get('company', 'Unknown'),
                    "position": experience.get('position', 'Unknown'),
                    "experience_type": "Real Interview Experience",
                    "difficulty": self._assess_question_difficulty(question),
                    "category": self._categorize_question(question)
                })
        
        # Remove duplicates while preserving order
        seen_questions = set()
        unique_questions = []
        for q in real_questions:
            question_text = q['question'].lower().strip()
            if question_text not in seen_questions:
                seen_questions.add(question_text)
                unique_questions.append(q)
        
        print(f"❓ Extracted {len(unique_questions)} unique real interview questions")
        return unique_questions[:10]  # Limit to top 10
    
    def _parse_questions_from_text(self, text):
        """Parse interview questions from experience text"""
        questions = []
        
        # Look for question patterns in the text
        import re
        
        # Common question patterns
        question_patterns = [
            r'[Qq]uestion\s*\d*[:\-]?\s*([^.!?]*\?)',
            r'[Ww]hat\s+[^.!?]*\?',
            r'[Hh]ow\s+[^.!?]*\?',
            r'[Ww]hy\s+[^.!?]*\?',
            r'[Ee]xplain\s+[^.!?]*\?',
            r'[Dd]escribe\s+[^.!?]*\?'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                question = match.strip()
                if len(question) > 20 and len(question) < 200:
                    questions.append(question)
        
        return questions
    
    def _assess_question_difficulty(self, question):
        """Assess the difficulty level of a question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['explain', 'describe', 'what', 'why']):
            return "Easy"
        elif any(word in question_lower for word in ['how', 'implement', 'design', 'optimize']):
            return "Medium"
        elif any(word in question_lower for word in ['complex', 'advanced', 'algorithm', 'system design']):
            return "Hard"
        else:
            return "Medium"
    
    def _categorize_question(self, question):
        """Categorize a question as technical or behavioral"""
        question_lower = question.lower()
        
        behavioral_keywords = ['tell me about', 'describe a time', 'situation', 'experience', 'team', 'leadership']
        technical_keywords = ['code', 'algorithm', 'data structure', 'system', 'database', 'api', 'debug']
        
        if any(keyword in question_lower for keyword in behavioral_keywords):
            return "Behavioral"
        elif any(keyword in question_lower for keyword in technical_keywords):
            return "Technical"
        else:
            return "General"
    
    def _analyze_question_patterns(self, real_questions):
        """Analyze patterns in real interview questions"""
        patterns = {
            "common_topics": [],
            "difficulty_distribution": {"Easy": 0, "Medium": 0, "Hard": 0},
            "question_types": {"Technical": 0, "Behavioral": 0, "General": 0}
        }
        
        for q in real_questions:
            patterns["difficulty_distribution"][q.get("difficulty", "Medium")] += 1
            patterns["question_types"][q.get("category", "General")] += 1
        
        return patterns
    
    def _format_questions_for_prompt(self, questions):
        """Format questions for use in Groq prompt"""
        formatted = []
        for i, q in enumerate(questions, 1):
            formatted.append(f"{i}. {q.get('question', 'N/A')}")
        return "\n".join(formatted)

async def main():
    """Main function"""
    print("💼 Job Posting to Interview Questions Generator")
    print("=" * 60)
    print("This tool scrapes job postings and generates relevant interview questions")
    print("using Groq AI based on the extracted skills and requirements.")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # URL provided as command line argument
        job_url = sys.argv[1]
        print(f"🔗 Processing Job Posting: {job_url}")
        
        async with JobToQuestionsGenerator() as generator:
            results = await generator.generate_questions_from_job_posting(job_url)
            
            if results:
                print(f"\n🎉 Successfully generated {results['total_questions']} interview questions!")
            else:
                print(f"\n❌ Failed to generate questions")
    else:
        # Interactive mode
        print("\n📝 Enter a job posting URL to generate questions (or 'quit' to exit):")
        print("💡 Try job postings from LinkedIn, Indeed, Glassdoor, etc.")
        print("🔧 If Apple/Google URLs timeout, try simpler job sites like Indeed or LinkedIn")
        print("📋 Example URLs:")
        print("   - https://www.linkedin.com/jobs/view/...")
        print("   - https://www.indeed.com/viewjob?jk=...")
        print("   - https://jobs.apple.com/... (may timeout)")
        
        async with JobToQuestionsGenerator() as generator:
            while True:
                try:
                    job_url = input("\n🔗 Job Posting URL: ").strip()
                    
                    if job_url.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    if not job_url:
                        print("❌ Please enter a valid URL")
                        continue
                    
                    if not job_url.startswith(('http://', 'https://')):
                        job_url = 'https://' + job_url
                    
                    results = await generator.generate_questions_from_job_posting(job_url)
                    
                    if results:
                        print(f"\n🎉 Successfully generated {results['total_questions']} interview questions!")
                    else:
                        print(f"\n❌ Failed to generate questions")
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
