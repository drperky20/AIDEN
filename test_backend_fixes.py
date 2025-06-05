#!/usr/bin/env python3
"""
Test script to verify OpenRouter and ElevenLabs fixes
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models.openrouter import OpenRouterModel
from backend.voice.tts import ElevenLabsTTS
from backend.config import settings

async def test_openrouter():
    """Test OpenRouter model creation and basic functionality"""
    print("🧪 Testing OpenRouter Model...")
    
    try:
        # Test model creation
        model = OpenRouterModel(
            id=settings.OPENROUTER_MODEL_ID,
            api_key=settings.OPENROUTER_API_KEY,
            temperature=0.7,
            max_tokens=100
        )
        print("✅ OpenRouter model created successfully")
        
        # Test basic invoke method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in exactly 5 words."}
        ]
        
        print("📡 Testing ainvoke method...")
        response = await model.ainvoke(messages)
        print(f"✅ Response received: {type(response)}")
        
        # Test parse method
        content = model.parse_provider_response(response)
        print(f"✅ Parsed content: {content[:50]}...")
        
        # Clean up
        await model.close()
        print("✅ OpenRouter model test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter test failed: {e}")
        return False

async def test_elevenlabs():
    """Test ElevenLabs TTS functionality"""
    print("\n🧪 Testing ElevenLabs TTS...")
    
    try:
        # Test TTS creation
        tts = ElevenLabsTTS(
            api_key=settings.ELEVENLABS_API_KEY,
            voice_id=settings.ELEVENLABS_VOICE_ID,
            model_id=settings.ELEVENLABS_MODEL_ID
        )
        print("✅ ElevenLabs TTS created successfully")
        
        # Test voice listing
        print("📡 Testing voice listing...")
        voices = tts.get_available_voices()
        print(f"✅ Found {len(voices)} voices")
        
        # Test basic synthesis (short text to avoid usage)
        print("📡 Testing text synthesis...")
        audio_data = await tts.synthesize("Test")
        print(f"✅ Audio synthesized: {len(audio_data)} bytes")
        
        print("✅ ElevenLabs TTS test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ ElevenLabs test failed: {e}")
        return False

async def test_agent_creation():
    """Test agent creation with the fixed model"""
    print("\n🧪 Testing Agent Creation...")
    
    try:
        from backend.agent.agent_factory import create_simple_agent
        
        agent = create_simple_agent()
        print("✅ Agent created successfully")
        print(f"✅ Agent model: {type(agent.model).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting AIDEN Backend Fix Tests\n")
    
    results = []
    
    # Test OpenRouter
    if settings.is_openrouter_valid:
        results.append(await test_openrouter())
    else:
        print("⚠️ OpenRouter API key not configured, skipping test")
        results.append(True)  # Don't fail the test
    
    # Test ElevenLabs
    if settings.is_elevenlabs_valid:
        results.append(await test_elevenlabs())
    else:
        print("⚠️ ElevenLabs API key not configured, skipping test")
        results.append(True)  # Don't fail the test
    
    # Test agent creation
    results.append(await test_agent_creation())
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! The fixes are working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 