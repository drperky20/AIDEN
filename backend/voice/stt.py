"""
Fast Speech-to-Text Implementation using Whisper

Provides low-latency speech-to-text using faster-whisper for real-time transcription.
"""

import asyncio
import logging
import queue
import threading
import time
from typing import AsyncGenerator, Optional, Callable, Dict, Any
import os

import pyaudio
import numpy as np
from faster_whisper import WhisperModel
from pydub import AudioSegment
from io import BytesIO

logger = logging.getLogger(__name__)


class WhisperSTT:
    """
    Fast Whisper Speech-to-Text with real-time transcription capabilities.
    
    Uses faster-whisper for optimal performance and pyaudio for real-time audio capture.
    """

    def __init__(
        self,
        model_size: str = "tiny.en",  # Fastest model for lowest latency
        device: str = "auto",
        compute_type: str = "auto",
        sample_rate: int = 16000,
        chunk_duration: float = 1.0,  # Process audio every 1 second
        silence_threshold: float = 0.01,
        min_audio_length: float = 0.5,
        language: str = "en"
    ):
        """
        Initialize Whisper STT.
        
        Args:
            model_size: Whisper model size (tiny.en, base.en, small.en for speed)
            device: Device to use (cpu, cuda, auto)
            compute_type: Computation type (auto, int8, float16)
            sample_rate: Audio sample rate
            chunk_duration: How often to process audio chunks (seconds)
            silence_threshold: Threshold for detecting silence
            min_audio_length: Minimum audio length to process (seconds)
            language: Language for transcription
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.silence_threshold = silence_threshold
        self.min_audio_length = min_audio_length
        self.language = language
        
        # Initialize Whisper model
        logger.info(f"Loading Whisper model: {model_size}")
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                download_root=os.path.expanduser("~/.cache/whisper")
            )
            logger.info(f"Whisper model {model_size} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
        
        # Audio configuration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.format = pyaudio.paInt16
        self.channels = 1
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.audio_stream = None
        self.pyaudio_instance = None

    async def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Transcribed text
        """
        try:
            # Convert bytes to numpy array
            if isinstance(audio_data, bytes):
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            else:
                audio_array = audio_data
            
            # Convert to float32 and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Check if audio is long enough and not silent
            duration = len(audio_float) / self.sample_rate
            if duration < self.min_audio_length:
                return ""
            
            # Check for silence
            if np.max(np.abs(audio_float)) < self.silence_threshold:
                return ""
            
            # Transcribe using faster-whisper
            segments, info = self.model.transcribe(
                audio_float,
                language=self.language,
                beam_size=1,  # Fastest beam size
                best_of=1,    # Fastest setting
                temperature=0.0,  # Deterministic output
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=400
                )
            )
            
            # Combine all segments
            text = " ".join([segment.text.strip() for segment in segments])
            
            if text.strip():
                logger.debug(f"Transcribed: {text}")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""

    async def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Convert to the required format
            audio = audio.set_frame_rate(self.sample_rate).set_channels(1)
            
            # Convert to numpy array
            audio_data = np.array(audio.get_array_of_samples(), dtype=np.int16)
            
            return await self.transcribe_audio(audio_data.tobytes())
            
        except Exception as e:
            logger.error(f"Error transcribing file {file_path}: {e}")
            return ""

    def start_recording(self) -> None:
        """Start real-time audio recording."""
        try:
            if self.is_recording:
                logger.warning("Recording is already active")
                return
            
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Find the best input device
            default_input = self.pyaudio_instance.get_default_input_device_info()
            logger.info(f"Using input device: {default_input['name']}")
            
            self.audio_stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.audio_stream.start_stream()
            logger.info("Started real-time audio recording")
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.stop_recording()
            raise

    def stop_recording(self) -> None:
        """Stop real-time audio recording."""
        try:
            self.is_recording = False
            
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            
            # Clear any remaining audio data
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            logger.info("Stopped real-time audio recording")
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream."""
        if self.is_recording:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    async def stream_transcription(
        self,
        callback: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream real-time transcription.
        
        Args:
            callback: Optional callback function for each transcription
            
        Yields:
            Transcribed text chunks
        """
        if not self.is_recording:
            raise RuntimeError("Recording must be started before streaming transcription")
        
        audio_buffer = b""
        last_process_time = time.time()
        
        try:
            while self.is_recording:
                # Collect audio data
                try:
                    while not self.audio_queue.empty():
                        chunk = self.audio_queue.get_nowait()
                        audio_buffer += chunk
                except queue.Empty:
                    pass
                
                # Process audio if enough time has passed
                current_time = time.time()
                if (current_time - last_process_time) >= self.chunk_duration:
                    if len(audio_buffer) > 0:
                        # Transcribe the audio buffer
                        text = await self.transcribe_audio(audio_buffer)
                        
                        if text:
                            if callback:
                                callback(text)
                            yield text
                        
                        # Reset buffer and timer
                        audio_buffer = b""
                        last_process_time = current_time
                
                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error in stream transcription: {e}")
        finally:
            # Process any remaining audio
            if len(audio_buffer) > 0:
                try:
                    text = await self.transcribe_audio(audio_buffer)
                    if text:
                        if callback:
                            callback(text)
                        yield text
                except Exception as e:
                    logger.error(f"Error processing final audio buffer: {e}")

    async def detect_speech_start(self, timeout: float = 5.0) -> bool:
        """
        Detect when speech starts.
        
        Args:
            timeout: Maximum time to wait for speech (seconds)
            
        Returns:
            True if speech detected, False if timeout
        """
        if not self.is_recording:
            raise RuntimeError("Recording must be started before detecting speech")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if not self.audio_queue.empty():
                    chunk = self.audio_queue.get_nowait()
                    audio_array = np.frombuffer(chunk, dtype=np.int16)
                    audio_float = audio_array.astype(np.float32) / 32768.0
                    
                    # Check if audio level is above silence threshold
                    if np.max(np.abs(audio_float)) > self.silence_threshold:
                        logger.debug("Speech detected")
                        return True
                        
            except queue.Empty:
                pass
            
            await asyncio.sleep(0.01)
        
        logger.debug("Speech detection timeout")
        return False

    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        return [
            "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr", "pl", "ca", "nl",
            "ar", "sv", "it", "id", "hi", "fi", "vi", "he", "uk", "el", "ms", "cs", "ro",
            "da", "hu", "ta", "no", "th", "ur", "hr", "bg", "lt", "la", "mi", "ml", "cy",
            "sk", "te", "fa", "lv", "bn", "sr", "az", "sl", "kn", "et", "mk", "br", "eu",
            "is", "hy", "ne", "mn", "bs", "kk", "sq", "sw", "gl", "mr", "pa", "si", "km",
            "sn", "yo", "so", "af", "oc", "ka", "be", "tg", "sd", "gu", "am", "yi", "lo",
            "uz", "fo", "ht", "ps", "tk", "nn", "mt", "sa", "lb", "my", "bo", "tl", "mg",
            "as", "tt", "haw", "ln", "ha", "ba", "jw", "su"
        ] 