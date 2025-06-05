#!/usr/bin/env python3
"""
AIDEN Voice Mode Setup Script

Interactive script to help configure API keys and test voice functionality.
"""
import os
import asyncio
import httpx
from pathlib import Path

def create_env_file():
    """Create or update .env file with voice configuration"""
    env_path = Path(".env")
    
    print("🔧 AIDEN Voice Mode Setup")
    print("=" * 40)
    
    # Template content
    env_template = """# ===========================================
# AIDEN V2 Voice Mode Configuration
# ===========================================

# ===================
# Model Configuration
# ===================
USE_OPENROUTER=True
OPENROUTER_API_KEY={openrouter_key}
OPENROUTER_MODEL_ID=meta-llama/llama-4-maverick:free

# Fallback Model
GOOGLE_API_KEY={google_key}
GEMINI_MODEL_ID=gemini-1.5-flash-latest

# ===================
# Voice Configuration
# ===================
ENABLE_VOICE_MODE=True
ELEVENLABS_API_KEY={elevenlabs_key}
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

# ===================
# Agent Configuration
# ===================
ENABLE_WEB_SEARCH=True
SHOW_TOOL_CALLS=True
ENABLE_MARKDOWN=True
MAX_HISTORY_MESSAGES=5
"""

    # Collect API keys
    print("\n📋 API Key Configuration")
    print("You can get these API keys from:")
    print("1. OpenRouter: https://openrouter.ai/ (FREE)")
    print("2. ElevenLabs: https://elevenlabs.io/ (Free tier: 10k chars/month)")
    print("3. Google AI Studio: https://aistudio.google.com/ (Free tier)")
    print()
    
    # Check existing .env
    existing_keys = {}
    if env_path.exists():
        print("Found existing .env file. Current values will be shown in [brackets].")
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if not value.startswith('your_'):
                        existing_keys[key] = value
    
    # Get OpenRouter API key
    current_openrouter = existing_keys.get('OPENROUTER_API_KEY', '')
    openrouter_prompt = f"OpenRouter API Key [{current_openrouter[:20]}...]: " if current_openrouter else "OpenRouter API Key: "
    openrouter_key = input(openrouter_prompt).strip()
    if not openrouter_key and current_openrouter:
        openrouter_key = current_openrouter
    elif not openrouter_key:
        openrouter_key = "your_openrouter_api_key_here"
    
    # Get ElevenLabs API key
    current_elevenlabs = existing_keys.get('ELEVENLABS_API_KEY', '')
    elevenlabs_prompt = f"ElevenLabs API Key [{current_elevenlabs[:20]}...]: " if current_elevenlabs else "ElevenLabs API Key: "
    elevenlabs_key = input(elevenlabs_prompt).strip()
    if not elevenlabs_key and current_elevenlabs:
        elevenlabs_key = current_elevenlabs
    elif not elevenlabs_key:
        elevenlabs_key = "your_elevenlabs_api_key_here"
    
    # Get Google API key
    current_google = existing_keys.get('GOOGLE_API_KEY', '')
    google_prompt = f"Google API Key [{current_google[:20]}...]: " if current_google else "Google API Key: "
    google_key = input(google_prompt).strip()
    if not google_key and current_google:
        google_key = current_google
    elif not google_key:
        google_key = "your_google_api_key_here"
    
    # Write the file
    env_content = env_template.format(
        openrouter_key=openrouter_key,
        elevenlabs_key=elevenlabs_key,
        google_key=google_key
    )
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to {env_path}")
    
    # Show status
    has_openrouter = openrouter_key and not openrouter_key.startswith('your_')
    has_elevenlabs = elevenlabs_key and not elevenlabs_key.startswith('your_')
    has_google = google_key and not google_key.startswith('your_')
    
    print("\n📊 Configuration Status:")
    print(f"   OpenRouter (Llama 4 Maverick): {'✅' if has_openrouter else '❌'}")
    print(f"   ElevenLabs (Voice TTS): {'✅' if has_elevenlabs else '❌'}")
    print(f"   Google Gemini (Fallback): {'✅' if has_google else '❌'}")
    
    if has_google and (has_openrouter or has_elevenlabs):
        print("\n🎉 Ready to start AIDEN with voice capabilities!")
        print("\nNext steps:")
        print("1. Restart the server: python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Test voice status: python test_voice_setup.py")
        print("3. View API docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Please add valid API keys to enable full functionality.")

async def test_server():
    """Test if the server is running and show voice status"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Test basic connectivity
            response = await client.get("http://localhost:8000/")
            print("✅ Server is running")
            
            # Test voice status
            response = await client.get("http://localhost:8000/voice/status")
            voice_status = response.json()
            
            print(f"🎤 Voice Status:")
            print(f"   Available: {voice_status['voice_mode_available']}")
            if voice_status['voice_mode_available']:
                print(f"   Voice ID: {voice_status['configuration']['voice_id']}")
                print(f"   Model: {voice_status['configuration']['whisper_model']}")
            
    except httpx.ConnectError:
        print("❌ Server not running. Start with:")
        print("   python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload")
    except Exception as e:
        print(f"❌ Error testing server: {e}")

def main():
    """Main setup function"""
    print("Welcome to AIDEN Voice Mode Setup! 🎉")
    print()
    
    choice = input("Choose an option:\n1. Configure API keys\n2. Test current setup\n3. Show voice commands\nChoice (1-3): ").strip()
    
    if choice == "1":
        create_env_file()
    elif choice == "2":
        asyncio.run(test_server())
    elif choice == "3":
        show_voice_commands()
    else:
        print("Invalid choice. Please run again.")

def show_voice_commands():
    """Show available voice commands and endpoints"""
    print("🎤 AIDEN Voice Commands & Endpoints")
    print("=" * 45)
    
    print("\n📞 REST API Endpoints:")
    print("   GET  /voice/status              - Check voice system status")
    print("   POST /voice/tts                 - Convert text to speech")
    print("   POST /voice/stt                 - Convert speech to text")
    print("   GET  /voice/voices              - List available voices")
    print("   POST /voice/start-voice-mode    - Start voice conversation")
    print("   POST /voice/stop-voice-mode     - Stop voice conversation")
    
    print("\n🌐 WebSocket Endpoints:")
    print("   WS /voice/stream                - Full bidirectional voice chat")
    print("   WS /voice/tts-stream            - Streaming TTS generation")
    
    print("\n🧪 Test Commands:")
    print("   # Check voice status")
    print("   curl http://localhost:8000/voice/status")
    print()
    print("   # Test TTS")
    print('   curl -X POST "http://localhost:8000/voice/tts" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"text": "Hello from AIDEN!"}\' \\')
    print('     --output speech.mp3')
    print()
    print("   # View API documentation")
    print("   open http://localhost:8000/docs")

if __name__ == "__main__":
    main() 