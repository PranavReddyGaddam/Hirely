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
import groq

from app.services.supabase_service import SupabaseService
from app.services.s3_service import S3Service
from app.services.elevenlabs_service import ElevenLabsService
from app.services.transcript_analyzer import TranscriptAnalyzer
from app.services.enhanced_metrics_calculator import EnhancedMetricsCalculator
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
        self.enhanced_metrics_calc = EnhancedMetricsCalculator()
        # Use Groq instead of OpenRouter for AI insights
        from app.services.groq_service import GroqService
        self.groq_service = GroqService()
    
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
            "user_id": user_id,
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
                # Retry logic: wait up to 5 minutes for video to appear (video upload can be slow)
                max_retries = 300  # 5 minutes (300 seconds)
                retry_count = 0
                while not interview.video_storage_path and retry_count < max_retries:
                    await asyncio.sleep(1)
                    interview = await self.supabase_service.get_interview(interview_id, user_id)
                    if interview.video_storage_path:
                        logger.info(f"[Analysis Orchestrator] ✅ Video found after {retry_count + 1}s: {interview.video_storage_path}")
                        break
                    retry_count += 1
                    
                    # Log progress every 30 seconds
                    if retry_count % 30 == 0:
                        logger.info(f"[Analysis Orchestrator] Still waiting for video... ({retry_count}s elapsed)")
                
                if not interview.video_storage_path:
                    logger.error(f"[Analysis Orchestrator] ❌ Video still not found after {max_retries}s, skipping CV analysis")
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
                
                if transcript_data and transcript_data.get('user_transcript'):
                    # Analyze only user's speech (not agent's responses)
                    user_transcript = transcript_data['user_transcript']
                    logger.info(f"[Analysis Orchestrator] Analyzing user transcript ({len(user_transcript)} chars)")
                    logger.info(f"[Analysis Orchestrator] Conversation duration: {transcript_data.get('duration', 0)} seconds")
                    
                    # Get interview duration
                    duration = transcript_data.get('duration', 0)
                    if cv_analysis and 'session_info' in cv_analysis:
                        duration = cv_analysis['session_info'].get('duration_seconds', duration)
                    
                    # Analyze speech patterns
                    transcript_analysis = self.transcript_analyzer.analyze_transcript(
                        user_transcript,
                        duration
                    )
                    
                    # Add conversation metadata
                    transcript_analysis['conversation_id'] = conversation_id
                    transcript_analysis['full_conversation'] = transcript_data.get('full_transcript', '')
                    transcript_analysis['messages'] = transcript_data.get('messages', [])
                    transcript_analysis['conversation_metadata'] = transcript_data.get('metadata', {})
                    
                    results['transcript_analysis'] = transcript_analysis
                    logger.info(f"[Analysis Orchestrator] ✅ Transcript analysis complete")
                    logger.info(f"[Analysis Orchestrator]   - Communication score: {transcript_analysis.get('communication_score', {}).get('score', 0)}/100")
                else:
                    logger.warning(f"[Analysis Orchestrator] No transcript available from ElevenLabs")
            else:
                logger.warning(f"[Analysis Orchestrator] No conversation_id provided")
            
            # Step 4: Calculate enhanced metrics from existing data
            logger.info(f"[Analysis Orchestrator] Calculating enhanced metrics")
            if cv_analysis and transcript_analysis:
                try:
                    enhanced_cv = self.enhanced_metrics_calc.calculate_enhanced_cv_metrics(cv_analysis)
                    enhanced_comm = self.enhanced_metrics_calc.calculate_enhanced_communication_metrics(transcript_analysis)
                    comparison = self.enhanced_metrics_calc.calculate_comparison_metrics(cv_analysis, transcript_analysis)
                    roadmap = self.enhanced_metrics_calc.calculate_improvement_roadmap(
                        cv_analysis, transcript_analysis, enhanced_cv, enhanced_comm
                    )
                    
                    results['enhanced_metrics'] = {
                        'cv_detailed': enhanced_cv,
                        'communication_detailed': enhanced_comm,
                        'comparison_to_benchmarks': comparison,
                        'improvement_roadmap': roadmap
                    }
                    logger.info(f"[Analysis Orchestrator] ✅ Enhanced metrics calculated")
                except Exception as e:
                    logger.error(f"[Analysis Orchestrator] Enhanced metrics calculation failed: {e}")
                    results['enhanced_metrics'] = None
            
            # Step 5: Generate AI insights using Groq (with enhanced metrics)
            logger.info(f"[Analysis Orchestrator] Generating AI insights with Groq")
            ai_insights = await self._generate_ai_insights(
                cv_analysis,
                transcript_analysis,
                interview.interview_type,
                results.get('enhanced_metrics')  # Pass enhanced metrics to AI
            )
            results['ai_insights'] = ai_insights
            
            # Step 6: Calculate overall score
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
        interview_type: str,
        enhanced_metrics: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate AI insights using Groq"""
        
        # Validate Groq service
        if not self.groq_service:
            error_msg = "Groq service not initialized"
            logger.error(f"[AI Insights] ❌ {error_msg}")
            return {
                "feedback": f"AI insights unavailable: {error_msg}. Please check server configuration.",
                "error": error_msg,
                "error_type": "service_not_initialized"
            }
        
        if not self.groq_service.client:
            error_msg = "Groq API client not configured. Please verify GROQ_API_KEY in environment variables."
            logger.error(f"[AI Insights] ❌ {error_msg}")
            return {
                "feedback": f"AI insights unavailable: {error_msg}",
                "error": error_msg,
                "error_type": "api_key_missing"
            }
        
        # Log what data we have for analysis
        logger.info(f"[AI Insights] 🔍 Preparing to generate insights:")
        logger.info(f"[AI Insights]   - CV Analysis: {'Available' if cv_analysis else 'Missing'}")
        logger.info(f"[AI Insights]   - Transcript Analysis: {'Available' if transcript_analysis else 'Missing'}")
        logger.info(f"[AI Insights]   - Interview Type: {interview_type}")
        
        try:
            # Build comprehensive prompt with enhanced metrics
            logger.info("[AI Insights] 📝 Building analysis prompt...")
            prompt = self._build_analysis_prompt(cv_analysis, transcript_analysis, interview_type, enhanced_metrics)
            logger.info(f"[AI Insights] 📝 Prompt length: {len(prompt)} characters")
            
            system_prompt = """You are an expert interview performance analyst and career coach with deep expertise in behavioral psychology and communication skills.

Your role is to ANALYZE a candidate's completed interview performance based on comprehensive metrics and provide data-driven, actionable feedback.

You will receive:
- **Basic Metrics:** Visual behavior (facial expressions, eye contact, posture), communication (filler words, pace, vocabulary)
- **Enhanced Metrics:** Professional presence scores, nervousness indicators, energy levels, confidence assessments
- **Benchmark Comparisons:** How the candidate compares to average candidates and top 10% performers
- **Identified Issues:** Prioritized improvement areas with current→target metrics
- **Conversation Samples:** Actual responses from the interview

Your response should include:
1. **Executive Summary** (2-3 sentences - reference SPECIFIC numbers from the data)
2. **Top 3 Strengths** (cite exact metrics, e.g., "Your eye contact of 85% exceeded the 65% average")
3. **Top 3 Areas for Improvement** (reference the provided improvement roadmap and metrics)
4. **Detailed Recommendations** (5-7 concrete actions based on the specific issues identified)
5. **Next Steps** (3-4 practical steps with measurable goals, e.g., "Practice to reduce filler words from 5.2% to under 3%")

CRITICAL Guidelines:
- BE SPECIFIC: Always cite exact numbers and metrics (e.g., "78% posture", "3.2% filler words", "145 WPM")
- BE COMPARATIVE: Reference averages and benchmarks (e.g., "above the 65% average", "approaching top 10% at 85%")
- BE ACTIONABLE: Every suggestion must be concrete and measurable
- ACKNOWLEDGE CONTEXT: If improvement roadmap shows specific issues, address those directly
- Use a professional, supportive, data-driven tone
- DO NOT ask questions - this is POST-interview analysis
- DO NOT be generic - use the rich data provided"""
            
            # Call Groq API
            logger.info("[AI Insights] 🚀 Calling Groq API...")
            logger.info("[AI Insights]   - Model: llama-3.3-70b-versatile")
            logger.info("[AI Insights]   - Temperature: 0.7")
            logger.info("[AI Insights]   - Max tokens: 2000")
            
            response = self.groq_service.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            logger.info("[AI Insights] 📥 Received response from Groq API")
            
            if response.choices and len(response.choices) > 0:
                feedback_text = response.choices[0].message.content
                logger.info(f"[AI Insights] ✅ Successfully generated {len(feedback_text)} characters of feedback")
                logger.info(f"[AI Insights] ✅ Preview: {feedback_text[:100]}...")
                
                return {
                    "feedback": feedback_text,
                    "model": "llama-3.3-70b-versatile",
                    "success": True
                }
            else:
                error_msg = "Groq API returned empty response (no choices)"
                logger.error(f"[AI Insights] ❌ {error_msg}")
                logger.error(f"[AI Insights] ❌ Full response: {response}")
                raise Exception(error_msg)
            
        except groq.APIError as e:
            error_msg = f"Groq API Error: {str(e)}"
            logger.error(f"[AI Insights] ❌ {error_msg}", exc_info=True)
            return {
                "feedback": f"AI insights generation failed due to API error. Error: {str(e)}\n\nPlease review the metrics manually or try again later.",
                "error": error_msg,
                "error_type": "api_error",
                "success": False
            }
        except groq.RateLimitError as e:
            error_msg = f"Groq API Rate Limit: {str(e)}"
            logger.error(f"[AI Insights] ❌ {error_msg}")
            return {
                "feedback": "AI insights generation failed due to rate limiting. Please try again in a few moments.\n\nPlease review the metrics manually in the meantime.",
                "error": error_msg,
                "error_type": "rate_limit",
                "success": False
            }
        except groq.AuthenticationError as e:
            error_msg = f"Groq Authentication Error: {str(e)}"
            logger.error(f"[AI Insights] ❌ {error_msg}")
            return {
                "feedback": "AI insights generation failed due to authentication error. Please contact support.\n\nPlease review the metrics manually.",
                "error": error_msg,
                "error_type": "authentication_error",
                "success": False
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"[AI Insights] ❌ {error_msg}", exc_info=True)
            logger.error(f"[AI Insights] ❌ Error type: {type(e).__name__}")
            return {
                "feedback": f"AI insights generation encountered an unexpected error: {str(e)}\n\nPlease review the metrics manually or contact support if this persists.",
                "error": error_msg,
                "error_type": "unexpected_error",
                "success": False
            }
    
    def _build_analysis_prompt(
        self,
        cv_analysis: Optional[Dict],
        transcript_analysis: Optional[Dict],
        interview_type: str,
        enhanced_metrics: Optional[Dict] = None
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
            
            # Include sample of actual conversation for context
            messages = transcript_analysis.get('messages', [])
            if messages:
                prompt += "## Interview Conversation Sample\n\n"
                prompt += "Here are key excerpts from the candidate's responses:\n\n"
                
                # Get user messages only (up to 5 key responses)
                user_messages = [msg for msg in messages if msg.get('speaker') == 'user'][:5]
                for i, msg in enumerate(user_messages, 1):
                    text = msg.get('text', '')[:200]  # Limit to 200 chars
                    prompt += f"{i}. \"{text}...\"\n\n"
        
        # Enhanced Metrics section - DETAILED ANALYSIS
        if enhanced_metrics:
            prompt += "## Enhanced Performance Metrics (DETAILED ANALYSIS)\n\n"
            prompt += "**These are advanced, actionable metrics calculated from the raw data above:**\n\n"
            
            # Professional Presence
            cv_detailed = enhanced_metrics.get('cv_detailed', {})
            if cv_detailed.get('professional_presence'):
                presence = cv_detailed['professional_presence']
                prompt += f"### Professional Presence: {presence.get('overall_score', 0):.1f}/100 ({presence.get('rating', 'N/A')})\n"
                prompt += f"- This combines eye contact, posture, engagement, and emotional stability\n\n"
            
            # Eye Contact Details
            if cv_detailed.get('eye_contact_detailed'):
                eye = cv_detailed['eye_contact_detailed']
                prompt += f"### Eye Contact Quality: {eye.get('quality_rating', 'N/A')}\n"
                prompt += f"- Direct contact: {eye.get('direct_contact_percentage', 0):.1f}%\n"
                prompt += f"- Looking away: {eye.get('looking_away_percentage', 0):.1f}%\n"
                prompt += f"- Looking down: {eye.get('looking_down_percentage', 0):.1f}%\n"
                if eye.get('improvement_needed'):
                    prompt += f"- ⚠️ **Needs Improvement**: {eye.get('tip', '')}\n"
                prompt += "\n"
            
            # Nervousness Indicators
            if cv_detailed.get('nervousness_indicators'):
                nerv = cv_detailed['nervousness_indicators']
                prompt += f"### Nervousness Level: {nerv.get('nervousness_rating', 'N/A')}\n"
                prompt += f"- Hand fidgeting: {nerv.get('hand_fidgeting_count', 0)} times\n"
                prompt += f"- Face touching: {nerv.get('face_touching_count', 0)} times\n"
                prompt += f"- Total nervous movements: {nerv.get('total_nervous_movements', 0)}\n"
                if nerv.get('total_nervous_movements', 0) > 10:
                    prompt += f"- ⚠️ **High nervousness detected** - recommend relaxation techniques\n"
                prompt += "\n"
            
            # Energy & Enthusiasm
            if cv_detailed.get('energy_enthusiasm'):
                energy = cv_detailed['energy_enthusiasm']
                prompt += f"### Energy & Enthusiasm: {energy.get('enthusiasm_rating', 'N/A')}\n"
                prompt += f"- Energy level: {energy.get('energy_level', 0)}/100\n"
                prompt += f"- Genuine smiles: {energy.get('genuine_smiles', 0)}\n"
                prompt += f"- Dominant emotion: {energy.get('dominant_emotion', 'N/A')}\n\n"
            
            # Communication Details
            comm_detailed = enhanced_metrics.get('communication_detailed', {})
            if comm_detailed.get('speech_quality'):
                speech = comm_detailed['speech_quality']
                prompt += f"### Speech Quality: {speech.get('pace_rating', 'N/A')}\n"
                prompt += f"- Speaking pace: {speech.get('speaking_pace_wpm', 0):.0f} WPM\n"
                prompt += f"- Ideal range: 130-160 WPM\n"
                prompt += f"- In ideal range: {'✅ Yes' if speech.get('in_ideal_range') else '⚠️ No'}\n"
                if speech.get('tip'):
                    prompt += f"- Tip: {speech.get('tip')}\n"
                prompt += "\n"
            
            # Filler Word Details
            if comm_detailed.get('filler_analysis_detailed'):
                filler = comm_detailed['filler_analysis_detailed']
                prompt += f"### Filler Word Analysis: {filler.get('rating', 'N/A')}\n"
                prompt += f"- Total: {filler.get('total_count', 0)} ({filler.get('percentage', 0):.1f}%)\n"
                prompt += f"- Most used: \"{filler.get('most_used', 'none')}\" ({filler.get('most_used_count', 0)}x)\n"
                prompt += f"- Confidence impact: {filler.get('confidence_impact', 'N/A')}\n"
                if filler.get('tip'):
                    prompt += f"- Tip: {filler.get('tip')}\n"
                prompt += "\n"
            
            # Vocabulary Details
            if comm_detailed.get('vocabulary_detailed'):
                vocab = comm_detailed['vocabulary_detailed']
                prompt += f"### Vocabulary: {vocab.get('rating', 'N/A')}\n"
                prompt += f"- Unique words: {vocab.get('unique_words', 0)}/{vocab.get('total_words', 0)}\n"
                prompt += f"- Diversity: {vocab.get('diversity_percentage', 0):.1f}%\n"
                if vocab.get('tip'):
                    prompt += f"- Tip: {vocab.get('tip')}\n"
                prompt += "\n"
            
            # Comparison to Benchmarks
            comparison = enhanced_metrics.get('comparison_to_benchmarks', {})
            if comparison:
                prompt += "### Comparison to Average Candidates\n\n"
                for metric_name, data in comparison.items():
                    status = data.get('status', 'N/A')
                    your_score = data.get('your_score', 0)
                    avg = data.get('average', 0)
                    top10 = data.get('top_10_percent', 0)
                    
                    status_emoji = "✅" if status in ['above_average', 'on_target'] else "⚠️"
                    prompt += f"**{metric_name.replace('_', ' ').title()}:** {status_emoji} {status.replace('_', ' ').title()}\n"
                    prompt += f"  - Your score: {your_score}\n"
                    prompt += f"  - Average: {avg}\n"
                    prompt += f"  - Top 10%: {top10}\n\n"
            
            # Improvement Roadmap
            roadmap = enhanced_metrics.get('improvement_roadmap', [])
            if roadmap:
                prompt += "### Priority Improvements Needed\n\n"
                prompt += "**The following issues were automatically identified and should be addressed:**\n\n"
                for i, item in enumerate(roadmap, 1):
                    priority_emoji = "🔴" if item['priority'] == 'high' else "🟡" if item['priority'] == 'medium' else "🔵"
                    prompt += f"{i}. {priority_emoji} **[{item['priority'].upper()}] {item['issue']}**\n"
                    prompt += f"   - Current: {item['current']} → Target: {item['target']}\n"
                    prompt += f"   - Impact: {item['impact']}\n"
                    prompt += f"   - Action: {item['action']}\n\n"
        
        prompt += "\n\n---\n\n"
        prompt += "**INSTRUCTIONS FOR YOUR ANALYSIS:**\n\n"
        prompt += "Based on ALL the data above (basic metrics + enhanced metrics + comparisons + identified issues), provide comprehensive, data-driven feedback.\n\n"
        prompt += "Reference specific numbers and metrics in your response. For example:\n"
        prompt += "- 'Your eye contact was strong at 85%, well above the average of 65%'\n"
        prompt += "- 'Your filler word usage of 3.2% is excellent, showing strong confidence'\n"
        prompt += "- 'The 12 instances of fidgeting suggest some nervousness - try relaxation techniques'\n\n"
        prompt += "Make your feedback actionable and specific, not generic."
        
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
            logger.info(f"[Analysis Orchestrator] Saving results to database for interview {interview_id}")
            
            # Prepare analysis data for database
            analysis_data = {
                'interview_id': interview_id,
                'user_id': results.get('user_id'),  # Get from results if available
                'status': results.get('analysis_status', 'completed'),
                'overall_score': results.get('overall_score', {}).get('overall_score'),
                'detailed_analysis': results,  # Store full results as JSONB
                'created_at': datetime.utcnow().isoformat(),
                'completed_at': datetime.utcnow().isoformat() if results.get('analysis_status') == 'completed' else None
            }
            
            # Check if analysis already exists
            existing = self.supabase_service.client.table('analysis').select('id').eq('interview_id', interview_id).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing record
                result = self.supabase_service.client.table('analysis').update(analysis_data).eq('interview_id', interview_id).execute()
                logger.info(f"[Analysis Orchestrator] ✅ Updated existing analysis record for {interview_id}")
            else:
                # Insert new record
                result = self.supabase_service.client.table('analysis').insert(analysis_data).execute()
                logger.info(f"[Analysis Orchestrator] ✅ Saved new analysis record for {interview_id}")
            
        except Exception as e:
            logger.error(f"[Analysis Orchestrator] Error saving results: {e}", exc_info=True)
    
    async def get_analysis_status(self, interview_id: str) -> Dict[str, str]:
        """Check if analysis is complete for an interview"""
        # TODO: Implement status tracking in database
        return {"status": "unknown", "interview_id": interview_id}

