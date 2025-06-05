"""
ElevenLabs Text-to-Speech Implementation

Provides high-quality text-to-speech using ElevenLabs API with WebSocket streaming
for minimal latency voice generation.
"""

import asyncio
import json
import logging
import websockets
import base64
from typing import AsyncGenerator, Optional, Dict, Any
from io import BytesIO
import os

from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

logger = logging.getLogger(__name__)


class ElevenLabsTTS:
    """
    ElevenLabs Text-to-Speech with WebSocket streaming support.
    
    Supports both standard API and multi-context WebSocket for real-time streaming.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel voice (default)
        model_id: str = "eleven_flash_v2_5",  # Fastest model for low latency
        stability: float = 0.5,
        similarity_boost: float = 0.8,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ):
        """
        Initialize ElevenLabs TTS.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice to use for TTS
            model_id: Model to use (eleven_flash_v2_5 for speed)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)
            style: Voice style (0.0-1.0)
            use_speaker_boost: Whether to use speaker boost
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")
        
        # Configure ElevenLabs client using the new client-based approach
        self.client = ElevenLabs(api_key=self.api_key)
        
        self.voice_id = voice_id
        self.model_id = model_id
        self.voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost
        )
        
        # WebSocket configuration
        self.ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input"
        self.ws_params = {
            "model_id": model_id,
            "output_format": "mp3_44100_128",
            "enable_logging": "false",
            "auto_mode": "true",  # Reduces latency
            "apply_text_normalization": "auto"
        }

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to speech using standard API.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        try:
            logger.debug(f"Synthesizing text: {text[:50]}...")
            
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                voice_settings=self.voice_settings,
                output_format="mp3_44100_128"
            )
            
            # Convert generator to bytes if needed
            if hasattr(audio, '__iter__') and not isinstance(audio, (bytes, str)):
                audio_bytes = b''.join(audio)
            else:
                audio_bytes = audio
            
            logger.debug(f"Successfully synthesized {len(audio_bytes)} bytes of audio")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise

    async def stream_synthesize(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Stream synthesize text to speech using WebSocket for minimal latency.
        
        Args:
            text: Text to synthesize
            
        Yields:
            Audio chunks as bytes
        """
        try:
            logger.debug(f"Stream synthesizing text: {text[:50]}...")
            
            # Build WebSocket URL with parameters
            params = "&".join([f"{k}={v}" for k, v in self.ws_params.items()])
            ws_url = f"{self.ws_url}?{params}"
            
            headers = {"xi-api-key": self.api_key}
            
            async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                # Initialize connection
                init_message = {
                    "text": " ",
                    "voice_settings": {
                        "stability": self.voice_settings.stability,
                        "similarity_boost": self.voice_settings.similarity_boost,
                        "style": self.voice_settings.style,
                        "use_speaker_boost": self.voice_settings.use_speaker_boost
                    },
                    "generation_config": {
                        "chunk_length_schedule": [120, 160, 250, 290]
                    }
                }
                
                await websocket.send(json.dumps(init_message))
                
                # Send text for synthesis
                text_message = {
                    "text": text,
                    "try_trigger_generation": True
                }
                await websocket.send(json.dumps(text_message))
                
                # Send end of stream
                eos_message = {
                    "text": ""
                }
                await websocket.send(json.dumps(eos_message))
                
                # Receive audio chunks
                total_chunks = 0
                while True:
                    try:
                        response = await websocket.recv()
                        data = json.loads(response)
                        
                        if "audio" in data:
                            audio_chunk = base64.b64decode(data["audio"])
                            total_chunks += 1
                            logger.debug(f"Received audio chunk {total_chunks}: {len(audio_chunk)} bytes")
                            yield audio_chunk
                        
                        if data.get("isFinal", False):
                            logger.debug(f"Stream synthesis complete. Total chunks: {total_chunks}")
                            break
                            
                    except websockets.exceptions.ConnectionClosed:
                        logger.debug("WebSocket connection closed")
                        break
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to decode WebSocket response: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in stream synthesis: {e}")
            # Fallback to standard synthesis
            logger.info("Falling back to standard synthesis")
            audio_data = await self.synthesize(text)
            yield audio_data

    async def multi_context_stream(self, context_id: str = "default") -> Dict[str, Any]:
        """
        Create a multi-context streaming session for real-time conversation.
        
        Args:
            context_id: Unique identifier for this context
            
        Returns:
            Context session object with methods for sending text and receiving audio
        """
        try:
            # Build WebSocket URL for multi-context
            ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/multi-stream-input"
            params = "&".join([f"{k}={v}" for k, v in self.ws_params.items()])
            full_url = f"{ws_url}?{params}"
            
            headers = {"xi-api-key": self.api_key}
            
            websocket = await websockets.connect(full_url, extra_headers=headers)
            
            # Initialize connection
            init_message = {
                "message": "init_connection_multi",
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": self.voice_settings.stability,
                    "similarity_boost": self.voice_settings.similarity_boost,
                    "style": self.voice_settings.style,
                    "use_speaker_boost": self.voice_settings.use_speaker_boost
                }
            }
            await websocket.send(json.dumps(init_message))
            
            # Initialize context
            context_init = {
                "message": "init_context",
                "context_id": context_id,
                "voice_settings": {
                    "stability": self.voice_settings.stability,
                    "similarity_boost": self.voice_settings.similarity_boost,
                    "style": self.voice_settings.style,
                    "use_speaker_boost": self.voice_settings.use_speaker_boost
                }
            }
            await websocket.send(json.dumps(context_init))
            
            logger.info(f"Multi-context session initialized with context_id: {context_id}")
            
            return {
                "websocket": websocket,
                "context_id": context_id,
                "send_text": self._create_send_text_func(websocket, context_id),
                "close": self._create_close_func(websocket, context_id)
            }
            
        except Exception as e:
            logger.error(f"Error creating multi-context stream: {e}")
            raise

    def _create_send_text_func(self, websocket, context_id: str):
        """Create a function to send text to the multi-context stream."""
        async def send_text(text: str, flush: bool = False):
            try:
                message = {
                    "message": "send_text_multi",
                    "context_id": context_id,
                    "text": text
                }
                await websocket.send(json.dumps(message))
                
                if flush:
                    flush_message = {
                        "message": "flush_context",
                        "context_id": context_id
                    }
                    await websocket.send(json.dumps(flush_message))
                    
            except Exception as e:
                logger.error(f"Error sending text to context {context_id}: {e}")
                raise
                
        return send_text

    def _create_close_func(self, websocket, context_id: str):
        """Create a function to close the multi-context stream."""
        async def close():
            try:
                close_message = {
                    "message": "close_context",
                    "context_id": context_id
                }
                await websocket.send(json.dumps(close_message))
                await websocket.close()
                logger.info(f"Multi-context session closed for context_id: {context_id}")
                
            except Exception as e:
                logger.error(f"Error closing context {context_id}: {e}")
                
        return close

    def get_available_voices(self) -> list:
        """Get list of available voices."""
        try:
            voices = self.client.voices.search()
            return [{"id": voice.voice_id, "name": voice.name} for voice in voices.voices]
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return [] 