# AIDEN V2 Voice Mode Setup Guide

This guide will help you set up the complete voice-enabled AIDEN system with **Llama 4 Maverick** (the fastest FREE model) and **ElevenLabs** for minimal latency voice interactions.

## 🚀 Quick Overview

- **Primary Model**: OpenRouter with **Llama 4 Maverick FREE** (fastest free model available)
- **Voice TTS**: ElevenLabs with WebSocket streaming for minimal latency
- **Voice STT**: Whisper (faster-whisper) for fast, accurate transcription
- **Fallback Model**: Google Gemini (if OpenRouter unavailable)

## 📋 Prerequisites

1. Python 3.11+ (recommended for best performance)
2. Audio input device (microphone)
3. Audio output device (speakers/headphones)

## 🔑 Required API Keys

### 1. OpenRouter API Key (FREE - Primary Model)
- **Service**: OpenRouter 
- **Model**: `meta-llama/llama-4-maverick:free` (100% FREE!)
- **Get Key**: https://openrouter.ai/
- **Why**: Industry-leading performance at zero cost

### 2. ElevenLabs API Key (Voice TTS)
- **Service**: ElevenLabs
- **Free Tier**: 10,000 characters/month
- **Get Key**: https://elevenlabs.io/
- **Why**: High-quality, low-latency voice synthesis

### 3. Google Gemini API Key (Fallback)
- **Service**: Google AI Studio
- **Free Tier**: Generous free quota
- **Get Key**: https://aistudio.google.com/
- **Why**: Reliable fallback if OpenRouter issues

## ⚙️ Environment Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Then update the file with your API keys
# (.env is ignored by Git)

# ===================
# Model Configuration
# ===================
USE_OPENROUTER=True
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL_ID=meta-llama/llama-4-maverick:free

# Fallback
GOOGLE_API_KEY=your_google_api_key_here

# ===================
# Voice Configuration
# ===================
ENABLE_VOICE_MODE=True
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel voice
ELEVENLABS_MODEL_ID=eleven_flash_v2_5      # Fastest model

# Whisper STT Settings
WHISPER_MODEL_SIZE=tiny.en                 # Fastest for low latency
VOICE_ACTIVATION_THRESHOLD=0.02
MAX_SILENCE_DURATION=2.0

# ===================
# API Configuration
# ===================
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
ENVIRONMENT=development
```

## 📦 Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Install Audio Dependencies** (if needed):

**macOS**:
```bash
brew install portaudio ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio ffmpeg
```

**Windows**:
```bash
# Usually works out of the box, but if issues:
pip install pipwin
pipwin install pyaudio
```

## 🎯 Performance Optimization

### For Fastest Voice Response:

1. **Use the recommended models**:
   - OpenRouter: `meta-llama/llama-4-maverick:free`
   - ElevenLabs: `eleven_flash_v2_5`
   - Whisper: `tiny.en`

2. **Audio Settings**:
```bash
VOICE_ACTIVATION_THRESHOLD=0.02  # Lower = more sensitive
MAX_SILENCE_DURATION=2.0         # Shorter = faster response
WHISPER_MODEL_SIZE=tiny.en       # Fastest transcription
```

3. **Network Optimization**:
   - Use a stable internet connection
   - Consider running on a server closer to API endpoints

## 🚀 Running AIDEN with Voice

1. **Start the API Server**:
```bash
cd /path/to/AIDEN
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Check Voice Status**:
```bash
curl http://localhost:8000/voice/status
```

3. **Test Basic TTS**:
```bash
curl -X POST "http://localhost:8000/voice/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello! AIDEN voice mode is working!"}' \
  --output test_speech.mp3
```

## 🎤 Voice API Endpoints

### REST Endpoints:
- `GET /voice/status` - Check voice system status
- `POST /voice/tts` - Text-to-speech conversion
- `POST /voice/stt` - Speech-to-text conversion  
- `GET /voice/voices` - List available voices
- `POST /voice/start-voice-mode` - Start voice conversation mode
- `POST /voice/stop-voice-mode` - Stop voice conversation mode

### WebSocket Endpoints:
- `WS /voice/stream` - Full bidirectional voice conversation
- `WS /voice/tts-stream` - Streaming TTS generation

## 🔧 Voice Configuration Options

### Available Voices (ELEVENLABS_VOICE_ID):
- `21m00Tcm4TlvDq8ikWAM` - Rachel (default, professional female)
- `EXAVITQu4vr4xnSDxMaL` - Bella (young female)
- `ErXwobaYiN019PkySvjV` - Antoni (male)
- `MF3mGyEYCl7XYWbV9V6O` - Elli (young female)
- `TxGEqnHWrfWFTfGW9XjX` - Josh (young male)

### Whisper Models (WHISPER_MODEL_SIZE):
- `tiny.en` - Fastest (39 MB, English only) ⚡
- `base.en` - Balanced (74 MB, English only)
- `small.en` - Better quality (244 MB, English only)
- `medium.en` - High quality (769 MB, English only)
- `large-v2` - Best quality (1550 MB, multilingual)

### ElevenLabs Models (ELEVENLABS_MODEL_ID):
- `eleven_flash_v2_5` - Fastest, lowest latency ⚡
- `eleven_turbo_v2_5` - Good balance
- `eleven_multilingual_v2` - Supports multiple languages

## 🐛 Troubleshooting

### Common Issues:

1. **"Voice mode not available"**:
   - Check ELEVENLABS_API_KEY is set correctly
   - Verify API key is valid at https://elevenlabs.io/

2. **Audio input not working**:
   - Check microphone permissions
   - Verify audio device in system settings
   - Try different VOICE_ACTIVATION_THRESHOLD values

3. **Slow response times**:
   - Use `tiny.en` Whisper model
   - Use `eleven_flash_v2_5` ElevenLabs model
   - Check internet connection stability

4. **OpenRouter API errors**:
   - Verify OPENROUTER_API_KEY is correct
   - Check model ID: `meta-llama/llama-4-maverick:free`
   - System will fallback to Gemini automatically

5. **Module import errors**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 🌟 Why This Setup?

### Llama 4 Maverick Benefits:
- **FREE** to use (no cost per request)
- **Fastest** Llama 4 model available
- **State-of-the-art** performance for conversation
- **Multimodal** capabilities
- **Best-in-class** performance-to-cost ratio

### ElevenLabs Benefits:
- **WebSocket streaming** for minimal latency
- **High-quality** voice synthesis
- **Multiple voices** and languages
- **Real-time** audio generation

### Faster-Whisper Benefits:
- **4-5x faster** than OpenAI Whisper
- **Lower memory** usage
- **Real-time** transcription capability
- **Multiple model sizes** for speed/accuracy tradeoff

## 📈 Performance Benchmarks

Expected latencies with recommended settings:
- **STT (Speech-to-Text)**: ~200-500ms
- **LLM Processing**: ~500-1500ms  
- **TTS (Text-to-Speech)**: ~200-800ms
- **Total Voice Round-trip**: ~1-3 seconds

## 🔄 Upgrading

To upgrade to newer models when available:

1. **Check OpenRouter models**:
```bash
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models
```

2. **Update model ID** in `.env`:
```bash
OPENROUTER_MODEL_ID=meta-llama/llama-4-scout:free  # Example future model
```

## 💡 Advanced Usage

### Custom Voice Workflows:
- Integrate with webhooks for external triggers
- Build custom voice commands and responses
- Create voice-activated automation

### Multi-language Support:
- Use `eleven_multilingual_v2` model
- Set appropriate Whisper model for your language
- Configure language codes in STT settings

---

**Ready to experience the future of AI voice interaction!** 🎉

For issues or questions, check the logs at `backend/api/main.py` startup for configuration validation. 