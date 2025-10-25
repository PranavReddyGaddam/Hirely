"""
ElevenLabs Service for managing conversational AI agents.
Handles agent creation, configuration, and conversation management.
"""
import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings

class ElevenLabsService:
    """Service to manage ElevenLabs AI agents for persona-based voice consultations"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _create_system_prompt(
        self, 
        persona: Dict[str, Any], 
        startup_idea: Optional[str] = None,
        previous_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a system prompt for the agent based on persona information and context.
        This creates an agent that can discuss the specific startup idea with full context.
        """
        prompt = f"""You are {persona['name']}, a {persona['title']} based in {persona['location']}.

BACKGROUND:
{persona['bio']}

EXPERTISE:
You specialize in: {', '.join(persona['expertise'])}

YOUR ROLE:
You are conducting a voice consultation to provide expert feedback and insights on a specific startup idea. Draw upon your {persona['experience']} of experience in {persona['industry']}.

KEY INSIGHTS YOU'VE OBSERVED:
"""
        
        # Add persona insights if available
        if 'insights' in persona and persona['insights']:
            for insight in persona['insights']:
                prompt += f"- {insight}\n"
        
        # Add startup context if provided
        if startup_idea:
            prompt += f"\n\nSTARTUP IDEA FOR THIS CONSULTATION:\n{startup_idea}\n"
        
        # Add previous analysis if provided
        if previous_analysis:
            prompt += f"\n\nYOUR PREVIOUS ANALYSIS OF THIS IDEA:\n"
            if previous_analysis.get('rating'):
                prompt += f"- Rating: {previous_analysis['rating']}/10\n"
            if previous_analysis.get('sentiment'):
                prompt += f"- Sentiment: {previous_analysis['sentiment']}\n"
            if previous_analysis.get('key_insight'):
                prompt += f"- Key Insight: {previous_analysis['key_insight']}\n"
            
            # Add detailed analysis if available
            if previous_analysis.get('detailed_analysis'):
                detailed = previous_analysis['detailed_analysis']
                prompt += f"\nDETAILED ANALYSIS:\n"
                prompt += f"Market Potential: {detailed.get('marketPotential', 'N/A')}\n"
                prompt += f"Strengths: {', '.join(detailed.get('strengths', []))}\n"
                prompt += f"Concerns: {', '.join(detailed.get('concerns', []))}\n"
                prompt += f"Opportunities: {', '.join(detailed.get('opportunities', []))}\n"
                prompt += f"Recommendations: {', '.join(detailed.get('recommendations', []))}\n"
                prompt += f"Risks: {', '.join(detailed.get('risks', []))}\n"
                prompt += f"Action Items: {', '.join(detailed.get('actionItems', []))}\n"
            
            prompt += "\nIMPORTANT: You have already analyzed this startup idea in detail. Reference your analysis naturally in the conversation. Don't ask for basic details about the idea - you already know them. Instead, dive deeper into the specific points from your analysis and be ready to discuss implementation, challenges, and next steps."
        
        prompt += """
CONVERSATION STYLE:
- Be conversational and approachable, like speaking with a knowledgeable friend
- Reference your previous analysis naturally when relevant
- Provide specific, actionable feedback based on your expertise and analysis
- Share relevant examples from your experience in the industry
- Be honest about potential challenges while remaining encouraging
- Keep responses concise (2-3 sentences typically) to maintain natural conversation flow
- Focus on implementation details, next steps, and deeper insights rather than basic information gathering

Remember: You're having a real-time voice conversation. Be natural, authentic, and speak as yourself. You already know the startup idea and have analyzed it - use that knowledge to provide valuable insights."""
        
        return prompt
    
    def _create_interview_system_prompt(
        self, 
        persona: Dict[str, Any], 
        interview_config: Dict[str, Any]
    ) -> str:
        """
        Create a system prompt for interview agents with enhanced noise reduction awareness.
        """
        role = interview_config.get('role', 'interviewer')
        interview_type = interview_config.get('interview_type', 'mixed')
        enhanced_noise_reduction = interview_config.get('enhanced_noise_reduction', True)
        
        prompt = f"""You are {persona['name']}, a {persona['title']} based in {persona['location']}.

BACKGROUND:
{persona['bio']}

EXPERTISE:
You specialize in: {', '.join(persona['expertise'])}

YOUR ROLE:
You are conducting a {interview_type} interview. Your role is to {role} the candidate and provide a professional, supportive interview experience.

INTERVIEW CONTEXT:
- Interview Type: {interview_type}
- Your Role: {role}
- Enhanced Noise Reduction: {'Active' if enhanced_noise_reduction else 'Standard'}

KEY INSIGHTS YOU'VE OBSERVED:
"""
        
        # Add persona insights if available
        if 'insights' in persona and persona['insights']:
            for insight in persona['insights']:
                prompt += f"- {insight}\n"
        
        prompt += f"""
INTERVIEW STYLE:
- Be professional, warm, and encouraging
- Speak clearly and at a moderate pace for the introduction
- Use a formal but approachable tone
- Provide clear instructions and expectations
- Be patient and allow time for the candidate to process information
- Maintain a conversational, natural tone throughout

INTRODUCTION FOCUS:
- Welcome the candidate warmly
- Explain the interview format and structure
- Set clear expectations about the process
- Encourage the candidate to think out loud
- Reassure them about the interview environment
- Transition smoothly into the first question

NOISE REDUCTION AWARENESS:
- The system has enhanced noise reduction capabilities
- Speak clearly and at a moderate pace
- Pause briefly between sentences to allow for processing
- If you detect background noise or unclear speech, politely ask the candidate to repeat
- Be understanding of technical difficulties

CONVERSATION FLOW:
- Start with a comprehensive welcome and introduction
- Explain the interview process clearly
- Set expectations about timing and format
- Encourage the candidate and reduce anxiety
- Transition naturally into the first question
- Listen actively to responses
- Provide appropriate follow-up questions

SILENCE HANDLING (SMART INTERRUPTIONS):
- If candidate pauses for 5-10 seconds: Stay silent (normal thinking time)
- If candidate pauses for 12-15 seconds: Gently acknowledge with "Take your time" or "I'm listening"
- If candidate pauses for 20-25 seconds: Offer gentle help like "Would you like me to rephrase the question?" or "Is there a specific aspect you'd like to explore first?"
- If candidate pauses for 30+ seconds: Actively help by breaking down the question or offering examples
- Always distinguish between thinking pauses and being stuck
- Never interrupt while candidate is actively speaking (wait for natural pauses)
- If candidate says "um", "uh", or "let me think", give them space
- Only interrupt if it's clear they need help, not just processing

Remember: You're conducting a professional interview. Be natural, authentic, and supportive while maintaining interview standards. Your goal is to help candidates perform their best, not to trick them or make them uncomfortable."""
        
        return prompt
    
    async def create_agent_for_persona(
        self,
        persona: Dict[str, Any],
        startup_idea: Optional[str] = None,
        previous_analysis: Optional[Dict[str, Any]] = None,
        interview_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an ElevenLabs conversational AI agent for a specific persona with context.
        This agent will have the startup idea and analysis built into its system prompt.
        """
        # Use interview-specific prompt if interview config is provided
        if interview_config:
            system_prompt = self._create_interview_system_prompt(persona, interview_config)
        else:
            system_prompt = self._create_system_prompt(persona, startup_idea, previous_analysis)
        
        # Select an appropriate voice (you can customize this based on persona characteristics)
        voice_id = self._select_voice_for_persona(persona)
        
        # Create a contextual first message
        if interview_config:
            # Interview-specific introduction
            role = interview_config.get('role', 'interviewer')
            interview_type = interview_config.get('interview_type', 'mixed')
            candidate_data = interview_config.get('candidate_data', {})
            
            # Extract candidate information
            candidate_name = candidate_data.get('candidate_name', 'there')
            candidate_email = candidate_data.get('candidate_email', '')
            candidate_phone = candidate_data.get('candidate_phone', '')
            
            if role == 'interviewer':
                first_message = f"""Hello {candidate_name}! I'm {persona['name']}, your {interview_type} interviewer for today's session. 

Welcome to your interview! I'm excited to get to know you and learn about your background and experience. This will be a {interview_type} interview where we'll discuss various aspects of your technical skills and experience.

The interview will consist of several questions, and I encourage you to think out loud as you work through your responses. Don't worry about getting everything perfect - I'm interested in your thought process and how you approach problems.

Are you ready to begin? Let's start with our first question."""
            else:
                first_message = f"Hello {candidate_name}! I'm {persona['name']}, {persona['title']}. I'm here to conduct your {interview_type} interview. Let's begin!"
        elif previous_analysis and previous_analysis.get('key_insight'):
            first_message = f"Hello! I'm {persona['name']}. I've already analyzed your startup idea and given it a {previous_analysis.get('rating', 'N/A')}/10. I'm excited to dive deeper into my thoughts and discuss the specific insights from my analysis. What aspect would you like to explore first?"
        else:
            first_message = f"Hello! I'm {persona['name']}, {persona['title']}. I'm here to help you with your startup idea and provide insights from my {persona['experience']} of experience in {persona['industry']}. What would you like to discuss?"
        
        # Enhanced configuration for interview agents
        if interview_config:
            enhanced_noise_reduction = interview_config.get('enhanced_noise_reduction', True)
            agent_config = {
                "conversation_config": {
                    "agent": {
                        "first_message": first_message,
                        "language": "en",
                        "prompt": {
                            "prompt": system_prompt,
                            "llm": "gpt-4o",
                            "temperature": 0.6,  # Slightly lower for more consistent interview responses
                            "max_tokens": 400
                        }
                    },
                    "tts": {
                        "voice_id": voice_id,
                        "model_id": "eleven_turbo_v2",
                        "stability": 0.8,  # Higher stability for clearer speech
                        "similarity_boost": 0.7,  # Better voice consistency
                        "style": 0.2,  # Professional tone
                        "use_speaker_boost": True  # Enhanced voice clarity
                    },
                    "stt": {
                        "model": "whisper-1",
                        "language": "en",
                        "temperature": 0.0,  # More accurate transcription
                        "enhanced_noise_reduction": enhanced_noise_reduction,
                        "echo_cancellation": True,
                        "noise_suppression": True,
                        "auto_gain_control": True,
                        "voice_activity_detection": True,
                        "background_noise_suppression": True,
                        "wind_noise_reduction": True,
                        "aggressive_noise_suppression": True,
                        "vad_threshold": 0.7,  # Higher threshold to filter background noise
                        "min_speech_duration": 0.5,  # Minimum speech duration to process
                        "max_silence_duration": 2.0,  # Max silence before stopping
                        "noise_gate_threshold": 0.3  # Noise gate to filter low-level sounds
                    }
                },
                "name": f"{persona['name']} - {interview_config.get('role', 'Interviewer').title()}"
            }
        else:
            # Standard configuration for startup consultations
            agent_config = {
                "conversation_config": {
                    "agent": {
                        "first_message": first_message,
                        "language": "en",
                        "prompt": {
                            "prompt": system_prompt,
                            "llm": "gpt-4o",
                            "temperature": 0.7,
                            "max_tokens": 500
                        }
                    },
                    "tts": {
                        "voice_id": voice_id,
                        "model_id": "eleven_turbo_v2"
                    }
                },
                "name": f"{persona['name']} - Consultant"
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/convai/agents/create",
                    headers=self.headers,
                    json=agent_config
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "agent_id": result["agent_id"],
                    "persona_id": persona["id"],
                    "persona_name": persona["name"],
                    "system_prompt": system_prompt
                }
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
                print(f"ElevenLabs API Error Response: {json.dumps(error_detail, indent=2)}")
            except:
                error_detail = e.response.text
                print(f"ElevenLabs API Error Text: {error_detail}")
            print(f"Error creating ElevenLabs agent: {e}")
            print(f"Request payload: {json.dumps(agent_config, indent=2)}")
            raise Exception(f"Failed to create agent: {str(e)} - {error_detail}")
        except httpx.HTTPError as e:
            print(f"Error creating ElevenLabs agent: {e}")
            raise Exception(f"Failed to create agent: {str(e)}")
    
    def _select_voice_for_persona(self, persona: Dict[str, Any]) -> str:
        """
        Select an appropriate voice ID based on persona characteristics
        You can expand this logic to match voices to persona demographics
        """
        # Default voices - you can customize this mapping
        # ElevenLabs has many voices available in their library
        default_voices = {
            "male": "21m00Tcm4TlvDq8ikWAM",  # Example male voice
            "female": "EXAVITQu4vr4xnSDxMaL",  # Example female voice
        }
        
        # Simple gender detection from name (can be improved)
        # For now, using a default professional voice
        return "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional female voice
    
    async def get_agent_link(self, agent_id: str) -> Dict[str, str]:
        """
        Get the agent link (for public agents, this is just the agent ID)
        """
        return {
            "agent_id": agent_id,
            "agent_url": f"https://elevenlabs.io/app/conversational-ai/{agent_id}"
        }
    
    async def get_conversation_details(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve details and transcript of a completed conversation
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/convai/conversations/{conversation_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching conversation details: {e}")
            raise Exception(f"Failed to fetch conversation: {str(e)}")
    
    async def start_conversation_with_context(
        self,
        agent_id: str,
        startup_idea: Optional[str] = None,
        previous_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a conversation with an existing agent and provide context about the startup idea and analysis.
        This allows the agent to reference the detailed analysis during the conversation.
        
        Note: ElevenLabs conversational AI agents are typically accessed directly via their agent URL.
        This method returns the agent information for direct access.
        """
        try:
            # For ElevenLabs conversational AI, we don't create separate conversations
            # Instead, we return the agent information so users can interact directly
            # The agent already has the context built into its system prompt
            
            # Get the agent link
            agent_link = await self.get_agent_link(agent_id)
            
            return {
                "conversation_id": f"direct-{agent_id}",  # Placeholder for direct access
                "agent_id": agent_id,
                "context_provided": True,
                "agent_url": agent_link["agent_url"],
                "message": "Agent is ready for direct conversation. Use the agent URL to start talking."
            }
                
        except Exception as e:
            print(f"Error preparing agent for conversation: {e}")
            raise Exception(f"Failed to prepare agent: {str(e)}")

    async def send_message_to_agent(self, agent_id: str, message: str) -> str:
        """
        Send a message to an ElevenLabs agent and get a response.
        For now, we'll use a simulated response since the exact conversational AI API endpoint structure may vary.
        """
        try:
            # For ElevenLabs conversational AI, the exact API structure may vary
            # Let's use a more realistic response based on the message content
            # In a production environment, you would need to check the exact API documentation
            
            # Simulate intelligent responses based on the message content
            message_lower = message.lower()
            
            if any(word in message_lower for word in ["hello", "hi", "hey"]):
                return "Hello! I'm excited to discuss your startup idea with you. Based on my analysis, I see great potential here. What specific aspect would you like to dive into first?"
            elif any(word in message_lower for word in ["market", "competition", "competitor"]):
                return "Great question about the market! From my experience, I'd recommend focusing on your unique value proposition. The market analysis shows strong potential, but differentiation will be key to your success."
            elif any(word in message_lower for word in ["funding", "investment", "money", "capital"]):
                return "Funding strategy is crucial at this stage. Based on your startup's current position, I'd suggest starting with seed funding to validate your MVP before seeking larger rounds."
            elif any(word in message_lower for word in ["team", "hiring", "people"]):
                return "Team building is one of the most critical aspects of startup success. Focus on finding people who share your vision and bring complementary skills to the table."
            elif any(word in message_lower for word in ["product", "development", "build"]):
                return "Product development should be driven by user feedback. I recommend starting with an MVP to test your core assumptions before building additional features."
            elif any(word in message_lower for word in ["challenge", "problem", "issue", "difficulty"]):
                return "Every startup faces challenges, and that's completely normal. The key is to identify the most critical obstacles early and develop strategies to overcome them systematically."
            else:
                return f"Thank you for sharing that with me. As someone with extensive experience in this industry, I find your perspective interesting. Could you tell me more about how you're planning to address the main challenges you're facing?"
            
        except Exception as e:
            print(f"Error sending message to agent: {e}")
            return "I apologize, but I'm having trouble processing your message right now. Please try again."
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent when no longer needed
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/convai/agents/{agent_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            print(f"Error deleting agent: {e}")
            return False
    
    async def get_conversation_transcript(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get transcript of a completed ElevenLabs conversation.
        
        Args:
            conversation_id: Conversation ID from ElevenLabs
            
        Returns:
            Dict with transcript data including text, timestamps, and speaker info
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/convai/conversations/{conversation_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                conversation_data = response.json()
                
                # Extract transcript from conversation data
                # ElevenLabs returns conversation with messages/turns
                transcript_text = ""
                messages = []
                
                if 'transcript' in conversation_data:
                    # If direct transcript is available (could be string or list)
                    raw_transcript = conversation_data['transcript']
                    if isinstance(raw_transcript, list):
                        # Join list items into single string
                        transcript_text = " ".join(str(item) for item in raw_transcript)
                    else:
                        transcript_text = str(raw_transcript)
                elif 'messages' in conversation_data:
                    # Build transcript from messages
                    for msg in conversation_data['messages']:
                        speaker = msg.get('role', 'unknown')
                        text = msg.get('message', '')
                        timestamp = msg.get('timestamp', '')
                        
                        messages.append({
                            'speaker': speaker,
                            'text': text,
                            'timestamp': timestamp
                        })
                        
                        transcript_text += f"{text} "
                
                return {
                    'conversation_id': conversation_id,
                    'full_transcript': transcript_text.strip(),
                    'messages': messages,
                    'duration': conversation_data.get('duration', 0),
                    'created_at': conversation_data.get('created_at', '')
                }
                
        except httpx.HTTPStatusError as e:
            print(f"Error fetching conversation transcript: {e}")
            print(f"Status code: {e.response.status_code}")
            return None
        except httpx.HTTPError as e:
            print(f"Error fetching conversation transcript: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching transcript: {e}")
            return None
