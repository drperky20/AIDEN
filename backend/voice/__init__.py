"""
Voice Module for AIDEN V2

Provides text-to-speech and speech-to-text capabilities using ElevenLabs and Whisper.
"""

from .tts import ElevenLabsTTS
from .stt import WhisperSTT
from .voice_manager import VoiceManager

__all__ = ['ElevenLabsTTS', 'WhisperSTT', 'VoiceManager'] 