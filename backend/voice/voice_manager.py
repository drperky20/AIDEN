"""
Voice Manager for AIDEN V2

Coordinates TTS and STT for seamless voice conversations with minimal latency.
"""

import asyncio
import json
import base64
import logging
import time
from typing import Optional, AsyncGenerator, Callable, Dict, Any
from enum import Enum

from .tts import ElevenLabsTTS
from .stt import WhisperSTT

logger = logging.getLogger(__name__)


class VoiceState(Enum):
    """Voice manager states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class VoiceManager:
    """
    Voice Manager that coordinates TTS and STT for real-time conversations.
    
    Handles voice activation detection, speech processing, and audio playback
    with minimal latency for natural conversation flow.
    """

    def __init__(
        self,
        tts_config: Optional[Dict[str, Any]] = None,
        stt_config: Optional[Dict[str, Any]] = None,
        voice_activation_threshold: float = 0.02,
        max_silence_duration: float = 2.0,
        response_timeout: float = 10.0
    ):
        """
        Initialize Voice Manager.
        
        Args:
            tts_config: Configuration for TTS system
            stt_config: Configuration for STT system
            voice_activation_threshold: Threshold for voice activation
            max_silence_duration: Max silence before stopping listening
            response_timeout: Maximum time to wait for response
        """
        self.voice_activation_threshold = voice_activation_threshold
        self.max_silence_duration = max_silence_duration
        self.response_timeout = response_timeout
        
        # Initialize TTS
        tts_config = tts_config or {}
        self.tts = ElevenLabsTTS(**tts_config)
        
        # Initialize STT
        stt_config = stt_config or {}
        stt_config.setdefault("silence_threshold", voice_activation_threshold)
        self.stt = WhisperSTT(**stt_config)
        
        # State management
        self.state = VoiceState.IDLE
        self.current_session = None
        self.is_voice_mode_active = False
        
        # Conversation context
        self.conversation_context = []
        self.last_user_input = ""
        self.last_response = ""

    async def start_voice_mode(self) -> None:
        """Start voice mode for continuous conversation."""
        try:
            if self.is_voice_mode_active:
                logger.warning("Voice mode is already active")
                return
            
            logger.info("Starting voice mode...")
            
            # Start STT recording
            self.stt.start_recording()
            
            # Create TTS multi-context session for low latency
            self.current_session = await self.tts.multi_context_stream("conversation")
            
            self.is_voice_mode_active = True
            self.state = VoiceState.LISTENING
            
            logger.info("Voice mode started successfully")
            
        except Exception as e:
            logger.error(f"Error starting voice mode: {e}")
            self.state = VoiceState.ERROR
            await self.stop_voice_mode()
            raise

    async def stop_voice_mode(self) -> None:
        """Stop voice mode and cleanup resources."""
        try:
            logger.info("Stopping voice mode...")
            
            self.is_voice_mode_active = False
            self.state = VoiceState.IDLE
            
            # Stop STT
            if self.stt.is_recording:
                self.stt.stop_recording()
            
            # Close TTS session
            if self.current_session:
                await self.current_session["close"]()
                self.current_session = None
            
            logger.info("Voice mode stopped")
            
        except Exception as e:
            logger.error(f"Error stopping voice mode: {e}")

    async def listen_for_input(
        self,
        timeout: Optional[float] = None
    ) -> str:
        """
        Listen for user voice input with voice activation detection.
        
        Args:
            timeout: Maximum time to wait for input
            
        Returns:
            Transcribed user input
        """
        if not self.is_voice_mode_active:
            raise RuntimeError("Voice mode must be started before listening")
        
        timeout = timeout or self.response_timeout
        start_time = time.time()
        
        try:
            self.state = VoiceState.LISTENING
            logger.debug("Listening for voice input...")
            
            # Wait for speech to start
            speech_detected = await self.stt.detect_speech_start(timeout=5.0)
            if not speech_detected:
                logger.debug("No speech detected within timeout")
                return ""
            
            # Collect transcription
            full_transcription = ""
            last_speech_time = time.time()
            
            async for text_chunk in self.stt.stream_transcription():
                if text_chunk.strip():
                    full_transcription += " " + text_chunk.strip()
                    last_speech_time = time.time()
                    logger.debug(f"Transcription chunk: {text_chunk}")
                
                # Check for silence timeout
                if time.time() - last_speech_time > self.max_silence_duration:
                    logger.debug("Silence timeout reached")
                    break
                
                # Check for overall timeout
                if time.time() - start_time > timeout:
                    logger.debug("Overall timeout reached")
                    break
            
            self.last_user_input = full_transcription.strip()
            
            if self.last_user_input:
                logger.info(f"User said: {self.last_user_input}")
                self.conversation_context.append({
                    "role": "user",
                    "content": self.last_user_input,
                    "timestamp": time.time()
                })
            
            return self.last_user_input
            
        except Exception as e:
            logger.error(f"Error listening for input: {e}")
            self.state = VoiceState.ERROR
            return ""

    async def speak_response(
        self,
        text: str,
        stream_callback: Optional[Callable[[bytes], None]] = None
    ) -> None:
        """
        Speak the response using TTS with streaming for low latency.
        
        Args:
            text: Text to speak
            stream_callback: Optional callback for each audio chunk
        """
        if not self.is_voice_mode_active or not self.current_session:
            # Fallback to standard synthesis if no session
            audio_data = await self.tts.synthesize(text)
            if stream_callback:
                stream_callback(audio_data)
            return
        
        try:
            self.state = VoiceState.SPEAKING
            logger.info(f"Speaking: {text[:50]}...")
            
            # Send text to TTS session and flush
            await self.current_session["send_text"](text, flush=True)
            
            # Listen for audio chunks from the session
            websocket = self.current_session["websocket"]
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if "audio" in data:
                        audio_chunk = base64.b64decode(data["audio"])
                        if stream_callback:
                            stream_callback(audio_chunk)
                    
                    if data.get("isFinal", False):
                        break
                        
                except asyncio.TimeoutError:
                    logger.warning("TTS response timeout")
                    break
                except json.JSONDecodeError:
                    continue
            
            self.last_response = text
            self.conversation_context.append({
                "role": "assistant",
                "content": text,
                "timestamp": time.time()
            })
            
            self.state = VoiceState.LISTENING
            logger.debug("Finished speaking")
            
        except Exception as e:
            logger.error(f"Error speaking response: {e}")
            self.state = VoiceState.ERROR
            
            # Fallback to standard synthesis
            try:
                audio_data = await self.tts.synthesize(text)
                if stream_callback:
                    stream_callback(audio_data)
            except Exception as fallback_error:
                logger.error(f"Fallback synthesis also failed: {fallback_error}")

    async def handle_conversation_turn(
        self,
        agent_handler: Callable[[str], AsyncGenerator[str, None]],
        audio_callback: Optional[Callable[[bytes], None]] = None,
        text_callback: Optional[Callable[[str, str], None]] = None
    ) -> Dict[str, str]:
        """
        Handle a complete conversation turn: listen -> process -> speak.
        
        Args:
            agent_handler: Async function that takes user input and yields agent responses
            audio_callback: Callback for audio chunks
            text_callback: Callback for text updates (user_input, agent_response)
            
        Returns:
            Dictionary with user_input and agent_response
        """
        if not self.is_voice_mode_active:
            raise RuntimeError("Voice mode must be active for conversation turns")
        
        try:
            # Listen for user input
            user_input = await self.listen_for_input()
            
            if not user_input:
                return {"user_input": "", "agent_response": ""}
            
            # Process with agent
            self.state = VoiceState.PROCESSING
            agent_response = ""
            
            async for response_chunk in agent_handler(user_input):
                agent_response += response_chunk
            
            # Speak the response
            if agent_response:
                await self.speak_response(agent_response, audio_callback)
            
            # Call text callback if provided
            if text_callback:
                text_callback(user_input, agent_response)
            
            return {
                "user_input": user_input,
                "agent_response": agent_response
            }
            
        except Exception as e:
            logger.error(f"Error in conversation turn: {e}")
            self.state = VoiceState.ERROR
            return {"user_input": "", "agent_response": ""}

    async def continuous_conversation(
        self,
        agent_handler: Callable[[str], AsyncGenerator[str, None]],
        audio_callback: Optional[Callable[[bytes], None]] = None,
        text_callback: Optional[Callable[[str, str], None]] = None,
        stop_phrases: Optional[list] = None
    ) -> None:
        """
        Run continuous voice conversation until stopped.
        
        Args:
            agent_handler: Async function for agent responses
            audio_callback: Callback for audio chunks
            text_callback: Callback for text updates
            stop_phrases: Phrases that will stop the conversation
        """
        stop_phrases = stop_phrases or ["goodbye", "stop conversation", "end voice mode"]
        
        logger.info("Starting continuous voice conversation")
        
        try:
            while self.is_voice_mode_active:
                turn_result = await self.handle_conversation_turn(
                    agent_handler, audio_callback, text_callback
                )
                
                user_input = turn_result["user_input"].lower()
                
                # Check for stop phrases
                if any(phrase in user_input for phrase in stop_phrases):
                    logger.info("Stop phrase detected, ending conversation")
                    break
                
                # Small delay between turns
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error in continuous conversation: {e}")
        finally:
            await self.stop_voice_mode()

    def get_conversation_context(self, limit: int = 10) -> list:
        """Get recent conversation context."""
        return self.conversation_context[-limit:] if limit else self.conversation_context

    def clear_conversation_context(self) -> None:
        """Clear conversation context."""
        self.conversation_context.clear()
        logger.info("Conversation context cleared")

    @property
    def is_listening(self) -> bool:
        """Check if currently listening for input."""
        return self.state == VoiceState.LISTENING

    @property
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self.state == VoiceState.SPEAKING

    @property
    def is_processing(self) -> bool:
        """Check if currently processing."""
        return self.state == VoiceState.PROCESSING 