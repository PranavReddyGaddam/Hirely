"""
Interview Analysis Orchestrator
Coordinates CV analysis, transcript analysis, and generates comprehensive interview reports
"""
import asyncio
import json
import cv2
import time
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import requests
import os

from app.services.supabase_service import SupabaseService
from app.services.s3_service import S3Service
from app.services.elevenlabs_service import ElevenLabsService
from app.services.transcript_analyzer import TranscriptAnalyzer
from app.cv.services.cv_processor import CVProcessor
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class InterviewAnalysisOrchestrator:
    """Orchestrates complete interview analysis including CV, audio, and AI insights"""
    
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.s3_service = S3Service()
        self.elevenlabs_service = ElevenLabsService()
        self.transcript_analyzer = TranscriptAnalyzer()
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY") or settings.OPENROUTER_API_KEY if hasattr(settings, 'OPENROUTER_API_KEY') else None
    
    async def analyze_interview(
        self,
        interview_id: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform complete interview analysis.
        
        Args:
            interview_id: Interview ID
            user_id: User ID
            conversation_id: ElevenLabs conversation ID (if available)
            
        Returns:
            Complete analysis results
        """
        logger.info(f"[Analysis Orchestrator] Starting analysis for interview {interview_id}")
        
        analysis_start_time = time.time()
        results = {
            "interview_id": interview_id,
            "analysis_status": "in_progress",
            "cv_analysis": None,
            "transcript_analysis": None,
            "ai_insights": None,
            "error": None
        }
        
        try:
            # Step 1: Get interview data from database
            interview = await self.supabase_service.get_interview(interview_id, user_id)
            if not interview:
                raise Exception(f"Interview {interview_id} not found")
            
            logger.info(f"[Analysis Orchestrator] Interview found: {interview.interview_type}")
            
            # Step 2: WAIT for video to be uploaded to S3 and stored in database
            if not interview.video_storage_path:
                logger.warning(f"[Analysis Orchestrator] ⏳ No video_storage_path yet, waiting for upload...")
                # Retry logic: wait up to 30 seconds for video to appear
                max_retries = 30
                retry_count = 0
                while not interview.video_storage_path and retry_count < max_retries:
                    await asyncio.sleep(1)
                    interview = await self.supabase_service.get_interview(interview_id, user_id)
                    if interview.video_storage_path:
                        logger.info(f"[Analysis Orchestrator] ✅ Video found after {retry_count + 1}s: {interview.video_storage_path}")
                        break
                    retry_count += 1
                
                if not interview.video_storage_path:
                    logger.error(f"[Analysis Orchestrator] ❌ Video still not found after 30s, skipping CV analysis")
                    # Continue without CV analysis
            
            # Step 3: Get video from S3 and run CV analysis
            cv_analysis = None
            if interview.video_storage_path:
                logger.info(f"[Analysis Orchestrator] Running CV analysis on video: {interview.video_storage_path}")
                try:
                    cv_analysis = await self._run_cv_analysis(interview.video_storage_path)
                    if cv_analysis:
                        logger.info(f"[Analysis Orchestrator] ✅ CV analysis completed successfully")
                        results['cv_analysis'] = cv_analysis
                    else:
                        logger.warning(f"[Analysis Orchestrator] CV analysis returned None")
                except Exception as e:
                    logger.error(f"[Analysis Orchestrator] CV analysis failed: {e}", exc_info=True)
            else:
                logger.warning(f"[Analysis Orchestrator] No video found for interview {interview_id}")
            
            # Step 3: Get transcript from ElevenLabs and analyze
            transcript_analysis = None
            if conversation_id:
                logger.info(f"[Analysis Orchestrator] Getting transcript from ElevenLabs: {conversation_id}")
                transcript_data = await self.elevenlabs_service.get_conversation_transcript(conversation_id)
                
                if transcript_data and transcript_data.get('full_transcript'):
                    logger.info(f"[Analysis Orchestrator] Analyzing transcript ({len(transcript_data['full_transcript'])} chars)")
                    
                    # Get interview duration from video or estimate
                    duration = transcript_data.get('duration', 0)
                    if cv_analysis and 'session_info' in cv_analysis:
                        duration = cv_analysis['session_info'].get('duration_seconds', duration)
                    
                    transcript_analysis = self.transcript_analyzer.analyze_transcript(
                        transcript_data['full_transcript'],
                        duration
                    )
                    
                    # Add raw transcript data
                    transcript_analysis['conversation_id'] = conversation_id
                    transcript_analysis['messages'] = transcript_data.get('messages', [])
                    
                    results['transcript_analysis'] = transcript_analysis
                else:
                    logger.warning(f"[Analysis Orchestrator] No transcript available from ElevenLabs")
            else:
                logger.warning(f"[Analysis Orchestrator] No conversation_id provided")
            
            # Step 4: Generate AI insights using Groq
            logger.info(f"[Analysis Orchestrator] Generating AI insights with Groq")
            ai_insights = await self._generate_ai_insights(
                cv_analysis,
                transcript_analysis,
                interview.interview_type
            )
            results['ai_insights'] = ai_insights
            
            # Step 5: Calculate overall score
            overall_score = self._calculate_overall_score(cv_analysis, transcript_analysis)
            results['overall_score'] = overall_score
            
            # Mark as completed
            results['analysis_status'] = 'completed'
            analysis_duration = time.time() - analysis_start_time
            results['analysis_duration_seconds'] = round(analysis_duration, 2)
            
            logger.info(f"[Analysis Orchestrator] ✅ Analysis complete in {analysis_duration:.2f}s")
            
            # Step 6: Save results to database/storage
            await self._save_analysis_results(interview_id, results)
            
            return results
            
        except Exception as e:
            logger.error(f"[Analysis Orchestrator] Error during analysis: {e}", exc_info=True)
            results['analysis_status'] = 'failed'
            results['error'] = str(e)
            return results
    
    async def _run_cv_analysis(self, video_storage_path: str) -> Optional[Dict[str, Any]]:
        """Run CV analysis on video from S3"""
        try:
            # Download video from S3
            logger.info(f"[CV Analysis] Starting download from S3: {video_storage_path}")
            video_data = await self.s3_service.download_video(video_storage_path)
            
            if not video_data:
                logger.error("[CV Analysis] ❌ Failed to download video from S3")
                return None
            
            logger.info(f"[CV Analysis] ✅ Video downloaded successfully: {len(video_data) / 1024 / 1024:.2f} MB")
            
            # Save to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(video_data)
                temp_video_path = temp_file.name
            
            logger.info(f"[CV Analysis] Video saved to temp: {temp_video_path}")
            
            try:
                # Process video with CV (run in executor to prevent blocking)
                # This now returns the actual analysis data (not file paths)
                analysis_data = await asyncio.to_thread(self._process_video_sync, temp_video_path)
                
                if analysis_data:
                    logger.info(f"[CV Analysis] ✅ Analysis completed successfully")
                    return analysis_data
                else:
                    logger.error(f"[CV Analysis] ❌ No analysis data returned")
                    return None
                
            finally:
                # Cleanup temp file
                import os
                try:
                    os.remove(temp_video_path)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"[CV Analysis] Error: {e}", exc_info=True)
            return None
    
    def _process_video_sync(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Synchronous video processing (runs in thread pool)"""
        try:
            # Process video with CV
            processor = CVProcessor()
            processor.start_session()
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception("Could not open video file")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            frame_count = 0
            processed_frames = 0
            target_fps = 5
            frame_skip_interval = int(fps / target_fps) if fps > target_fps else 1
            
            logger.info(f"[CV Analysis] Processing video: {total_frames} frames at {fps} FPS")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_skip_interval == 0:
                    success, encoded_image = cv2.imencode('.jpg', frame)
                    if success:
                        processor.process_frame(encoded_image.tobytes())
                        processed_frames += 1
                
                frame_count += 1
            
            cap.release()
            
            logger.info(f"[CV Analysis] Processed {processed_frames} frames")
            
            # Create temp directory for CV analysis exports
            with tempfile.TemporaryDirectory() as temp_dir:
                export_path = Path(temp_dir) / "cv_analysis"
                export_path.mkdir(exist_ok=True)
                
                # Get analysis results (returns file paths)
                cv_results = processor.stop_session(export_path=str(export_path))
                
                # Read the analysis file BEFORE temp directory is deleted
                if cv_results and 'export_files' in cv_results:
                    export_files = cv_results['export_files']
                    if 'interview_analysis' in export_files:
                        analysis_file = export_files['interview_analysis']
                        try:
                            with open(analysis_file, 'r') as f:
                                analysis_data = json.load(f)
                            
                            # Verify CV score exists
                            if 'overall_interview_score' in analysis_data:
                                overall_score = analysis_data['overall_interview_score'].get('overall_score', 0)
                                logger.info(f"[CV Analysis] ✅ CV score calculated: {overall_score}/100")
                                return analysis_data
                            else:
                                logger.error("[CV Analysis] ❌ No overall_interview_score in analysis data")
                                return None
                        except Exception as e:
                            logger.error(f"[CV Analysis] ❌ Error reading analysis file: {e}")
                            return None
                    else:
                        logger.error("[CV Analysis] ❌ No interview_analysis in export_files")
                        return None
                else:
                    logger.error("[CV Analysis] ❌ stop_session did not return export_files")
                    return None
            
        except Exception as e:
            logger.error(f"[CV Analysis] Error in sync processing: {e}", exc_info=True)
            return None
    
    async def _generate_ai_insights(
        self,
        cv_analysis: Optional[Dict],
        transcript_analysis: Optional[Dict],
        interview_type: str
    ) -> Dict[str, Any]:
        """Generate AI insights using OpenRouter (Claude Sonnet 4.5)"""
        
        if not self.openrouter_api_key:
            logger.error("[AI Insights] OpenRouter API key not configured")
            return {
                "feedback": "AI insights generation failed. OpenRouter API key not configured.",
                "error": "Missing API key"
            }
        
        try:
            # Build comprehensive prompt
            prompt = self._build_analysis_prompt(cv_analysis, transcript_analysis, interview_type)
            
            system_prompt = """You are an expert interview coach providing comprehensive feedback.
            
Your task is to analyze the candidate's performance across multiple dimensions:
- Visual behavior (from CV analysis)
- Communication skills (from transcript analysis)
- Overall interview performance

Provide:
1. Executive Summary (2-3 sentences)
2. Top 3 Strengths (specific and actionable)
3. Top 3 Areas for Improvement (specific and actionable)
4. Detailed Recommendations (5-7 items)
5. Next Steps (3-4 action items)

Be encouraging but honest. Focus on actionable feedback."""
            
            # Call OpenRouter API
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Hirely Interview Analysis",
                },
                json={
                    "model": "anthropic/claude-sonnet-4.5",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"[AI Insights] OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter API returned status {response.status_code}")
            
            data = response.json()
            feedback_text = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            
            return {
                "feedback": feedback_text,
                "model": "anthropic/claude-sonnet-4.5",
                "tokens_used": {
                    "prompt": usage.get('prompt_tokens', 0),
                    "completion": usage.get('completion_tokens', 0),
                    "total": usage.get('total_tokens', 0)
                }
            }
            
        except requests.exceptions.Timeout:
            logger.error("[AI Insights] OpenRouter API request timed out")
            return {
                "feedback": "AI insights generation timed out. Please try again later.",
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"[AI Insights] Error generating insights: {e}", exc_info=True)
            return {
                "feedback": "AI insights generation failed. Please review the metrics manually.",
                "error": str(e)
            }
    
    def _build_analysis_prompt(
        self,
        cv_analysis: Optional[Dict],
        transcript_analysis: Optional[Dict],
        interview_type: str
    ) -> str:
        """Build comprehensive analysis prompt for LLM"""
        
        prompt = f"# Interview Analysis Report\n\n"
        prompt += f"**Interview Type:** {interview_type}\n\n"
        
        # CV Analysis section
        if cv_analysis:
            prompt += "## Visual Behavior Analysis\n\n"
            
            if 'emotions' in cv_analysis:
                emotions = cv_analysis['emotions']
                prompt += f"**Emotional State:**\n"
                prompt += f"- Dominant emotion: {emotions.get('dominant_emotion', 'unknown')}\n"
                prompt += f"- Emotional stability: {emotions.get('emotional_stability', {}).get('score', 'unknown')}\n"
                prompt += f"- Smile analysis: {emotions.get('smile_analysis', {}).get('recommendation', 'unknown')}\n\n"
            
            if 'eye_contact' in cv_analysis:
                eye = cv_analysis['eye_contact']
                prompt += f"**Eye Contact:**\n"
                prompt += f"- Looking at camera: {eye.get('looking_at_camera_percentage', 0):.1f}%\n"
                prompt += f"- Eye openness: {eye.get('avg_eye_openness', 0):.1f}%\n\n"
            
            if 'posture' in cv_analysis:
                posture = cv_analysis['posture']
                prompt += f"**Posture:**\n"
                prompt += f"- Good posture: {posture.get('good_posture_percentage', 0):.1f}%\n\n"
            
            if 'overall_interview_score' in cv_analysis:
                scores = cv_analysis['overall_interview_score']
                prompt += f"**Overall CV Score:** {scores.get('overall_score', 0):.0f}/100\n\n"
        
        # Transcript Analysis section
        if transcript_analysis:
            prompt += "## Communication Analysis\n\n"
            
            filler = transcript_analysis.get('filler_word_analysis', {})
            prompt += f"**Filler Words:**\n"
            prompt += f"- Total filler words: {filler.get('total_filler_words', 0)}\n"
            prompt += f"- Filler percentage: {filler.get('filler_percentage', 0):.1f}%\n"
            prompt += f"- Most used: '{filler.get('most_used_filler', 'none')}' ({filler.get('most_used_count', 0)} times)\n"
            prompt += f"- Rating: {filler.get('rating', 'unknown')}\n\n"
            
            pace = transcript_analysis.get('speaking_pace', {})
            prompt += f"**Speaking Pace:**\n"
            prompt += f"- Words per minute: {pace.get('words_per_minute', 0):.1f}\n"
            prompt += f"- Rating: {pace.get('pace_rating', 'unknown')}\n\n"
            
            diversity = transcript_analysis.get('word_diversity', {})
            prompt += f"**Vocabulary:**\n"
            prompt += f"- Unique words: {diversity.get('unique_words', 0)}/{diversity.get('total_words', 0)}\n"
            prompt += f"- Diversity ratio: {diversity.get('diversity_ratio', 0):.2f}\n\n"
            
            comm_score = transcript_analysis.get('communication_score', {})
            prompt += f"**Communication Score:** {comm_score.get('score', 0):.1f}/100 ({comm_score.get('grade', 'N/A')})\n\n"
        
        prompt += "\n\nBased on this data, provide comprehensive feedback for the candidate."
        
        return prompt
    
    def _calculate_overall_score(
        self,
        cv_analysis: Optional[Dict],
        transcript_analysis: Optional[Dict]
    ) -> Dict[str, Any]:
        """Calculate weighted overall interview score"""
        
        cv_score = 0
        comm_score = 0
        
        # Get CV score (if available)
        if cv_analysis and 'overall_interview_score' in cv_analysis:
            cv_score = cv_analysis['overall_interview_score'].get('overall_score', 0)
            
            # Validate CV score - log warning if analysis likely failed
            if cv_score == 0:
                logger.warning(f"[Score Calculation] CV score is 0 - possible causes: no face detected in video, poor lighting, or video processing error")
            else:
                logger.info(f"[Score Calculation] CV score: {cv_score}/100")
        
        # Get communication score (if available)
        if transcript_analysis and 'communication_score' in transcript_analysis:
            comm_score = transcript_analysis['communication_score'].get('score', 0)
        
        # Weighted average: 60% CV, 40% Communication
        if cv_score > 0 and comm_score > 0:
            overall = (cv_score * 0.6) + (comm_score * 0.4)
        elif cv_score > 0:
            overall = cv_score
        elif comm_score > 0:
            overall = comm_score
        else:
            overall = 0
        
        # Determine grade
        if overall >= 90:
            grade = "A+"
        elif overall >= 85:
            grade = "A"
        elif overall >= 80:
            grade = "B+"
        elif overall >= 75:
            grade = "B"
        elif overall >= 70:
            grade = "C+"
        elif overall >= 65:
            grade = "C"
        elif overall >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall_score": round(overall, 1),
            "grade": grade,
            "cv_score": cv_score,
            "communication_score": comm_score,
            "rating": "excellent" if overall >= 85 else "good" if overall >= 70 else "fair" if overall >= 60 else "needs_improvement"
        }
    
    async def _save_analysis_results(self, interview_id: str, results: Dict[str, Any]) -> None:
        """Save analysis results to database"""
        try:
            # Save to Supabase or store in sessionStorage
            # For now, we'll just log that we would save it
            logger.info(f"[Analysis Orchestrator] Would save results for interview {interview_id}")
            # TODO: Implement database save
        except Exception as e:
            logger.error(f"[Analysis Orchestrator] Error saving results: {e}")
    
    async def get_analysis_status(self, interview_id: str) -> Dict[str, str]:
        """Check if analysis is complete for an interview"""
        # TODO: Implement status tracking in database
        return {"status": "unknown", "interview_id": interview_id}

