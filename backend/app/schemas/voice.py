"""
Voice interaction schemas for real-time audio processing and WebSocket communication.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class VoiceProvider(str, Enum):
    """Voice processing provider enumeration."""
    DEEPGRAM = "deepgram"
    VAPI = "vapi"
    OPENAI_WHISPER = "openai_whisper"


class AudioFormat(str, Enum):
    """Audio format enumeration."""
    WAV = "wav"
    MP3 = "mp3"
    WEBM = "webm"
    M4A = "m4a"


class WebSocketMessageType(str, Enum):
    """WebSocket message type enumeration."""
    AUDIO_CHUNK = "audio_chunk"
    TRANSCRIPTION = "transcription"
    QUESTION = "question"
    RESPONSE = "response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    SESSION_START = "session_start"
    SESSION_END = "session_end"


class AudioChunk(BaseModel):
    """Schema for audio data chunks."""
    data: bytes
    format: AudioFormat
    sample_rate: int = 16000
    channels: int = 1
    timestamp: datetime


class TranscriptionResult(BaseModel):
    """Schema for speech-to-text transcription results."""
    text: str
    confidence: float
    is_final: bool
    alternatives: List[str] = []
    timestamp: datetime
    duration: float


class VoiceSessionConfig(BaseModel):
    """Schema for voice session configuration."""
    provider: VoiceProvider = VoiceProvider.DEEPGRAM
    language: str = "en-US"
    model: str = "nova-2"
    enable_smart_format: bool = True
    enable_utterance_endpoint: bool = True
    enable_sentiment_analysis: bool = True


class WebSocketMessage(BaseModel):
    """Schema for WebSocket communication messages."""
    type: WebSocketMessageType
    data: Dict[str, Any]
    timestamp: datetime
    session_id: Optional[str] = None


class VoiceSessionStart(BaseModel):
    """Schema for starting a voice session."""
    interview_id: str
    config: VoiceSessionConfig
    user_id: str


class VoiceSessionResponse(BaseModel):
    """Schema for voice session responses."""
    session_id: str
    status: str
    provider: VoiceProvider
    config: VoiceSessionConfig
    created_at: datetime


class VapiCallRequest(BaseModel):
    """Schema for Vapi voice AI call requests."""
    interview_id: str
    phone_number: str
    assistant_id: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class VapiCallResponse(BaseModel):
    """Schema for Vapi call responses."""
    call_id: str
    status: str
    phone_number: str
    created_at: datetime
    # TODO: Add Vapi-specific response fields


class VoiceAnalysisRequest(BaseModel):
    """Schema for requesting voice analysis."""
    audio_data: bytes
    format: AudioFormat
    analysis_type: str = "comprehensive"  # transcription, sentiment, emotion
    language: str = "en-US"


class VoiceAnalysisResult(BaseModel):
    """Schema for voice analysis results."""
    transcription: Optional[TranscriptionResult] = None
    sentiment: Optional[Dict[str, float]] = None
    emotions: Optional[Dict[str, float]] = None
    speaking_rate: Optional[float] = None
    confidence_score: Optional[float] = None
    processing_time: float
