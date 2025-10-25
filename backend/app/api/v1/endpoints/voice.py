"""
Voice interaction endpoints for real-time audio processing and WebSocket communication.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from app.schemas.voice import (
    VoiceSessionStart, VoiceSessionResponse, VapiCallRequest, VapiCallResponse,
    WebSocketMessage, WebSocketMessageType, TranscriptionResult
)
try:
    from app.services.deepgram_service import DeepgramService
except Exception:
    DeepgramService = None  # type: ignore
try:
    from app.services.vapi_service import VapiService
except Exception:
    VapiService = None  # type: ignore
from app.core.auth import get_current_user
from app.schemas.user import UserResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Service instances
deepgram_service = DeepgramService() if DeepgramService else None
vapi_service = VapiService() if VapiService else None

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/stream/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time voice interaction with Deepgram.
    
    Args:
        websocket: WebSocket connection
        session_id: Session ID for the voice interaction
    """
    if not deepgram_service:
        await websocket.close()
        return
    await websocket.accept()
    active_connections[session_id] = websocket
    
    logger.info(f"WebSocket connection established for session: {session_id}")
    
    try:
        # TODO: DEEPGRAM - Set up live transcription
        config = VoiceSessionConfig()  # Use default config
        
        def on_transcript(transcript: TranscriptionResult):
            """Handle transcription results."""
            message = WebSocketMessage(
                type=WebSocketMessageType.TRANSCRIPTION,
                data={
                    "text": transcript.text,
                    "confidence": transcript.confidence,
                    "is_final": transcript.is_final,
                    "alternatives": transcript.alternatives
                },
                timestamp=transcript.timestamp,
                session_id=session_id
            )
            
            # Send transcription to client
            asyncio.create_task(
                websocket.send_text(json.dumps(message.dict()))
            )
        
        def on_error(error: str):
            """Handle transcription errors."""
            message = WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                data={"error": error},
                timestamp=transcript.timestamp,
                session_id=session_id
            )
            
            asyncio.create_task(
                websocket.send_text(json.dumps(message.dict()))
            )
        
        # Start live transcription
        await deepgram_service.start_live_transcription(
            f"ws://localhost:8000/voice/stream/{session_id}",
            config,
            on_transcript,
            on_error
        )
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_bytes()
                
                # Send audio data to Deepgram
                await deepgram_service.send_audio_chunk(
                    deepgram_service.connection,  # TODO: Fix connection reference
                    data
                )
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session: {session_id}")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        # Clean up connection
        if session_id in active_connections:
            del active_connections[session_id]


@router.post("/session/start", response_model=VoiceSessionResponse)
async def start_voice_session(
    session_data: VoiceSessionStart,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Start a new voice interaction session.
    
    Args:
        session_data: Voice session configuration
        current_user: Current authenticated user
        
    Returns:
        VoiceSessionResponse: Session information
    """
    try:
        # TODO: Implement session initialization
        session_id = f"session_{current_user.id}_{session_data.interview_id}"
        
        # Store session configuration
        # TODO: Store in database or cache
        
        response = VoiceSessionResponse(
            session_id=session_id,
            status="active",
            provider=session_data.config.provider,
            config=session_data.config,
            created_at="2024-01-01T00:00:00Z"  # TODO: Use actual timestamp
        )
        
        logger.info(f"Voice session started: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error starting voice session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start voice session")


@router.post("/vapi/call", response_model=VapiCallResponse)
async def create_vapi_call(
    call_request: VapiCallRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a Vapi phone call for voice interview.
    
    Args:
        call_request: Vapi call request parameters
        current_user: Current authenticated user
        
    Returns:
        VapiCallResponse: Call information
    """
    try:
        if not vapi_service:
            raise HTTPException(status_code=503, detail="Vapi not configured")
        # Create Vapi call
        call_response = await vapi_service.create_phone_call(call_request)
        
        if not call_response:
            raise HTTPException(status_code=500, detail="Failed to create Vapi call")
        
        logger.info(f"Vapi call created: {call_response.call_id}")
        return call_response
        
    except Exception as e:
        logger.error(f"Error creating Vapi call: {e}")
        raise HTTPException(status_code=500, detail="Failed to create Vapi call")


@router.get("/vapi/call/{call_id}/status")
async def get_vapi_call_status(
    call_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get status of a Vapi call.
    
    Args:
        call_id: Vapi call ID
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Call status information
    """
    try:
        if not vapi_service:
            raise HTTPException(status_code=503, detail="Vapi not configured")
        call_status = await vapi_service.get_call_status(call_id)
        
        if not call_status:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return call_status
        
    except Exception as e:
        logger.error(f"Error getting Vapi call status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get call status")


@router.post("/vapi/call/{call_id}/end")
async def end_vapi_call(
    call_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    End a Vapi call.
    
    Args:
        call_id: Vapi call ID
        current_user: Current authenticated user
        
    Returns:
        Dict[str, str]: Success message
    """
    try:
        if not vapi_service:
            raise HTTPException(status_code=503, detail="Vapi not configured")
        success = await vapi_service.end_call(call_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to end call")
        
        return {"message": "Call ended successfully"}
        
    except Exception as e:
        logger.error(f"Error ending Vapi call: {e}")
        raise HTTPException(status_code=500, detail="Failed to end call")


@router.get("/vapi/call/{call_id}/transcript")
async def get_vapi_call_transcript(
    call_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get transcript of a Vapi call.
    
    Args:
        call_id: Vapi call ID
        current_user: Current authenticated user
        
    Returns:
        Dict[str, str]: Call transcript
    """
    try:
        if not vapi_service:
            raise HTTPException(status_code=503, detail="Vapi not configured")
        transcript = await vapi_service.get_call_transcript(call_id)
        
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        return {"transcript": transcript}
        
    except Exception as e:
        logger.error(f"Error getting Vapi call transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transcript")


@router.get("/vapi/call/{call_id}/recording")
async def get_vapi_call_recording(
    call_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get recording URL of a Vapi call.
    
    Args:
        call_id: Vapi call ID
        current_user: Current authenticated user
        
    Returns:
        Dict[str, str]: Recording URL
    """
    try:
        if not vapi_service:
            raise HTTPException(status_code=503, detail="Vapi not configured")
        recording_url = await vapi_service.get_call_recording(call_id)
        
        if not recording_url:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        return {"recording_url": recording_url}
        
    except Exception as e:
        logger.error(f"Error getting Vapi call recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recording")


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages for voice processing.
    
    Returns:
        Dict[str, List[str]]: Supported languages
    """
    try:
        if not deepgram_service:
            raise HTTPException(status_code=503, detail="Deepgram not configured")
        languages = await deepgram_service.get_supported_languages()
        return {"languages": languages}
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported languages")


@router.get("/supported-models")
async def get_supported_models():
    """
    Get list of supported models for voice processing.
    
    Returns:
        Dict[str, List[str]]: Supported models
    """
    try:
        if not deepgram_service:
            raise HTTPException(status_code=503, detail="Deepgram not configured")
        models = await deepgram_service.get_supported_models()
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Error getting supported models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported models")
