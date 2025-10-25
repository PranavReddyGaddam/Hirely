"""
Question Generator Service

Generates interview questions based on job role, company, and customization parameters.
Currently uses mock questions - will integrate with Groq on hackathon day.
"""

from typing import List, Dict, Any
from app.schemas.interview import QuestionCreate
import random

class QuestionGeneratorService:
    """
    Service for generating interview questions based on job requirements and preferences.
    """
    
    def __init__(self):
        # Mock question pools for different interview types
        self.behavioral_questions = [
            "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
            "Describe a situation where you had to learn a new technology quickly. What was your approach?",
            "Give me an example of a project where you had to meet a tight deadline. How did you manage it?",
            "Tell me about a time when you had to give difficult feedback to a colleague. How did you approach it?",
            "Describe a situation where you had to work with limited resources. How did you adapt?",
            "Give me an example of when you had to lead a team through a challenging situation.",
            "Tell me about a time when you had to pivot your approach mid-project. What led to the change?",
            "Describe a situation where you had to collaborate with stakeholders who had conflicting priorities."
        ]
        
        self.technical_questions = [
            "Explain the difference between SQL and NoSQL databases. When would you use each?",
            "How would you design a system to handle 1 million concurrent users?",
            "What are the key principles of RESTful API design?",
            "Explain the concept of microservices and their trade-offs.",
            "How would you optimize a slow database query?",
            "What is the difference between authentication and authorization?",
            "Explain the CAP theorem and its implications for distributed systems.",
            "How would you implement caching in a web application?"
        ]
        
        self.system_design_questions = [
            "Design a URL shortener like bit.ly. What are the key components?",
            "How would you design a chat application like WhatsApp?",
            "Design a social media feed system. How would you handle real-time updates?",
            "How would you design a file storage system like Google Drive?",
            "Design a recommendation system for an e-commerce platform.",
            "How would you design a distributed cache system?",
            "Design a real-time analytics system for tracking user behavior.",
            "How would you design a load balancer for a web application?"
        ]
        
        self.leadership_questions = [
            "How do you motivate a team that's struggling with low morale?",
            "Describe your approach to giving constructive feedback to team members.",
            "How would you handle a situation where a team member consistently misses deadlines?",
            "What strategies do you use to build trust within your team?",
            "How do you balance being a leader and a team player?",
            "Describe a time when you had to make a difficult decision that affected your team.",
            "How do you ensure your team stays aligned with company goals?",
            "What's your approach to mentoring junior team members?"
        ]
        
        self.problem_solving_questions = [
            "How would you debug a production issue that's affecting multiple users?",
            "Describe your approach to breaking down a complex problem into manageable parts.",
            "How would you handle a situation where you don't know the answer to a technical question?",
            "What's your process for evaluating different solutions to a problem?",
            "How do you prioritize tasks when everything seems urgent?",
            "Describe a time when you had to think outside the box to solve a problem.",
            "How would you approach learning a completely new technology or framework?",
            "What's your strategy for handling ambiguous requirements?"
        ]

    async def generate_questions(
        self,
        company_name: str,
        position_title: str,
        job_description: str,
        question_count: int,
        interview_type: str,
        focus_areas: List[str],
        difficulty_level: str
    ) -> List[QuestionCreate]:
        """
        Generate interview questions based on the provided parameters.
        
        Args:
            company_name: Name of the company
            position_title: Job title/position
            job_description: Job description text
            question_count: Number of questions to generate
            interview_type: Type of interview (behavioral, technical, etc.)
            focus_areas: List of focus areas to emphasize
            difficulty_level: Easy, medium, or hard
            
        Returns:
            List of QuestionCreate objects
        """
        questions = []
        
        # Determine question distribution based on interview type
        if interview_type == "behavioral":
            question_pool = self.behavioral_questions
        elif interview_type == "technical":
            question_pool = self.technical_questions
        elif interview_type == "system_design":
            question_pool = self.system_design_questions
        elif interview_type == "mixed":
            # Mix of behavioral and technical
            question_pool = self.behavioral_questions + self.technical_questions
        else:
            # Default to mixed
            question_pool = self.behavioral_questions + self.technical_questions
        
        # Add focus area specific questions
        if "leadership" in focus_areas:
            question_pool.extend(self.leadership_questions)
        if "problem_solving" in focus_areas:
            question_pool.extend(self.problem_solving_questions)
        
        # Remove duplicates and shuffle
        question_pool = list(set(question_pool))
        random.shuffle(question_pool)
        
        # Select questions based on count
        selected_questions = question_pool[:question_count]
        
        # Generate QuestionCreate objects
        for i, question_text in enumerate(selected_questions):
            question = QuestionCreate(
                question_text=question_text,
                question_type=self._determine_question_type(question_text, interview_type),
                difficulty_level=difficulty_level,
                expected_duration=self._get_expected_duration(question_text, difficulty_level),
                order_index=i + 1
            )
            questions.append(question)
        
        return questions
    
    def _determine_question_type(self, question_text: str, interview_type: str) -> str:
        """Determine the question type based on content and interview type."""
        if interview_type == "behavioral":
            return "behavioral"
        elif interview_type == "technical":
            return "technical"
        elif interview_type == "system_design":
            return "system_design"
        else:
            # For mixed interviews, try to determine from content
            if any(keyword in question_text.lower() for keyword in ["time when", "describe a situation", "give me an example"]):
                return "behavioral"
            elif any(keyword in question_text.lower() for keyword in ["design", "system", "architecture"]):
                return "system_design"
            else:
                return "technical"
    
    def _get_expected_duration(self, question_text: str, difficulty_level: str) -> int:
        """Get expected duration in seconds based on question complexity."""
        base_duration = 90  # 90 seconds base
        
        # Adjust based on difficulty
        if difficulty_level == "easy":
            base_duration = 60
        elif difficulty_level == "hard":
            base_duration = 120
        
        # Adjust based on question complexity
        if len(question_text) > 100:  # Longer questions typically need more time
            base_duration += 30
        
        return base_duration
