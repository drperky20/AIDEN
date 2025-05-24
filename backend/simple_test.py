#!/usr/bin/env python3
"""
Simple test script for the Agno Gemini Agent (without web search)
This avoids rate limiting issues with DuckDuckGo
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def test_simple_agent():
    """Test the simple agent without web search"""
    load_env_file()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable is not set!")
        print("Please set your API key before running the test.")
        return False
    
    try:
        print("🧪 Testing Simple Agno Gemini Agent (no web search)...")
        
        from agent import create_simple_agent
        
        # Create the simple agent
        agent = create_simple_agent()
        print("✅ Simple agent created successfully!")
        
        # Test with a simple message
        print("🤖 Testing agent response...")
        response = agent.run("Hello! Please introduce yourself and tell me what you can help with.")
        
        print("\n" + "="*50)
        print("AGENT RESPONSE:")
        print("="*50)
        print(response.content)
        print("="*50)
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_agent()
    sys.exit(0 if success else 1) 