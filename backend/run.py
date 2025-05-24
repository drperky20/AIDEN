#!/usr/bin/env python3
"""
Simple run script for the Agno Gemini Agent
This script loads environment variables from .env file if it exists
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print("No .env file found. Make sure to set GOOGLE_API_KEY environment variable.")

def main():
    """Main function to run the application"""
    load_env_file()
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable is not set!")
        print("\nPlease either:")
        print("1. Create a .env file with your API key (copy from env.example)")
        print("2. Set the environment variable manually:")
        print("   export GOOGLE_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("🚀 Starting Agno Gemini Agent...")
    print("📱 Web UI will be available at: http://localhost:8000")
    
    # Import and run the app
    from app import app
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 