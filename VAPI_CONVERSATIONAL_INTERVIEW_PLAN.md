# VAPI Conversational Interview Integration Plan - Hackathon Day

## Overview
This document outlines the implementation of VAPI (Voice AI Platform) to create a seamless, conversational interview experience with natural topic transitions and minimal human intervention.

## Current State vs Desired State

### Current State ❌
- Manual question-by-question flow
- Separate API calls for each question
- Choppy transitions between questions
- User manually navigates to next question
- Disconnected Q&A experience

### Desired State ✅
- Continuous conversational flow
- AI handles all transitions automatically
- Natural topic progression with filler text
- Timer-based smooth transitions
- User only intervenes to end questions early
- Seamless, human-like interview experience

## Hackathon Day Tasks

### 1. VAPI Setup and Configuration

#### 1.1 VAPI Account and API Setup
**Priority: HIGH**
- **Task**: Set up VAPI account and obtain API credentials
- **Requirements**:
  - VAPI API key
  - Webhook endpoints for conversation events
  - Voice model configuration
  - Conversation flow templates

#### 1.2 VAPI Integration Service
**Priority: HIGH**
- **Task**: Create VAPI service for interview management
- **Location**: `backend/app/services/vapi_service.py`
- **Implementation**:
  ```python
  import requests
  from typing import Dict, Any, Optional
  
  class VAPIService:
      def __init__(self):
          self.api_key = os.getenv("VAPI_API_KEY")
          self.base_url = "https://api.vapi.ai"
          self.webhook_url = os.getenv("VAPI_WEBHOOK_URL")
      
      async def create_interview_call(self, interview_data: Dict[str, Any]) -> str:
          """Create a new VAPI call for interview"""
          payload = {
              "assistant": {
                  "model": {
                      "provider": "openai",
                      "model": "gpt-4",
                      "systemMessage": self._build_system_message(interview_data),
                      "temperature": 0.7
                  },
                  "voice": {
                      "provider": "elevenlabs",
                      "voiceId": "rachel"  # Professional female voice
                  },
                  "firstMessage": self._build_opening_message(interview_data),
                  "endCallMessage": "Thank you for the interview. We'll be in touch soon.",
                  "endCallPhrases": ["end interview", "stop interview", "that's all"],
                  "recordingEnabled": True,
                  "backgroundSound": "office"
              },
              "customer": {
                  "number": "+1234567890"  # User's phone number or web call
              },
              "webhookUrl": self.webhook_url
          }
          
          response = requests.post(
              f"{self.base_url}/call",
              headers={"Authorization": f"Bearer {self.api_key}"},
              json=payload
          )
          
          return response.json()["id"]
  ```

#### 1.3 Interview Context Builder
**Priority: HIGH**
- **Task**: Build system message with interview context
- **Location**: `backend/app/services/vapi_service.py`
- **Implementation**:
  ```python
  def _build_system_message(self, interview_data: Dict[str, Any]) -> str:
      return f"""
      You are a professional AI interviewer conducting a {interview_data['interview_type']} interview.
      
      Job Details:
      - Position: {interview_data['position_title']}
      - Company: {interview_data['company_name']}
      - Job Description: {interview_data['job_description']}
      
      Interview Focus Areas: {', '.join(interview_data['focus_areas'])}
      Difficulty Level: {interview_data['difficulty_level']}
      
      Interview Structure:
      1. Opening and Introduction (2 minutes)
      2. Technical Questions (15 minutes)
      3. Behavioral Questions (10 minutes)
      4. Company-specific Questions (8 minutes)
      5. Candidate Questions (5 minutes)
      
      Guidelines:
      - Be professional, friendly, and engaging
      - Ask follow-up questions to probe deeper
      - Transition smoothly between topics using natural language
      - Monitor time and transition when appropriate
      - Use phrases like "Let's move on to..." or "That's interesting, now let's discuss..."
      - If candidate wants to end early, acknowledge and move on
      - Maintain conversational flow throughout
      
      Transition Phrases:
      - "That's a great point. Let's explore another aspect..."
      - "I'd like to shift gears and talk about..."
      - "Moving on from that topic, let's discuss..."
      - "That's helpful context. Now, regarding..."
      """
  ```

### 2. Webhook Integration

#### 2.1 VAPI Webhook Handler
**Priority: HIGH**
- **Task**: Create webhook endpoint to handle VAPI events
- **Location**: `backend/app/api/v1/endpoints/vapi.py`
- **Implementation**:
  ```python
  from fastapi import APIRouter, Request, HTTPException
  from pydantic import BaseModel
  
  router = APIRouter()
  
  class VAPIWebhookEvent(BaseModel):
      type: str
      call: Dict[str, Any]
      message: Optional[Dict[str, Any]] = None
  
  @router.post("/webhook")
  async def handle_vapi_webhook(request: Request):
      """Handle VAPI webhook events"""
      try:
          event = await request.json()
          event_type = event.get("type")
          
          if event_type == "call-started":
              await handle_call_started(event)
          elif event_type == "call-ended":
              await handle_call_ended(event)
          elif event_type == "message":
              await handle_message(event)
          elif event_type == "function-call":
              await handle_function_call(event)
          
          return {"status": "success"}
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  
  async def handle_call_started(event: Dict[str, Any]):
      """Handle call started event"""
      call_id = event["call"]["id"]
      # Update interview status in database
      # Start timer for interview session
  
  async def handle_call_ended(event: Dict[str, Any]):
      """Handle call ended event"""
      call_id = event["call"]["id"]
      # Process interview completion
      # Generate final analysis
      # Store results in ChromaDB
  ```

#### 2.2 Real-time Event Processing
**Priority: MEDIUM**
- **Task**: Process real-time conversation events
- **Implementation**:
  ```python
  async def handle_message(event: Dict[str, Any]):
      """Handle conversation messages"""
      call_id = event["call"]["id"]
      message = event["message"]
      
      if message["role"] == "user":
          # Store user response in ChromaDB
          await store_user_response(call_id, message["content"])
      elif message["role"] == "assistant":
          # Track AI questions and transitions
          await track_ai_message(call_id, message["content"])
  ```

### 3. Frontend Integration

#### 3.1 VAPI Call Interface
**Priority: HIGH**
- **Task**: Create frontend interface for VAPI calls
- **Location**: `frontend/src/pages/InterviewSession.tsx`
- **Implementation**:
  ```typescript
  import { useState, useEffect, useRef } from 'react';
  
  const VAPIInterviewSession = () => {
    const [callStatus, setCallStatus] = useState<'idle' | 'connecting' | 'active' | 'ended'>('idle');
    const [callId, setCallId] = useState<string | null>(null);
    const [transcript, setTranscript] = useState<string[]>([]);
    const [currentTopic, setCurrentTopic] = useState<string>('');
    const [timeRemaining, setTimeRemaining] = useState<number>(0);
    
    const startVAPICall = async () => {
      setCallStatus('connecting');
      
      const response = await fetch('/api/v1/interviews/start-vapi-call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          interview_id: interviewId,
          user_phone: userPhone // or web call setup
        })
      });
      
      const data = await response.json();
      setCallId(data.call_id);
      setCallStatus('active');
    };
    
    const endCallEarly = async () => {
      if (callId) {
        await fetch(`/api/v1/vapi/calls/${callId}/end`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
      }
    };
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white/30 backdrop-blur-md border border-white/30 rounded-2xl shadow-xl p-8">
            
            {/* Call Status */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-4">
                {callStatus === 'idle' && 'Ready to Start Interview'}
                {callStatus === 'connecting' && 'Connecting...'}
                {callStatus === 'active' && 'Interview in Progress'}
                {callStatus === 'ended' && 'Interview Completed'}
              </h1>
              
              {callStatus === 'active' && (
                <div className="flex justify-center items-center space-x-4 mb-4">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="text-lg font-medium">Live Interview</span>
                </div>
              )}
            </div>
            
            {/* Current Topic Display */}
            {currentTopic && (
              <div className="bg-lime-500/20 backdrop-blur-sm border border-lime-400/50 rounded-xl p-4 mb-6">
                <h3 className="text-lg font-semibold text-lime-800 mb-2">Current Topic</h3>
                <p className="text-lime-700">{currentTopic}</p>
              </div>
            )}
            
            {/* Timer Display */}
            {timeRemaining > 0 && (
              <div className="text-center mb-6">
                <div className="text-2xl font-bold text-gray-800">
                  {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}
                </div>
                <p className="text-sm text-gray-600">Time remaining for current topic</p>
              </div>
            )}
            
            {/* Live Transcript */}
            {transcript.length > 0 && (
              <div className="bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Live Transcript</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {transcript.map((message, index) => (
                    <div key={index} className={`p-3 rounded-lg ${
                      message.role === 'user' 
                        ? 'bg-lime-500/20 text-lime-800 ml-8' 
                        : 'bg-sky-500/20 text-sky-800 mr-8'
                    }`}>
                      <div className="font-medium text-xs mb-1">
                        {message.role === 'user' ? 'You' : 'Interviewer'}
                      </div>
                      <div>{message.content}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Controls */}
            <div className="flex justify-center space-x-4">
              {callStatus === 'idle' && (
                <button
                  onClick={startVAPICall}
                  className="bg-lime-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-lime-700 transition-colors"
                >
                  Start Interview
                </button>
              )}
              
              {callStatus === 'active' && (
                <button
                  onClick={endCallEarly}
                  className="bg-red-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-red-700 transition-colors"
                >
                  End Question Early
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };
  ```

#### 3.2 Real-time Updates
**Priority: MEDIUM**
- **Task**: Implement real-time updates for transcript and status
- **Implementation**:
  ```typescript
  useEffect(() => {
    if (callId) {
      const eventSource = new EventSource(`/api/v1/vapi/calls/${callId}/events`);
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'transcript_update':
            setTranscript(data.transcript);
            break;
          case 'topic_change':
            setCurrentTopic(data.topic);
            break;
          case 'timer_update':
            setTimeRemaining(data.timeRemaining);
            break;
          case 'call_ended':
            setCallStatus('ended');
            eventSource.close();
            break;
        }
      };
      
      return () => eventSource.close();
    }
  }, [callId]);
  ```

### 4. Interview Flow Management

#### 4.1 Dynamic Topic Transitions
**Priority: HIGH**
- **Task**: Implement smooth topic transitions with natural language
- **Location**: `backend/app/services/vapi_service.py`
- **Implementation**:
  ```python
  class InterviewFlowManager:
      def __init__(self):
          self.current_topic = "introduction"
          self.topic_timers = {
              "introduction": 120,  # 2 minutes
              "technical": 900,     # 15 minutes
              "behavioral": 600,    # 10 minutes
              "company": 480,       # 8 minutes
              "questions": 300      # 5 minutes
          }
          self.transition_phrases = [
              "That's very insightful. Let's move on to discuss your technical background...",
              "Great perspective on that. Now, I'd like to explore your experience with...",
              "That's helpful context. Shifting gears, let's talk about...",
              "Excellent point. Moving forward, I'm curious about your approach to...",
              "That's a solid foundation. Now, regarding your experience with..."
          ]
      
      def get_transition_phrase(self, from_topic: str, to_topic: str) -> str:
          """Get natural transition phrase between topics"""
          return random.choice(self.transition_phrases)
      
      def should_transition(self, current_time: int, topic: str) -> bool:
          """Check if it's time to transition to next topic"""
          return current_time >= self.topic_timers.get(topic, 0)
  ```

#### 4.2 Context-Aware Question Generation
**Priority: MEDIUM**
- **Task**: Generate follow-up questions based on user responses
- **Implementation**:
  ```python
  def generate_follow_up_question(self, user_response: str, current_topic: str) -> str:
      """Generate contextual follow-up questions"""
      # Use Groq to analyze response and generate follow-up
      prompt = f"""
      Based on this response about {current_topic}: "{user_response}"
      
      Generate a natural follow-up question that:
      1. Probes deeper into their answer
      2. Asks for specific examples
      3. Explores related aspects
      4. Maintains conversational flow
      
      Keep it natural and professional.
      """
      
      # Call Groq service to generate follow-up
      return self.groq_service.generate_follow_up(prompt)
  ```

### 5. Integration with Existing Systems

#### 5.1 ChromaDB Integration
**Priority: HIGH**
- **Task**: Store conversation data in ChromaDB for analysis
- **Implementation**:
  ```python
  async def store_conversation_segment(self, call_id: str, segment: Dict[str, Any]):
      """Store conversation segment in ChromaDB"""
      await self.chroma_service.add_interview_response(
          interview_id=call_id,
          question_id=segment["question_id"],
          response_text=segment["user_response"],
          metadata={
              "topic": segment["topic"],
              "timestamp": segment["timestamp"],
              "follow_up_count": segment["follow_up_count"],
              "ai_question": segment["ai_question"]
          }
      )
  ```

#### 5.2 Interview Analytics
**Priority: MEDIUM**
- **Task**: Generate real-time analytics during conversation
- **Implementation**:
  ```python
  class InterviewAnalytics:
      def __init__(self):
          self.response_quality_scores = []
          self.topic_coverage = {}
          self.follow_up_effectiveness = {}
      
      def analyze_response_quality(self, response: str) -> float:
          """Analyze response quality using ChromaDB similarity"""
          # Compare with best practices
          similar_responses = self.chroma_service.search_similar_responses(
              query=response,
              filter_metadata={"response_type": "best_practice"}
          )
          
          if similar_responses:
              return similar_responses[0]["distance"]
          return 0.5
      
      def generate_real_time_feedback(self, call_id: str) -> Dict[str, Any]:
          """Generate real-time feedback for the interview"""
          return {
              "overall_score": self.calculate_overall_score(),
              "strengths": self.identify_strengths(),
              "areas_for_improvement": self.identify_improvements(),
              "topic_coverage": self.topic_coverage
          }
  ```

### 6. Error Handling and Fallbacks

#### 6.1 VAPI Connection Issues
**Priority: HIGH**
- **Task**: Handle VAPI service interruptions gracefully
- **Implementation**:
  ```python
  class VAPIFallbackManager:
      def __init__(self):
          self.fallback_mode = False
          self.local_questions = []
      
      async def handle_vapi_failure(self, interview_data: Dict[str, Any]):
          """Fallback to local question system if VAPI fails"""
          self.fallback_mode = True
          # Generate questions using Groq
          self.local_questions = await self.groq_service.generate_questions(interview_data)
          # Switch to manual interview mode
          return "fallback_mode"
  ```

#### 6.2 Audio Quality Issues
**Priority: MEDIUM**
- **Task**: Handle poor audio quality or connection issues
- **Implementation**:
  ```python
  def handle_audio_issues(self, call_id: str, issue_type: str):
      """Handle various audio quality issues"""
      if issue_type == "poor_quality":
          # Adjust VAPI settings
          self.adjust_audio_settings(call_id, "high_quality")
      elif issue_type == "connection_lost":
          # Attempt reconnection
          self.reconnect_call(call_id)
      elif issue_type == "background_noise":
          # Enable noise cancellation
          self.enable_noise_cancellation(call_id)
  ```

## Implementation Priority Order

### Day 1 (Morning)
1. **VAPI Setup** - Account setup and basic integration
2. **Webhook Handler** - Create webhook endpoint for VAPI events
3. **Basic Call Interface** - Frontend interface for starting calls

### Day 1 (Afternoon)
4. **Interview Flow Manager** - Topic transitions and timing
5. **ChromaDB Integration** - Store conversation data
6. **Error Handling** - Fallback mechanisms

### Day 2 (If Time Permits)
7. **Real-time Analytics** - Live feedback and scoring
8. **Advanced Features** - Follow-up questions, context awareness
9. **Performance Optimization** - Audio quality, connection stability

## Technical Requirements

### VAPI Configuration
- **Voice Model**: Professional interviewer voice (ElevenLabs)
- **AI Model**: GPT-4 for conversation management
- **Recording**: Enabled for analysis
- **Background**: Office environment sounds

### Environment Variables
```env
VAPI_API_KEY=your_vapi_api_key
VAPI_WEBHOOK_URL=https://your-domain.com/api/v1/vapi/webhook
VAPI_ASSISTANT_ID=your_assistant_id
```

### Dependencies
```json
{
  "dependencies": {
    "vapi-ai": "^1.0.0",
    "socket.io-client": "^4.7.0"
  }
}
```

## Success Metrics

### Technical Metrics
- Call connection success rate: >95%
- Audio quality score: >4.0/5.0
- Transition smoothness: <2 second gaps
- Real-time processing latency: <500ms

### User Experience Metrics
- Interview completion rate: >90%
- User satisfaction with flow: >4.5/5.0
- Natural conversation rating: >4.0/5.0
- Transition awareness: <10% notice transitions

## Troubleshooting Guide

### Common Issues
1. **VAPI Connection Failed**: Check API key, network connectivity
2. **Poor Audio Quality**: Adjust VAPI settings, check user's microphone
3. **Webhook Not Receiving Events**: Verify webhook URL, SSL certificate
4. **Transitions Too Abrupt**: Adjust transition phrases, timing

### Debug Commands
```bash
# Test VAPI connection
curl -H "Authorization: Bearer $VAPI_API_KEY" https://api.vapi.ai/assistant

# Check webhook endpoint
curl -X POST https://your-domain.com/api/v1/vapi/webhook -d '{"test": true}'

# Monitor call status
curl -H "Authorization: Bearer $VAPI_API_KEY" https://api.vapi.ai/call/{call_id}
```

## Resources

### Documentation
- [VAPI Documentation](https://docs.vapi.ai/)
- [VAPI Webhooks](https://docs.vapi.ai/webhooks)
- [VAPI Assistants](https://docs.vapi.ai/assistants)

### Code References
- `backend/app/services/vapi_service.py` - VAPI integration
- `backend/app/api/v1/endpoints/vapi.py` - Webhook handlers
- `frontend/src/pages/InterviewSession.tsx` - Frontend interface

## Notes for Hackathon Day

### Quick Start Checklist
- [ ] Set up VAPI account and get API key
- [ ] Configure webhook endpoint
- [ ] Test basic call functionality
- [ ] Verify audio quality
- [ ] Test topic transitions

### Emergency Fallbacks
- If VAPI fails, fallback to manual interview mode
- If audio issues, provide text-based interview
- If webhook fails, use polling for updates
- If transitions fail, use manual navigation

### Demo Preparation
- Prepare test phone numbers for VAPI calls
- Test on different devices and browsers
- Prepare demo scenarios for different interview types
- Test transition phrases and timing

---

**Last Updated**: October 23, 2024
**Status**: Ready for Hackathon Implementation
**Next Review**: Hackathon Day Morning
