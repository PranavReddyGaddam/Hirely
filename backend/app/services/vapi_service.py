"""
Vapi service for voice AI integration and phone call management.
"""
import asyncio
import httpx
from typing import Optional, Dict, Any, Callable
from app.core.config import settings
from app.schemas.voice import VapiCallRequest, VapiCallResponse, VoiceSessionConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VapiService:
    """Service for Vapi voice AI operations."""
    
    def __init__(self):
        """Initialize Vapi service."""
        self.api_key = settings.VAPI_API_KEY
        self.base_url = "https://api.vapi.ai"
        self.phone_number = settings.VAPI_PHONE_NUMBER
        
        if not self.api_key:
            logger.warning("Vapi API key not configured")
    
    async def create_phone_call(
        self,
        call_request: VapiCallRequest,
        assistant_config: Optional[Dict[str, Any]] = None
    ) -> Optional[VapiCallResponse]:
        """
        Create a phone call using Vapi.
        
        Args:
            call_request: Call request parameters
            assistant_config: Optional assistant configuration
            
        Returns:
            VapiCallResponse: Call response or None if failed
        """
        if not self.api_key:
            logger.error("Vapi API key not configured")
            return None
        
        try:
            # TODO: VAPI - Implement phone call creation
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "phoneNumberId": self.phone_number,
                "customer": {
                    "number": call_request.phone_number
                },
                "assistantId": call_request.assistant_id,
                "assistantOverrides": call_request.custom_config or {}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/call",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return VapiCallResponse(
                        call_id=data.get("id", ""),
                        status=data.get("status", ""),
                        phone_number=call_request.phone_number,
                        created_at=data.get("createdAt", "")
                    )
                else:
                    logger.error(f"Vapi call creation failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating Vapi phone call: {e}")
            return None
    
    async def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a phone call.
        
        Args:
            call_id: Call ID to check
            
        Returns:
            Dict[str, Any]: Call status data or None if failed
        """
        if not self.api_key:
            logger.error("Vapi API key not configured")
            return None
        
        try:
            # TODO: VAPI - Implement call status retrieval
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/call/{call_id}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Vapi call status retrieval failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting Vapi call status: {e}")
            return None
    
    async def end_call(self, call_id: str) -> bool:
        """
        End an active phone call.
        
        Args:
            call_id: Call ID to end
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_key:
            logger.error("Vapi API key not configured")
            return False
        
        try:
            # TODO: VAPI - Implement call termination
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/call/{call_id}/end",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Vapi call {call_id} ended successfully")
                    return True
                else:
                    logger.error(f"Vapi call end failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error ending Vapi call: {e}")
            return False
    
    async def create_assistant(
        self,
        name: str,
        description: str,
        interview_config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a Vapi assistant for interview sessions.
        
        Args:
            name: Assistant name
            description: Assistant description
            interview_config: Interview-specific configuration
            
        Returns:
            str: Assistant ID or None if failed
        """
        if not self.api_key:
            logger.error("Vapi API key not configured")
            return None
        
        try:
            # TODO: VAPI - Implement assistant creation
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": name,
                "description": description,
                "model": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are an AI interviewer conducting a {interview_config.get('type', 'mock')} interview. {description}"
                        }
                    ]
                },
                "voice": {
                    "provider": "elevenlabs",
                    "voiceId": "21m00Tcm4TlvDq8ikWAM"
                },
                "firstMessage": "Hello! I'm your AI interviewer. Are you ready to begin the interview?",
                "endCallMessage": "Thank you for the interview. Have a great day!",
                "endCallPhrases": ["goodbye", "end interview", "that's all"],
                "recordingEnabled": True,
                "transcriptionEnabled": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/assistant",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assistant_id = data.get("id", "")
                    logger.info(f"Created Vapi assistant: {assistant_id}")
                    return assistant_id
                else:
                    logger.error(f"Vapi assistant creation failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating Vapi assistant: {e}")
            return None
    
    async def get_call_transcript(self, call_id: str) -> Optional[str]:
        """
        Get transcript of a completed call.
        
        Args:
            call_id: Call ID to get transcript for
            
        Returns:
            str: Call transcript or None if failed
        """
        if not self.api_key:
            logger.error("Vapi API key not configured")
            return None
        
        try:
            # TODO: VAPI - Implement transcript retrieval
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/call/{call_id}/transcript",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("transcript", "")
                else:
                    logger.error(f"Vapi transcript retrieval failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting Vapi call transcript: {e}")
            return None
    
    async def get_call_recording(self, call_id: str) -> Optional[str]:
        """
        Get recording URL of a completed call.
        
        Args:
            call_id: Call ID to get recording for
            
        Returns:
            str: Recording URL or None if failed
        """
        if not self.api_key:
            logger.error("Vapi API key not configured")
            return None
        
        try:
            # TODO: VAPI - Implement recording URL retrieval
            call_status = await self.get_call_status(call_id)
            
            if call_status:
                return call_status.get("recordingUrl", "")
            
            return None
                    
        except Exception as e:
            logger.error(f"Error getting Vapi call recording: {e}")
            return None
    
    async def setup_webhook(self, webhook_url: str) -> bool:
        """
        Set up webhook for call events.
        
        Args:
            webhook_url: Webhook URL to receive events
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_key:
            logger.error("Vapi API key not configured")
            return False
        
        try:
            # TODO: VAPI - Implement webhook setup
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": webhook_url,
                "events": ["call-started", "call-ended", "transcript", "recording-ready"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/webhook",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Vapi webhook set up successfully: {webhook_url}")
                    return True
                else:
                    logger.error(f"Vapi webhook setup failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error setting up Vapi webhook: {e}")
            return False
