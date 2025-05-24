#!/bin/bash

# AIDEN Agent Platform - Run Script
# This script starts both backend and frontend in development mode

set -e  # Exit on any error

echo "🚀 Starting AIDEN Agent Platform..."
echo "=================================="

# Check if we're in the correct directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the AIDEN project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes on cleanup
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup SIGINT SIGTERM

# Check prerequisites
if ! command_exists python3; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please run: ./scripts/install.sh"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ Error: Node.js/npm is not installed"
    echo "Please run: ./scripts/install.sh"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "backend/__pycache__" ] && [ ! -f "backend/.installed" ]; then
    echo "⚠️  Backend dependencies might not be installed"
    echo "Please run: ./scripts/install.sh"
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not installed"
    echo "Please run: ./scripts/install.sh"
    exit 1
fi

# Check if aiosqlite is installed (for database features)
python3 -c "import aiosqlite" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  The aiosqlite module is not installed"
    echo "Please run: ./scripts/install.sh or pip install aiosqlite"
    exit 1
fi

# Check for .env file and API key
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "Please copy .env.example to .env and add your GOOGLE_API_KEY"
    echo "cp .env.example .env"
    exit 1
fi

# Source the .env file
source .env 2>/dev/null || true

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-api-key-here" ]; then
    echo "⚠️  GOOGLE_API_KEY not set in .env file"
    echo "Please edit .env and add your Google API key"
    echo "Get it from: https://aistudio.google.com/app/apikey"
    exit 1
fi

# Check if ports are available
if port_in_use 8000; then
    echo "⚠️  Port 8000 is already in use (backend)"
    echo "Please stop the process using port 8000 or change the port in backend/config.py"
    exit 1
fi

if port_in_use 3000; then
    echo "⚠️  Port 3000 is already in use (frontend)"
    echo "Please stop the process using port 3000"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Start backend
echo "🔧 Starting backend server with database & streaming..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! port_in_use 8000; then
    echo "❌ Backend failed to start on port 8000"
    cleanup
    exit 1
fi

echo "✅ Backend server started (PID: $BACKEND_PID)"
echo "   Long-term memory database initialized"
echo "   Server-Sent Events streaming enabled"

# Start frontend
echo "🎨 Starting frontend with streaming visualization..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! port_in_use 3000; then
    echo "❌ Frontend failed to start on port 3000"
    cleanup
    exit 1
fi

echo "✅ Frontend development server started (PID: $FRONTEND_PID)"
echo ""
echo "🎉 AIDEN Agent Platform is running!"
echo "=================================="
echo ""
echo "🔗 URLs:"
echo "   🎨 Frontend (Chat UI):  http://localhost:3000"
echo "   🔧 Backend API:         http://localhost:8000"
echo "   📚 API Documentation:   http://localhost:8000/docs"
echo "   ❤️  Health Check:       http://localhost:8000/health"
echo ""
echo "📝 Features:"
echo "   💾 Long-term memory database: SQLite"
echo "   🔍 Web search capability: DuckDuckGo"
echo "   📡 Real-time agent activity streaming"
echo "   🖌️ Custom AIDEN branding"
echo ""
echo "🛑 To stop: Press Ctrl+C"
echo ""

# Wait for processes to complete
wait 