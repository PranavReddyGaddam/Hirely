"""
Interview service for managing interview sessions and video uploads.
"""
import uuid
import os
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewList, InterviewStatus, QuestionCreate
from app.schemas.user import UserResponse
from app.services.supabase_service import SupabaseService
from app.services.groq_service import GroqService
from app.services.chroma_service import ChromaService
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class InterviewService:
    """Service for interview session management."""
    
    # Class-level storage to persist across instances
    _active_interviews = {}
    
    def __init__(self):
        """Initialize interview service."""
        self.supabase_service = SupabaseService()
        self.groq_service = GroqService()
        self.chroma_service = ChromaService()
        # Use class-level storage for active interviews
        self.active_interviews = InterviewService._active_interviews
    
    async def create_interview(
        self,
        interview_data: InterviewCreate,
        user_id: str,
        question_count: int = 5,
        focus_areas: List[str] = None,
        difficulty_level: str = "medium",
        access_token: str = None
    ) -> InterviewResponse:
        """
        Create a new interview session.
        
        Args:
            interview_data: Interview creation data
            user_id: User ID creating the interview
            
        Returns:
            InterviewResponse: Created interview data
        """
        try:
            # Generate interview ID
            interview_id = str(uuid.uuid4())
            
            # Prepare interview data for database
            interview_dict = {
                "id": interview_id,
                "title": interview_data.title,
                "description": interview_data.description,
                "interview_type": interview_data.interview_type.value,
                "job_description": interview_data.job_description,
                "company_name": interview_data.company_name,
                "position_title": interview_data.position_title,
                "duration_minutes": interview_data.duration_minutes,
                "status": InterviewStatus.DRAFT.value,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Create interview in database
            created_interview = await self.supabase_service.create_interview(interview_dict, access_token)
            
            if not created_interview:
                raise Exception("Failed to create interview in database")
            
            # Generate initial questions using Groq
            logger.info(f"Generating {question_count} questions using Groq for {interview_data.interview_type.value} interview")
            logger.info(f"Focus areas: {focus_areas}, Difficulty: {difficulty_level}")
            
            try:
                questions = await self.groq_service.generate_initial_questions(
                    interview_type=interview_data.interview_type,
                    job_description=interview_data.job_description,
                    position_title=interview_data.position_title,
                    company_name=interview_data.company_name,
                    num_questions=question_count,
                    focus_areas=focus_areas or [],
                    difficulty_level=difficulty_level
                )
                logger.info(f"Groq generated {len(questions) if questions else 0} questions")
                
                if questions:
                    for i, q in enumerate(questions):
                        logger.info(f"  Question {i+1}: {q.question_text[:50]}...")
                else:
                    logger.error("Groq returned no questions!")
                    
            except Exception as e:
                logger.error(f"Error generating questions with Groq: {e}")
                questions = []
            
            # Store questions in memory for the interview session
            if questions:
                logger.info(f"Storing {len(questions)} questions in memory for interview {interview_id}")
                self.active_interviews[interview_id] = {
                    "questions": questions,
                    "current_question_index": 0,
                    "user_id": user_id,
                    "interview_data": interview_data,
                    "created_at": datetime.utcnow().isoformat()
                }
                created_interview.questions = questions
                logger.info(f"Successfully stored questions in memory for interview {interview_id}")
                logger.info(f"Active interviews count: {len(self.active_interviews)}")
            else:
                logger.warning(f"No questions generated by Groq for interview {interview_id}")
                logger.warning(f"Interview {interview_id} will NOT be added to active sessions")
                created_interview.questions = []
            
            created_interview.responses = []
            
            logger.info(f"Interview created successfully: {interview_id}")
            return created_interview
            
        except Exception as e:
            logger.error(f"Error creating interview: {e}")
            raise Exception(f"Failed to create interview: {str(e)}")
    
    async def get_user_interviews(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> InterviewList:
        """
        Get all interviews for a user.
        
        Args:
            user_id: User ID to get interviews for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            InterviewList: List of user interviews
        """
        try:
            interviews = await self.supabase_service.get_user_interviews(user_id, skip, limit)
            
            return InterviewList(
                interviews=interviews,
                total=len(interviews),
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error getting user interviews: {e}")
            raise Exception(f"Failed to get user interviews: {str(e)}")
    
    async def get_interview(
        self,
        interview_id: str,
        user_id: str
    ) -> InterviewResponse:
        """
        Get specific interview by ID.
        
        Args:
            interview_id: Interview ID to fetch
            user_id: User ID for authorization
            
        Returns:
            InterviewResponse: Interview data
        """
        try:
            interview = await self.supabase_service.get_interview(interview_id, user_id)
            
            if not interview:
                raise Exception("Interview not found")
            
            return interview
            
        except Exception as e:
            logger.error(f"Error getting interview: {e}")
            raise Exception(f"Failed to get interview: {str(e)}")
    
    async def start_interview(
        self,
        interview_id: str,
        user_id: str
    ) -> InterviewResponse:
        """
        Start an interview session.
        
        Args:
            interview_id: Interview ID to start
            user_id: User ID for authorization
            
        Returns:
            InterviewResponse: Updated interview data
        """
        try:
            # Get interview
            interview = await self.get_interview(interview_id, user_id)
            
            if interview.status != InterviewStatus.DRAFT:
                raise Exception("Interview is not in draft status")
            
            # Update interview status
            update_data = {
                "status": InterviewStatus.ACTIVE.value,
                "started_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            updated_interview = await self.supabase_service.update_interview(
                interview_id, update_data
            )
            
            if not updated_interview:
                raise Exception("Failed to start interview")
            
            logger.info(f"Interview started: {interview_id}")
            return updated_interview
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            raise Exception(f"Failed to start interview: {str(e)}")
    
    async def complete_interview(
        self,
        interview_id: str,
        user_id: str
    ) -> InterviewResponse:
        """
        Complete an interview session.
        
        Args:
            interview_id: Interview ID to complete
            user_id: User ID for authorization
            
        Returns:
            InterviewResponse: Updated interview data
        """
        try:
            # Get interview
            interview = await self.get_interview(interview_id, user_id)
            
            if interview.status != InterviewStatus.ACTIVE:
                raise Exception("Interview is not active")
            
            # Update interview status
            update_data = {
                "status": InterviewStatus.COMPLETED.value,
                "completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            updated_interview = await self.supabase_service.update_interview(
                interview_id, update_data
            )
            
            if not updated_interview:
                raise Exception("Failed to complete interview")
            
            logger.info(f"Interview completed: {interview_id}")
            return updated_interview
            
        except Exception as e:
            logger.error(f"Error completing interview: {e}")
            raise Exception(f"Failed to complete interview: {str(e)}")
    
    async def upload_video(
        self,
        interview_id: str,
        file: UploadFile,
        user_id: str
    ) -> dict:
        """
        Upload interview video for analysis.
        
        Args:
            interview_id: Interview ID
            file: Video file to upload
            user_id: User ID for authorization
            
        Returns:
            dict: Upload result
        """
        try:
            # Verify interview exists and user has access
            interview = await self.get_interview(interview_id, user_id)
            
            # Check file size
            if file.size > settings.MAX_FILE_SIZE:
                raise Exception(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes")
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(settings.UPLOAD_DIRECTORY, user_id, interview_id)
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Update interview with video path
            update_data = {
                "video_path": file_path,
                "video_filename": filename,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.supabase_service.update_interview(interview_id, update_data)
            
            logger.info(f"Video uploaded successfully: {file_path}")
            return {
                "message": "Video uploaded successfully",
                "file_path": file_path,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            raise Exception(f"Failed to upload video: {str(e)}")
    
    async def delete_interview(
        self,
        interview_id: str,
        user_id: str
    ) -> bool:
        """
        Delete an interview.
        
        Args:
            interview_id: Interview ID to delete
            user_id: User ID for authorization
            
        Returns:
            bool: True if successful
        """
        try:
            # Verify interview exists and user has access
            interview = await self.get_interview(interview_id, user_id)
            
            # Delete interview from database
            success = await self.supabase_service.delete_interview(interview_id, user_id)
            
            if not success:
                raise Exception("Failed to delete interview from database")
            
            # TODO: Clean up associated files (video, analysis results, etc.)
            
            logger.info(f"Interview deleted successfully: {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting interview: {e}")
            raise Exception(f"Failed to delete interview: {str(e)}")
    
    async def generate_follow_up_question(
        self,
        interview_id: str,
        current_question: str,
        user_response: str,
        user_id: str
    ) -> Optional[dict]:
        """
        Generate a follow-up question based on user's response.
        
        Args:
            interview_id: Interview ID
            current_question: Current question
            user_response: User's response
            user_id: User ID
            
        Returns:
            dict: Follow-up question or None
        """
        try:
            # Get interview context
            interview = await self.get_interview(interview_id, user_id)
            
            # Prepare context for Groq
            context = {
                "interview_type": interview.interview_type,
                "job_description": interview.job_description,
                "position_title": interview.position_title,
                "company_name": interview.company_name
            }
            
            # Generate follow-up question
            follow_up = await self.groq_service.generate_follow_up_question(
                current_question, user_response, context
            )
            
            if follow_up:
                # Store user response in Chroma for future reference
                await self.chroma_service.store_user_response(
                    user_id=user_id,
                    question=current_question,
                    response=user_response,
                    metadata={
                        "interview_id": interview_id,
                        "question_type": "interview_question",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                logger.info(f"Generated follow-up question for interview: {interview_id}")
                return follow_up.dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            return None
    
    async def add_questions_to_interview(
        self,
        interview_id: str,
        questions: List[QuestionCreate]
    ) -> bool:
        """
        Add questions to an interview.
        
        Args:
            interview_id: Interview ID
            questions: List of questions to add
            
        Returns:
            bool: True if successful
        """
        try:
            successful_questions = 0
            
            # Store questions in database
            for i, question in enumerate(questions):
                question_dict = {
                    "id": str(uuid.uuid4()),
                    "interview_id": interview_id,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "difficulty_level": question.difficulty_level,
                    "expected_duration": question.expected_duration,
                    "order_index": i + 1,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                success = await self.supabase_service.create_question(question_dict)
                if success:
                    successful_questions += 1
                else:
                    logger.error(f"Failed to create question {i+1}: {question.question_text[:50]}...")
            
            if successful_questions == len(questions):
                logger.info(f"Successfully added all {len(questions)} questions to interview: {interview_id}")
                return True
            else:
                logger.error(f"Only {successful_questions}/{len(questions)} questions were created successfully")
                return False
            
        except Exception as e:
            logger.error(f"Error adding questions to interview: {e}")
            raise Exception(f"Failed to add questions: {str(e)}")
    
    async def add_responses_to_interview(
        self,
        interview_id: str,
        responses: List[dict]
    ) -> bool:
        """
        Add responses to an interview.
        
        Args:
            interview_id: Interview ID
            responses: List of response data to add
            
        Returns:
            bool: True if successful
        """
        try:
            successful_responses = 0
            
            # Store responses in database
            for i, response in enumerate(responses):
                response_dict = {
                    "id": response.get("id", str(uuid.uuid4())),
                    "interview_id": interview_id,
                    "question_id": response.get("question_id"),
                    "response_text": response.get("response_text"),
                    "audio_duration": response.get("audio_duration"),
                    "confidence_score": response.get("confidence_score"),
                    "created_at": response.get("created_at", datetime.utcnow().isoformat())
                }
                
                success = await self.supabase_service.create_response(response_dict)
                if success:
                    successful_responses += 1
                else:
                    logger.error(f"Failed to create response {i+1}: {response.get('response_text', '')[:50]}...")
            
            if successful_responses == len(responses):
                logger.info(f"Successfully added all {len(responses)} responses to interview: {interview_id}")
                return True
            else:
                logger.error(f"Only {successful_responses}/{len(responses)} responses were created successfully")
                return False
            
        except Exception as e:
            logger.error(f"Error adding responses to interview: {e}")
            raise Exception(f"Failed to add responses: {str(e)}")
    
    async def get_next_question(
        self,
        interview_id: str,
        user_id: str
    ) -> dict:
        """
        Get the next question for an interview.
        
        Args:
            interview_id: Interview ID
            user_id: User ID for authorization
            
        Returns:
            dict: Next question data
        """
        try:
            # Check if interview exists in memory
            if interview_id not in self.active_interviews:
                raise Exception("Interview not found in active sessions")
            
            interview_session = self.active_interviews[interview_id]
            
            # Verify user authorization
            if interview_session["user_id"] != user_id:
                raise Exception("Unauthorized access to interview")
            
            questions = interview_session["questions"]
            current_index = interview_session["current_question_index"]
            
            if not questions:
                raise Exception("No questions available for this interview")
            
            if current_index >= len(questions):
                raise Exception("No more questions available")
            
            # Get the current question
            current_question = questions[current_index]
            
            return {
                "id": f"temp_{interview_id}_{current_index}",  # Use interview_id + index as temporary ID
                "question_text": current_question.question_text,
                "question_type": current_question.question_type,
                "difficulty_level": current_question.difficulty_level,
                "expected_duration": current_question.expected_duration,
                "order_index": current_index + 1
            }
            
        except Exception as e:
            logger.error(f"Error getting next question: {e}")
            raise Exception(f"Failed to get next question: {str(e)}")
    
    async def complete_interview(
        self,
        interview_id: str,
        user_id: str
    ) -> dict:
        """
        Complete an interview and store questions and responses in database for analytics.
        
        Args:
            interview_id: Interview ID
            user_id: User ID for authorization
            
        Returns:
            dict: Completion status
        """
        try:
            # Check if interview exists in memory
            if interview_id not in self.active_interviews:
                raise Exception("Interview not found in active sessions")
            
            interview_session = self.active_interviews[interview_id]
            
            # Verify user authorization
            if interview_session["user_id"] != user_id:
                raise Exception("Unauthorized access to interview")
            
            # Store questions in database for analytics
            questions = interview_session["questions"]
            if questions:
                logger.info(f"Storing {len(questions)} questions in database for analytics")
                await self.add_questions_to_interview(interview_id, questions)
            
            # Store responses in database
            responses = interview_session.get("responses", [])
            if responses:
                logger.info(f"Storing {len(responses)} responses in database for analytics")
                try:
                    await self.add_responses_to_interview(interview_id, responses)
                except Exception as e:
                    logger.error(f"Failed to store responses for interview {interview_id}: {e}")
                    # Don't fail the entire completion if response storage fails
                    # The interview can still be marked as completed
            else:
                logger.warning(f"No responses found for interview {interview_id}")
            
            # Remove from active interviews
            del self.active_interviews[interview_id]
            
            logger.info(f"Interview {interview_id} completed and questions/responses stored for analytics")
            return {"status": "completed", "message": "Interview completed successfully"}
            
        except Exception as e:
            logger.error(f"Error completing interview: {e}")
            raise Exception(f"Failed to complete interview: {str(e)}")
    
    async def submit_answer(
        self,
        interview_id: str,
        answer_data: dict,
        user_id: str
    ) -> dict:
        """
        Submit an answer for a question.
        
        Args:
            interview_id: Interview ID
            answer_data: Answer data including question_id, response_text, etc.
            user_id: User ID for authorization
            
        Returns:
            dict: Submission result
        """
        try:
            # Check if interview exists in memory
            if interview_id not in self.active_interviews:
                raise Exception("Interview not found in active sessions")
            
            interview_session = self.active_interviews[interview_id]
            
            # Verify user authorization
            if interview_session["user_id"] != user_id:
                raise Exception("Unauthorized access to interview")
            
            # Store response in memory (will be saved to database after interview completion)
            if "responses" not in interview_session:
                interview_session["responses"] = []
            
            response_data = {
                "id": str(uuid.uuid4()),
                "question_id": answer_data.get("question_id"),
                "response_text": answer_data.get("response_text"),
                "audio_duration": answer_data.get("audio_duration"),
                "confidence_score": answer_data.get("confidence_score"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            interview_session["responses"].append(response_data)
            
            # Move to next question
            interview_session["current_question_index"] += 1
            
            logger.info(f"Answer submitted for interview: {interview_id}, response count: {len(interview_session['responses'])}")
            return {
                "message": "Answer submitted successfully",
                "response_id": response_data["id"]
            }
            
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            raise Exception(f"Failed to submit answer: {str(e)}")
