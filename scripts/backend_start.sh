#!/bin/bash

echo "🚀 Starting Backend Application..."
echo "------------------------------------"
echo "⏳ Please wait while the backend server starts."
echo ""

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to the backend directory relative to the script's location
cd "$SCRIPT_DIR/../backend" || { echo "❌ Error: Could not navigate to backend directory."; exit 1; }

echo "✨ Backend server starting..."

# Placeholder for the actual command to start your backend server.
# COMMON EXAMPLES:
# Python FastAPI with Uvicorn: uvicorn main:app --reload --port 8000
# Python Flask: flask run --port 8000
# Node.js: node server.js

# Replace this with your actual backend start command:
# For example, if your main backend file is app.py in the backend/core directory
# and it uses uvicorn:

# Option 1: Uvicorn (adjust main:app and port as needed)
echo "Python Uvicorn server starting on http://localhost:8000"
python -m uvicorn core.main:app --reload --port 8000

# Option 2: Simple Python script (if your backend is a simple script)
# echo "Python script backend starting..."
# python main.py

echo "------------------------------------"
echo "🚪 Backend server process exited." 