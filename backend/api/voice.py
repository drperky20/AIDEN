"""
Voice API Endpoints for AIDEN V2

Provides REST and WebSocket endpoints for voice interactions including
text-to-speech, speech-to-text, and full voice conversation modes.
"""

import asyncio
import logging
import json
import base64
from typing import Optional, Dict, Any
from io import BytesIO

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel

from backend.config import settings
from backend.voice import VoiceManager, ElevenLabsTTS, WhisperSTT
from backend.agent.agent_factory import get_agent_instance

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/voice", tags=["voice"])

# Global voice manager instance
voice_manager: Optional[VoiceManager] = None

class TTSRequest(BaseModel):
    """Request model for text-to-speech."""
    text: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = None

class VoiceConfig(BaseModel):
    """Voice configuration model."""
    tts_voice_id: Optional[str] = None
    tts_model_id: Optional[str] = None
    stt_model_size: Optional[str] = None
    voice_activation_threshold: Optional[float] = None
    max_silence_duration: Optional[float] = None

class ConversationMessage(BaseModel):
    """Conversation message model."""
    user_input: str
    agent_response: str
    timestamp: float

def get_voice_manager() -> VoiceManager:
    """Get or create voice manager instance."""
    global voice_manager
    
    if not settings.is_voice_mode_available:
        raise HTTPException(
            status_code=503,
            detail="Voice mode not available. Please check ElevenLabs API key configuration."
        )
    
    if voice_manager is None:
        try:
            tts_config = {
                "api_key": settings.ELEVENLABS_API_KEY,
                "voice_id": settings.ELEVENLABS_VOICE_ID,
                "model_id": settings.ELEVENLABS_MODEL_ID
            }
            
            stt_config = {
                "model_size": settings.WHISPER_MODEL_SIZE,
                "language": "en"
            }
            
            voice_manager = VoiceManager(
                tts_config=tts_config,
                stt_config=stt_config,
                voice_activation_threshold=settings.VOICE_ACTIVATION_THRESHOLD,
                max_silence_duration=settings.MAX_SILENCE_DURATION
            )
            
            logger.info("Voice manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice manager: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize voice system: {e}")
    
    return voice_manager

@router.get("/status")
async def get_voice_status():
    """Get voice system status and configuration."""
    return {
        "voice_mode_available": settings.is_voice_mode_available,
        "elevenlabs_configured": settings.is_elevenlabs_valid,
        "configuration": {
            "voice_id": settings.ELEVENLABS_VOICE_ID,
            "model_id": settings.ELEVENLABS_MODEL_ID,
            "whisper_model": settings.WHISPER_MODEL_SIZE,
            "voice_activation_threshold": settings.VOICE_ACTIVATION_THRESHOLD,
            "max_silence_duration": settings.MAX_SILENCE_DURATION
        }
    }

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech and return audio data."""
    try:
        vm = get_voice_manager()
        
        # Override configuration if provided
        if request.voice_id:
            vm.tts.voice_id = request.voice_id
        if request.model_id:
            vm.tts.model_id = request.model_id
        
        # Generate audio
        audio_data = await vm.tts.synthesize(request.text)
        
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech audio file to text."""
    try:
        vm = get_voice_manager()
        
        # Read audio file
        audio_data = await audio.read()
        
        # Save temporarily and transcribe
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            text = await vm.stt.transcribe_file(temp_path)
            return {"text": text}
        finally:
            import os
            os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {e}")

@router.get("/voices")
async def list_voices():
    """Get available TTS voices."""
    try:
        vm = get_voice_manager()
        voices = vm.tts.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {e}")

@router.post("/start-voice-mode")
async def start_voice_mode():
    """Start voice mode for the session."""
    try:
        vm = get_voice_manager()
        await vm.start_voice_mode()
        return {"status": "voice_mode_started", "state": vm.state.value}
    except Exception as e:
        logger.error(f"Error starting voice mode: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start voice mode: {e}")

@router.post("/stop-voice-mode")
async def stop_voice_mode():
    """Stop voice mode for the session."""
    try:
        vm = get_voice_manager()
        await vm.stop_voice_mode()
        return {"status": "voice_mode_stopped", "state": vm.state.value}
    except Exception as e:
        logger.error(f"Error stopping voice mode: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop voice mode: {e}")

@router.get("/conversation-context")
async def get_conversation_context(limit: int = 10):
    """Get recent conversation context."""
    try:
        vm = get_voice_manager()
        context = vm.get_conversation_context(limit)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation context: {e}")

@router.delete("/conversation-context")
async def clear_conversation_context():
    """Clear conversation context."""
    try:
        vm = get_voice_manager()
        vm.clear_conversation_context()
        return {"status": "conversation_context_cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation context: {e}")

@router.websocket("/stream")
async def voice_stream_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice streaming.
    
    Supports bidirectional voice communication with minimal latency.
    """
    await websocket.accept()
    logger.info("Voice stream WebSocket connection accepted")
    
    try:
        vm = get_voice_manager()
        agent = get_agent_instance()
        
        # Start voice mode
        await vm.start_voice_mode()
        
        # Send initial status
        await websocket.send_json({
            "type": "status",
            "data": {
                "voice_mode_active": vm.is_voice_mode_active,
                "state": vm.state.value
            }
        })
        
        async def agent_handler(user_input: str):
            """Handle agent responses for voice conversation."""
            try:
                # Stream response from agent
                full_response = ""
                async for event in agent.stream_run(user_input):
                    if event["type"] == "llm_chunk":
                        full_response += event["content"]
                    elif event["type"] == "final_response":
                        full_response = event["content"]
                        break
                
                yield full_response
                
            except Exception as e:
                logger.error(f"Error in agent handler: {e}")
                yield f"I apologize, but I encountered an error: {str(e)}"
        
        def audio_callback(audio_chunk: bytes):
            """Send audio chunks to client."""
            try:
                audio_b64 = base64.b64encode(audio_chunk).decode()
                asyncio.create_task(websocket.send_json({
                    "type": "audio",
                    "data": audio_b64
                }))
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
        
        def text_callback(user_input: str, agent_response: str):
            """Send text updates to client."""
            try:
                asyncio.create_task(websocket.send_json({
                    "type": "conversation",
                    "data": {
                        "user_input": user_input,
                        "agent_response": agent_response,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                }))
            except Exception as e:
                logger.error(f"Error sending text update: {e}")
        
        # Start continuous conversation
        conversation_task = asyncio.create_task(
            vm.continuous_conversation(
                agent_handler=agent_handler,
                audio_callback=audio_callback,
                text_callback=text_callback
            )
        )
        
        try:
            # Handle incoming WebSocket messages
            while True:
                try:
                    message = await websocket.receive_json()
                    message_type = message.get("type")
                    
                    if message_type == "stop":
                        logger.info("Received stop command")
                        break
                    elif message_type == "config":
                        # Handle configuration updates
                        config = message.get("data", {})
                        logger.info(f"Received config update: {config}")
                        # Apply configuration changes here if needed
                    
                except WebSocketDisconnect:
                    logger.info("WebSocket disconnected")
                    break
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": str(e)}
                    })
        
        finally:
            # Cancel conversation task
            conversation_task.cancel()
            try:
                await conversation_task
            except asyncio.CancelledError:
                pass
            
            # Stop voice mode
            await vm.stop_voice_mode()
    
    except WebSocketDisconnect:
        logger.info("Voice stream WebSocket disconnected")
    except Exception as e:
        logger.error(f"Voice stream WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error", 
                "data": {"message": str(e)}
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
        logger.info("Voice stream WebSocket connection closed")

@router.websocket("/tts-stream")
async def tts_stream_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for streaming TTS generation.
    
    Receives text and streams back audio chunks in real-time.
    """
    await websocket.accept()
    logger.info("TTS stream WebSocket connection accepted")
    
    try:
        vm = get_voice_manager()
        
        while True:
            try:
                # Receive text message
                message = await websocket.receive_json()
                text = message.get("text", "")
                
                if not text:
                    continue
                
                logger.debug(f"Generating TTS for: {text[:50]}...")
                
                # Stream audio chunks
                async for audio_chunk in vm.tts.stream_synthesize(text):
                    audio_b64 = base64.b64encode(audio_chunk).decode()
                    await websocket.send_json({
                        "type": "audio",
                        "data": audio_b64
                    })
                
                # Send completion signal
                await websocket.send_json({
                    "type": "complete"
                })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"TTS stream error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": str(e)}
                })
    
    except WebSocketDisconnect:
        logger.info("TTS stream WebSocket disconnected")
    except Exception as e:
        logger.error(f"TTS stream WebSocket error: {e}")
    finally:
        await websocket.close()
        logger.info("TTS stream WebSocket connection closed") 