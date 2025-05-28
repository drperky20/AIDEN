#!/usr/bin/env python3
"""
Test script to verify streaming functionality
"""
import asyncio
import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.agent.agent_factory import create_main_agent
from backend.config import settings

async def test_streaming():
    """Test the streaming implementation"""
    print("🧪 Testing AIDEN streaming functionality...")
    
    # Check if API key is configured
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY.startswith("your"):
        print("❌ Google API key not configured. Please set GOOGLE_API_KEY in your .env file.")
        return
    
    try:
        # Create agent
        print("🤖 Creating AIDEN agent...")
        agent = create_main_agent()
        print("✅ Agent created successfully")
        
        # Test streaming
        print("\n🔄 Testing streaming response...")
        test_prompt = "Hello! Can you tell me a short story about a robot?"
        
        print(f"User: {test_prompt}")
        print("AIDEN: ", end="", flush=True)
        
        full_response = ""
        async for event in agent.stream_run(test_prompt, session_id="test"):
            event_type = event.get("type", "unknown")
            
            if event_type == "thinking_indicator":
                content = event.get("content", "")
                print(f"\n🤔 {content}")
            
            elif event_type == "tool_start":
                tool_name = event.get("name", "Unknown")
                print(f"\n🔧 Starting tool: {tool_name}")
            
            elif event_type == "tool_end":
                tool_name = event.get("name", "Unknown")
                print(f"✅ Tool completed: {tool_name}")
            
            elif event_type == "llm_chunk":
                chunk = event.get("content", "")
                print(chunk, end="", flush=True)
                full_response += chunk
            
            elif event_type == "final_response":
                final_content = event.get("content", "")
                if final_content and final_content != full_response:
                    print(final_content, end="", flush=True)
                print("\n")
                break
            
            elif event_type == "error":
                error_detail = event.get("detail", "Unknown error")
                print(f"\n❌ Error: {error_detail}")
                break
        
        print("\n✅ Streaming test completed successfully!")
        print(f"📊 Total response length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"❌ Error during streaming test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_streaming()) 