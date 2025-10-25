"""
Deepgram service for real-time speech-to-text transcription via WebSocket.
"""
import asyncio
import json
import websockets
from typing import Optional, Callable, Dict, Any
import deepgram
from app.core.config import settings
from app.schemas.voice import TranscriptionResult, VoiceSessionConfig, AudioFormat
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DeepgramService:
    """Service for Deepgram speech-to-text operations."""
    
    def __init__(self):
        """Initialize Deepgram client."""
        if settings.DEEPGRAM_API_KEY:
            self.client = deepgram.DeepgramClient(settings.DEEPGRAM_API_KEY)
        else:
            logger.warning("Deepgram API key not configured")
            self.client = None
    
    async def transcribe_audio_file(
        self,
        audio_file_path: str,
        config: VoiceSessionConfig
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe audio file using Deepgram.
        
        Args:
            audio_file_path: Path to audio file
            config: Voice session configuration
            
        Returns:
            TranscriptionResult: Transcription result or None if failed
        """
        if not self.client:
            logger.error("Deepgram client not initialized")
            return None
        
        try:
            # TODO: DEEPGRAM - Implement file transcription
            with open(audio_file_path, 'rb') as audio:
                buffer_data = audio.read()
            
            payload = {'buffer': buffer_data}
            
            response = self.client.listen.prerecorded.v('1').transcribe_file(
                payload,
                {
                    "model": config.model,
                    "language": config.language,
                    "smart_format": config.enable_smart_format,
                    "utterance_endpoint": config.enable_utterance_endpoint,
                    "sentiment": config.enable_sentiment_analysis
                }
            )
            
            if response.results and response.results.channels:
                channel = response.results.channels[0]
                if channel.alternatives:
                    alternative = channel.alternatives[0]
                    
                    return TranscriptionResult(
                        text=alternative.transcript,
                        confidence=alternative.confidence,
                        is_final=True,
                        alternatives=[alt.transcript for alt in channel.alternatives[1:]],
                        timestamp=response.metadata.created,
                        duration=response.metadata.duration
                    )
            
            logger.error("No transcription results found")
            return None
            
        except Exception as e:
            logger.error(f"Error transcribing audio file: {e}")
            return None
    
    async def start_live_transcription(
        self,
        websocket_url: str,
        config: VoiceSessionConfig,
        on_transcript: Callable[[TranscriptionResult], None],
        on_error: Callable[[str], None]
    ) -> None:
        """
        Start live transcription via WebSocket.
        
        Args:
            websocket_url: WebSocket URL for real-time audio
            config: Voice session configuration
            on_transcript: Callback for transcription results
            on_error: Callback for errors
        """
        if not self.client:
            logger.error("Deepgram client not initialized")
            on_error("Deepgram client not initialized")
            return
        
        try:
            # TODO: DEEPGRAM - Implement live transcription
            connection = self.client.listen.live.v('1')
            
            # Configure connection
            connection.configure({
                "model": config.model,
                "language": config.language,
                "smart_format": config.enable_smart_format,
                "utterance_endpoint": config.enable_utterance_endpoint,
                "sentiment": config.enable_sentiment_analysis,
                "interim_results": True
            })
            
            # Set up event handlers
            connection.on_open = self._on_open
            connection.on_message = lambda *args: self._on_message(*args, on_transcript)
            connection.on_error = lambda *args: self._on_error(*args, on_error)
            connection.on_close = self._on_close
            
            # Start connection
            if connection.start():
                logger.info("Deepgram live transcription started")
                
                # Keep connection alive
                while True:
                    await asyncio.sleep(1)
            else:
                logger.error("Failed to start Deepgram live transcription")
                on_error("Failed to start live transcription")
                
        except Exception as e:
            logger.error(f"Error starting live transcription: {e}")
            on_error(f"Error starting live transcription: {e}")
    
    async def send_audio_chunk(
        self,
        connection,
        audio_data: bytes
    ) -> None:
        """
        Send audio chunk to live transcription.
        
        Args:
            connection: Deepgram connection
            audio_data: Audio data bytes
        """
        try:
            if connection and connection.is_open():
                connection.send(audio_data)
            else:
                logger.warning("Deepgram connection not open")
        except Exception as e:
            logger.error(f"Error sending audio chunk: {e}")
    
    def _on_open(self, *args):
        """Handle connection open event."""
        logger.info("Deepgram WebSocket connection opened")
    
    def _on_message(self, *args, on_transcript: Callable[[TranscriptionResult], None]):
        """Handle transcription message."""
        try:
            message = args[0]
            if isinstance(message, str):
                data = json.loads(message)
                
                if 'channel' in data and 'alternatives' in data['channel']:
                    alternatives = data['channel']['alternatives']
                    if alternatives:
                        alternative = alternatives[0]
                        
                        transcript_result = TranscriptionResult(
                            text=alternative.get('transcript', ''),
                            confidence=alternative.get('confidence', 0.0),
                            is_final=data.get('is_final', False),
                            alternatives=[alt.get('transcript', '') for alt in alternatives[1:]],
                            timestamp=data.get('start', 0.0),
                            duration=data.get('duration', 0.0)
                        )
                        
                        on_transcript(transcript_result)
                        
        except Exception as e:
            logger.error(f"Error processing transcription message: {e}")
    
    def _on_error(self, *args, on_error: Callable[[str], None]):
        """Handle connection error."""
        error_msg = f"Deepgram WebSocket error: {args[0] if args else 'Unknown error'}"
        logger.error(error_msg)
        on_error(error_msg)
    
    def _on_close(self, *args):
        """Handle connection close."""
        logger.info("Deepgram WebSocket connection closed")
    
    async def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            list: List of supported language codes
        """
        # TODO: DEEPGRAM - Implement language list retrieval
        return [
            "en-US", "en-GB", "en-AU", "en-IN",
            "es-ES", "es-MX", "fr-FR", "de-DE",
            "it-IT", "pt-BR", "ja-JP", "ko-KR",
            "zh-CN", "zh-TW", "ru-RU", "ar-SA"
        ]
    
    async def get_supported_models(self) -> list:
        """
        Get list of supported models.
        
        Returns:
            list: List of supported model names
        """
        # TODO: DEEPGRAM - Implement model list retrieval
        return [
            "nova-2", "nova", "enhanced", "base",
            "meeting", "phonecall", "voicemail"
        ]
