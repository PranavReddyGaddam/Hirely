"""
Groq LLM service for question generation and answer analysis.
"""
from typing import List, Dict, Any, Optional
import groq
from app.core.config import settings
from app.schemas.interview import QuestionCreate, InterviewType
from app.schemas.analysis import FeedbackItem, FeedbackCategory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GroqService:
    """Service for Groq LLM operations."""
    
    def __init__(self):
        """Initialize Groq client."""
        try:
            if settings.GROQ_API_KEY:
                self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
                logger.info("✅ Groq client initialized successfully")
                logger.info(f"📝 Groq API key present: {settings.GROQ_API_KEY[:10]}...")
            else:
                logger.error("❌ Groq API key not configured in environment variables")
                logger.error("💡 Please set GROQ_API_KEY in your .env file")
                self.client = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq client: {e}", exc_info=True)
            self.client = None
    
    def test_connection(self) -> dict:
        """Test Groq API connection and return status."""
        if not self.client:
            return {
                "success": False,
                "error": "Groq client not initialized. Check API key."
            }
        
        try:
            # Make a minimal test call
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": "Say 'test' if you can read this."}
                ],
                max_tokens=10,
                temperature=0.5
            )
            
            if response.choices and len(response.choices) > 0:
                logger.info("✅ Groq API connection test successful")
                return {
                    "success": True,
                    "message": "Groq API is working",
                    "model": "llama-3.3-70b-versatile"
                }
            else:
                logger.error("❌ Groq API returned empty response")
                return {
                    "success": False,
                    "error": "Empty response from Groq API"
                }
                
        except Exception as e:
            logger.error(f"❌ Groq API connection test failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_initial_questions(
        self, 
        interview_type: InterviewType,
        job_description: Optional[str] = None,
        position_title: Optional[str] = None,
        company_name: Optional[str] = None,
        num_questions: int = 5,
        focus_areas: List[str] = None,
        difficulty_level: str = "medium"
    ) -> List[QuestionCreate]:
        """
        Generate initial set of interview questions.
        
        Args:
            interview_type: Type of interview
            job_description: Job description text
            position_title: Position title
            company_name: Company name
            num_questions: Number of questions to generate
            
        Returns:
            List[QuestionCreate]: Generated questions
        """
        if not self.client:
            logger.error("Groq client not initialized")
            return []
        
        try:
            # Build context for question generation
            context = f"Generate {num_questions} interview questions for a {interview_type.value} interview"
            
            if position_title:
                context += f" for the position of {position_title}"
            if company_name:
                context += f" at {company_name}"
            if job_description:
                context += f". Job description: {job_description[:500]}"
            
            # Add difficulty and focus areas if provided
            if focus_areas:
                context += f". Focus areas: {', '.join(focus_areas)}"
            else:
                context += f". Focus on: general interview skills"
            
            context += f". Difficulty level: {difficulty_level}"
            
            prompt = f"""
            {context}
            
            Generate exactly {num_questions} interview questions. For each question, provide:
            1. The question text
            2. Question type (behavioral, technical, or situational)
            3. Difficulty level (easy, medium, or hard)
            4. Expected duration in seconds
            
            Format each question as:
            Q1: [Question text here?]
            Type: [behavioral/technical/situational]
            Difficulty: [easy/medium/hard]
            Duration: [seconds]
            
            Example:
            Q1: Tell me about a time when you had to work with a difficult team member?
            Type: behavioral
            Difficulty: medium
            Duration: 120
            
            Q2: How would you design a scalable web application?
            Type: technical
            Difficulty: hard
            Duration: 180
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response and create questions
            questions = self._parse_questions_from_response(response.choices[0].message.content)
            
            logger.info(f"Generated {len(questions)} initial questions for {interview_type.value} interview")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating initial questions: {e}")
            return []
    
    async def generate_follow_up_question(
        self,
        previous_question: str,
        user_response: str,
        interview_context: Dict[str, Any]
    ) -> Optional[QuestionCreate]:
        """
        Generate a follow-up question based on user's response.
        
        Args:
            previous_question: The previous question asked
            user_response: User's response to the previous question
            interview_context: Context about the interview
            
        Returns:
            QuestionCreate: Follow-up question or None if interview should end
        """
        if not self.client:
            logger.error("Groq client not initialized")
            return None
        
        try:
            # TODO: GROQ - Implement dynamic follow-up question generation
            prompt = f"""
            Based on the user's response to the interview question, generate an appropriate follow-up question.
            
            Previous Question: {previous_question}
            User Response: {user_response}
            Interview Context: {interview_context}
            
            Generate a follow-up question that:
            1. Builds on the user's response
            2. Dives deeper into the topic
            3. Tests additional competencies
            4. Maintains interview flow
            
            If the user's response is comprehensive and the interview should move to a new topic, 
            generate a new question on a different but related topic.
            
            Return the question in the same format as before.
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response and create follow-up question
            questions = self._parse_questions_from_response(response.choices[0].message.content)
            
            if questions:
                logger.info("Generated follow-up question based on user response")
                return questions[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            return None
    
    async def analyze_response(
        self,
        question: str,
        response: str,
        context: Dict[str, Any]
    ) -> List[FeedbackItem]:
        """
        Analyze user's response and generate feedback.
        
        Args:
            question: The interview question
            response: User's response
            context: Additional context for analysis
            
        Returns:
            List[FeedbackItem]: Feedback items for the response
        """
        if not self.client:
            logger.error("Groq client not initialized")
            return []
        
        try:
            # TODO: GROQ - Implement response analysis
            prompt = f"""
            Analyze the user's interview response and provide detailed feedback.
            
            Question: {question}
            Response: {response}
            Context: {context}
            
            Provide feedback in the following categories:
            1. Communication (clarity, structure, articulation)
            2. Technical Skills (accuracy, depth, relevance)
            3. Problem Solving (approach, logic, creativity)
            4. Confidence (assurance, hesitation, conviction)
            5. Clarity (organization, coherence, completeness)
            6. Structure (logical flow, examples, conclusion)
            
            For each category, provide:
            - Score (0.0 to 1.0)
            - Feedback text
            - Specific suggestions for improvement
            - Strengths identified
            - Areas for improvement
            
            Be constructive and specific in your feedback.
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse response and create feedback items
            feedback_items = self._parse_feedback_from_response(response.choices[0].message.content)
            
            logger.info(f"Generated {len(feedback_items)} feedback items for response analysis")
            return feedback_items
            
        except Exception as e:
            logger.error(f"Error analyzing response: {e}")
            return []
    
    async def generate_interview_summary(
        self,
        questions: List[str],
        responses: List[str],
        feedback_items: List[FeedbackItem]
    ) -> Dict[str, Any]:
        """
        Generate overall interview summary and recommendations.
        
        Args:
            questions: List of interview questions
            responses: List of user responses
            feedback_items: List of feedback items
            
        Returns:
            Dict[str, Any]: Interview summary and recommendations
        """
        if not self.client:
            logger.error("Groq client not initialized")
            return {}
        
        try:
            # TODO: GROQ - Implement interview summary generation
            prompt = f"""
            Generate a comprehensive summary of the interview performance.
            
            Questions: {questions}
            Responses: {responses}
            Feedback: {[item.dict() for item in feedback_items]}
            
            Provide:
            1. Overall performance score (0.0 to 1.0)
            2. Key strengths demonstrated
            3. Main areas for improvement
            4. Specific recommendations for future interviews
            5. Next steps for skill development
            
            Be encouraging but honest in your assessment.
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response and create summary
            summary = self._parse_summary_from_response(response.choices[0].message.content)
            
            logger.info("Generated interview summary and recommendations")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating interview summary: {e}")
            return {}
    
    def _parse_questions_from_response(self, response_text: str) -> List[QuestionCreate]:
        """Parse questions from Groq response text."""
        questions = []
        
        # Split response into lines and look for questions
        lines = response_text.split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for question patterns (Q1:, Q2:, etc.)
            if line.startswith(('Q1:', 'Q2:', 'Q3:', 'Q4:', 'Q5:', 'Q6:', 'Q7:', 'Q8:', 'Q9:', 'Q10:')):
                # Save previous question if exists
                if current_question:
                    questions.append(current_question)
                
                # Start new question
                question_text = line.split(':', 1)[1].strip()  # Remove Q1: prefix
                current_question = QuestionCreate(
                    question_text=question_text,
                    question_type="behavioral",  # Default type
                    difficulty_level="medium",  # Default difficulty
                    expected_duration=120  # Default duration
                )
            elif current_question and line.startswith(('Type:', 'Difficulty:', 'Duration:')):
                # Parse metadata
                if line.startswith('Type:'):
                    current_question.question_type = line.split(':', 1)[1].strip().lower()
                elif line.startswith('Difficulty:'):
                    current_question.difficulty_level = line.split(':', 1)[1].strip().lower()
                elif line.startswith('Duration:'):
                    try:
                        duration = int(line.split(':', 1)[1].strip().replace('seconds', '').strip())
                        current_question.expected_duration = duration
                    except:
                        pass
        
        # Add the last question
        if current_question:
            questions.append(current_question)
        
        # If no structured questions found, try alternative parsing
        if not questions:
            # Look for questions that end with ?
            import re
            question_pattern = r'([^.!?]*\?)'
            matches = re.findall(question_pattern, response_text)
            
            for match in matches:
                question_text = match.strip()
                if len(question_text) > 10:  # Filter out very short matches
                    questions.append(QuestionCreate(
                        question_text=question_text,
                        question_type="behavioral",
                        difficulty_level="medium",
                        expected_duration=120
                    ))
                    if len(questions) >= 5:  # Limit to 5 questions
                        break
        
        # Fallback: create at least 3 questions if none found
        if not questions:
            questions = [
                QuestionCreate(
                    question_text="Tell me about yourself and your background.",
                    question_type="behavioral",
                    difficulty_level="easy",
                    expected_duration=120
                ),
                QuestionCreate(
                    question_text="Describe a challenging project you worked on and how you overcame the difficulties.",
                    question_type="behavioral",
                    difficulty_level="medium",
                    expected_duration=120
                ),
                QuestionCreate(
                    question_text="How do you handle working under pressure and tight deadlines?",
                    question_type="behavioral",
                    difficulty_level="medium",
                    expected_duration=120
                )
            ]
        
        logger.info(f"Parsed {len(questions)} questions from Groq response")
        return questions
    
    def _parse_feedback_from_response(self, response_text: str) -> List[FeedbackItem]:
        """Parse feedback items from Groq response text."""
        # TODO: Implement proper parsing of structured response
        # For now, return placeholder feedback
        feedback_items = []
        for category in FeedbackCategory:
            feedback_items.append(FeedbackItem(
                category=category,
                score=0.7,
                feedback_text=f"Good performance in {category.value}",
                suggestions=[f"Improve {category.value}"],
                strengths=[f"Strong {category.value}"],
                areas_for_improvement=[f"Work on {category.value}"]
            ))
        return feedback_items
    
    def _parse_summary_from_response(self, response_text: str) -> Dict[str, Any]:
        """Parse summary from Groq response text."""
        # TODO: Implement proper parsing of structured response
        # For now, return placeholder summary
        return {
            "overall_score": 0.75,
            "strengths": ["Good communication", "Technical knowledge"],
            "areas_for_improvement": ["More examples", "Better structure"],
            "recommendations": ["Practice more", "Study industry trends"],
            "next_steps": ["Take more interviews", "Focus on weak areas"]
        }
