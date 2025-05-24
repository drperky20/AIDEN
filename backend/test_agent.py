#!/usr/bin/env python3
"""
Test script for the Agno Gemini Agent
Run this to test if your agent is working correctly
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

def test_agent():
    """Test the agent with a simple message"""
    load_env_file()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable is not set!")
        print("Please set your API key before running the test.")
        return False
    
    try:
        print("🧪 Testing Agno Gemini Agent...")
        
        from agent import create_agent
        
        # Create the agent
        agent = create_agent()
        print("✅ Agent created successfully!")
        
        # Test with a simple message
        print("🤖 Testing agent response...")
        response = agent.run("Hello! Please introduce yourself briefly.")
        
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
    success = test_agent()
    sys.exit(0 if success else 1) 