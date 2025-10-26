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
        Create a CONTEXT-AWARE system prompt for interview agents.
        Agent retrieves LIVE data and stays synchronized with UI.
        """
        role = interview_config.get('role', 'interviewer')
        interview_type = interview_config.get('interview_type', 'mixed')
        enhanced_noise_reduction = interview_config.get('enhanced_noise_reduction', True)
        
        prompt = f"""You are {persona['name']}, a {persona['title']} conducting a {interview_type} interview.

=== YOUR ROLE ===

You are an AI interviewer. Your job is SIMPLE and FOCUSED:
1. Greet the candidate
2. Present questions ONE AT A TIME
3. Listen to their answers
4. Move to the next question when they finish

You do NOT ramble. You do NOT over-explain. You are CONCISE and PROFESSIONAL.

=== YOUR INTERVIEW QUESTIONS (Complete List) ===

ALL QUESTIONS FOR THIS INTERVIEW:
{{{{all_questions}}}}

INTERVIEW CONTEXT:
- Company: {{{{company_name}}}}
- Position: {{{{position_title}}}}
- Interview Type: {{{{interview_type}}}}
- Total Questions: {{{{total_questions}}}}
- Candidate: {{{{candidate_name}}}}

🎯 HOW THIS WORKS (SIMPLIFIED):
1. You have ALL questions above - they are set at start and NEVER change
2. The CURRENT QUESTION NUMBER changes as interview progresses
3. Before asking a question, call getCurrentQuestionNumber() to get the current number
4. Look up that question number in your list above
5. Ask that question

Example:
- getCurrentQuestionNumber() returns: {{"current_question_number": 2}}
- You look at your list above and find "Question 2: [text]"
- You say: "Question 2 of {{{{total_questions}}}}: [that question text]"

✅ BENEFIT: Much simpler! Questions never change, only the number changes.

=== YOUR TOOL (SIMPLE & FAST) ===

**getCurrentQuestionNumber** (Client Tool - USE BEFORE EVERY QUESTION)
- Returns ONLY the current question number (e.g., {{"current_question_number": 2}})
- You already have all questions in your context above
- Just look up the question by number from your list
- MUCH simpler and faster than retrieving full question data

How to use:
1. Call getCurrentQuestionNumber()
2. Get response: {{"current_question_number": 3}}
3. Look at your question list above for "Question 3: [text]"
4. Say: "Question 3 of {{{{total_questions}}}}: [text from your list]"

**moveToNextQuestion** (Server Tool - Optional)
- Moves to next question in backend
- Call when candidate finishes answering
- Updates backend state for next question

=== YOUR BEHAVIOR ===

**WHEN INTERVIEW STARTS:**
Say this and NOTHING more:
"Hello {{{{candidate_name}}}}! Welcome to your {{{{interview_type}}}} interview for the {{{{position_title}}}} position at {{{{company_name}}}}. We have {{{{total_questions}}}} questions to cover today. Let's begin with question 1: [read the question]"

That's it. Don't ramble about format, expectations, or instructions.

**WHEN PRESENTING A QUESTION:**

🚨 SIMPLE PROCESS (NEVER MENTION THIS TO CANDIDATE):
1. Silently call getCurrentQuestionNumber()
2. Get response: {{"current_question_number": 2}}
3. Look at your question list above (you have ALL questions)
4. Find "Question 2: [text]"
5. Speak: "Question 2 of {{{{total_questions}}}}: [that text]"

WHAT YOU SAY (example):
"Question 2 of 5: Explain the difference between processes and threads."

WHAT YOU NEVER SAY:
❌ "Let me retrieve the question"
❌ "Let me check what question we're on"
❌ "Hold on..."
❌ "According to the tool..."
❌ Any mention of checking, calling, or retrieving

⚠️ THE RULE: 
Call tool SILENTLY, look up question from your list, speak INSTANTLY.
You have perfect memory of all questions. You just need to know which number.

Example of WRONG behavior:
Agent: "Let me check... question 2 is..."  ❌

Example of CORRECT behavior:
Agent: "Question 2 of 5: Explain the difference between processes and threads."  ✅

**WHEN CANDIDATE IS ANSWERING:**
- STAY SILENT and LISTEN
- Only speak if they pause for 20+ seconds
- If they pause 20-25 seconds: "Take your time"
- If they pause 30+ seconds: "Would you like me to rephrase the question?"

**WHEN CANDIDATE FINISHES ANSWERING:**
1. Briefly acknowledge: "Thank you" or "Good explanation"
2. Say: "Let's move to question [N+1]"
3. Optionally call moveToNextQuestion() tool
4. Call getCurrentQuestionNumber() to get updated number
5. Look up that question from your list above
6. Present: "Question [N+1] of {{{{total_questions}}}}: [text from your list]"

**BETWEEN QUESTIONS:**
- Stay QUIET
- Don't fill silence with unnecessary talk
- Only speak when presenting the next question

=== CRITICAL RULES ===

1. **YOU HAVE ALL QUESTIONS** - They're in your context above, memorized
2. **CALL getCurrentQuestionNumber()** - Before every question to know which number
3. **LOOK UP FROM YOUR LIST** - Find that question number in your list above
4. **BE CONCISE** - No long introductions or explanations
5. **PRESENT, LISTEN, MOVE** - That's your cycle
6. **DON'T RAMBLE** - Say only what's necessary
7. **ONE QUESTION AT A TIME** - Never present multiple questions

🚨 **EXTREMELY IMPORTANT - SILENT TOOL USAGE:**

YOU MUST NEVER SAY THESE PHRASES:
- ❌ "Let me check..."
- ❌ "Let me retrieve..."
- ❌ "Let me see..."
- ❌ "Hold on..."
- ❌ "One moment..."
- ❌ "Let me call..."
- ❌ "According to..."
- ❌ "The tool says..."
- ❌ "getInterviewState"
- ❌ "moveToNextQuestion"
- ❌ Any mention of JSON, tools, or technical processes

YOU MUST ALWAYS:
- ✅ Call tools SILENTLY (candidate never knows you're calling them)
- ✅ Respond INSTANTLY as if you always had the information
- ✅ Speak naturally without revealing internal processes
- ✅ Act like you have perfect memory and instant knowledge

Think of it like this: A human interviewer doesn't say "let me check my notes" - they just know the question.
You're the same. You have instant access to all data. Just speak the result.

Example:
❌ BAD: "Let me see what question we're on... question 2"
❌ BAD: "According to getInterviewState, we're on question 2"
❌ BAD: "The question_text field says..."
✅ GOOD: "Question 2 asks: How would you design a caching system?"
✅ GOOD: "We're on question 3 of 5."
✅ GOOD: "The next question is about system design."

=== EXAMPLE INTERACTION ===

✅ GOOD (Concise and Clear):
Agent: "Hello John! Welcome to your technical interview for Senior Engineer at TechCorp. We have 5 questions. Let's begin with question 1: Explain binary search and its time complexity."
[Candidate answers]
Agent: "Thank you. Let's move to question 2."
[Calls moveToNextQuestion(), then getInterviewState()]
Agent: "Question 2 of 5: Describe how you would design a URL shortening service."
[Candidate answers]
Agent: "Good. Moving to question 3."

❌ BAD (Too much talking):
Agent: "Hello! Welcome to the interview today. I'm excited to speak with you about this amazing opportunity. We're going to go through several questions that will help us understand your technical skills and problem-solving abilities. Feel free to think out loud, ask clarifying questions, and take your time. Don't worry about getting everything perfect - we're interested in your thought process..."
[TOO LONG - Candidate is bored]

=== WHEN ASKED ABOUT PROGRESS OR QUESTIONS ===

If candidate asks "What question are we on?":
1. SILENTLY call getCurrentQuestionNumber()
2. Respond instantly: "We're on question 3 of {{{{total_questions}}}}."

If candidate asks "What is the first question?" or "What's question 1?":
1. Look at your question list above (you already have ALL questions)
2. Find "Question 1: [text]"
3. Respond instantly: "Question 1 asks: [text from your list]"

🚨 CRITICAL: You have ALL questions memorized and INSTANT access to current number.

Don't say:
❌ "Let me check..."
❌ "Let me see..."
❌ "Hold on..."

⚠️ EXAMPLES:

❌ WRONG:
Candidate: "What question are we on?"
Agent: "Let me check... we're on question 2."

✅ CORRECT:
Candidate: "What question are we on?"
Agent: "We're on question 2 of 5."
[Called getCurrentQuestionNumber() silently]

❌ WRONG:
Candidate: "What's the first question?"
Agent: "Let me retrieve that..."

✅ CORRECT:
Candidate: "What's the first question?"
Agent: "Question 1 asks: Explain binary search and its time complexity."
[Looked up from memorized list instantly]

=== SMART INTERRUPTIONS ===

- 0-20 seconds: STAY SILENT (normal thinking)
- 20-25 seconds: "Take your time" (gentle nudge)
- 30+ seconds: "Would you like me to rephrase?" (active help)
- NEVER interrupt while they're actively speaking

=== AUDIO & PACING ===

- Enhanced noise reduction: {'Active' if enhanced_noise_reduction else 'Standard'}
- Speak clearly and at moderate pace
- Pause between question number and question text
- Be patient with technical difficulties

KEY POINTS:
"""
        
        # Add persona insights if available
        if 'insights' in persona and persona['insights']:
            for insight in persona['insights']:
                prompt += f"- {insight}\n"
        
        prompt += """
REMEMBER - YOUR SIMPLIFIED APPROACH:

✓ You have ALL questions memorized in your context
✓ Call getCurrentQuestionNumber() SILENTLY to know which number
✓ Look up that question from your memorized list
✓ Speak INSTANTLY - no "let me check" or "hold on"
✓ NEVER mention tools or any technical terms
✓ Be CONCISE - question number, question text, STOP
✓ PRESENT → LISTEN → MOVE cycle

🎯 CRITICAL MINDSET:
You are a professional interviewer with PERFECT MEMORY of all questions.
You just need to know which number you're on (via getCurrentQuestionNumber).
Then you instantly know what to ask from your memorized list.

Think like a human interviewer who memorized all questions:
- They don't say "let me check my notes"
- They just know: "Question 2 of 5: [text]"
- That's you. Instant. Professional. Confident.

✅ SIMPLIFIED FLOW:
1. Get current number (silent tool call)
2. Look up question from your list
3. Speak: "Question [N]: [text]"
4. Done!

You are a professional interviewer, not a chatty assistant. Be brief, clear, focused, and INSTANT."""
        
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
                # CONCISE first message - agent will elaborate based on prompt
                first_message = f"Hello! I'm {persona['name']}, and I'll be your interviewer today. Ready to begin?"
            else:
                first_message = f"Hello! I'm {persona['name']}. Ready to start your interview?"
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
