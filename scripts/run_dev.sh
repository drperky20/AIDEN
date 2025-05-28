#!/bin/bash
# AIDEN V2 Development Run Script
# This script starts the backend API server and frontend development server.

# Set the script to exit immediately if any command fails
set -e

# Display ASCII art banner
echo ""
echo "    █████╗ ██╗██████╗ ███████╗███╗   ██╗    ██╗   ██╗██████╗ "
echo "   ██╔══██╗██║██╔══██╗██╔════╝████╗  ██║    ██║   ██║╚════██╗"
echo "   ███████║██║██║  ██║█████╗  ██╔██╗ ██║    ██║   ██║ █████╔╝"
echo "   ██╔══██║██║██║  ██║██╔══╝  ██║╚██╗██║    ╚██╗ ██╔╝██╔═══╝ "
echo "   ██║  ██║██║██████╔╝███████╗██║ ╚████║     ╚████╔╝ ███████╗"
echo "   ╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝      ╚═══╝  ╚══════╝"
echo ""
echo "   Personal AI Assistant powered by Agno & Gemini"
echo "   Version 2.0.0"
echo ""

# Define directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
DATA_DIR="$PROJECT_ROOT/data"
ENV_FILE="$PROJECT_ROOT/.env"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# Check if .env file exists, create from example if not
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        echo "⚠️  No .env file found. Creating from .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
        echo "⚠️  Please edit $ENV_FILE and set your API keys before continuing."
        exit 1
    else
        echo "⚠️  No .env or .env.example file found. Creating minimal .env..."
        cat > "$ENV_FILE" << EOF
# AIDEN V2 Environment Variables
# Please set your API keys below

# Google API Key for Gemini model
GOOGLE_API_KEY=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Environment
ENVIRONMENT=development
EOF
        echo "⚠️  Please edit $ENV_FILE and set your API keys before continuing."
        exit 1
    fi
fi

# Check for Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No active Python virtual environment detected."
    
    # Check if .venv exists in project root
    if [ -d "$PROJECT_ROOT/.venv" ] && [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
        echo "🔄 Activating existing virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    else
        echo "⚠️  No .venv directory found in project root."
        echo "   Please create and activate a virtual environment before running this script."
        echo "   Example:"
        echo "     python -m venv .venv"
        echo "     source .venv/bin/activate  # On macOS/Linux"
        echo "     .venv\\Scripts\\activate    # On Windows"
        exit 1
    fi
fi

# Check for required Python packages
echo "🔍 Checking for required Python packages..."
if ! python -c "import agno, fastapi, uvicorn" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r "$BACKEND_DIR/requirements.txt"
fi

# Function to start the backend server
start_backend() {
    echo "🚀 Starting AIDEN V2 backend API server..."
    cd "$PROJECT_ROOT"
    python -m uvicorn backend.api.main:app --host $(grep API_HOST "$ENV_FILE" | cut -d= -f2) --port $(grep API_PORT "$ENV_FILE" | cut -d= -f2) --reload --app-dir "$BACKEND_DIR"
}

# Function to start the frontend development server
start_frontend() {
    if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
        echo "🚀 Starting AIDEN V2 frontend development server..."
        cd "$FRONTEND_DIR"
        
        # Check if npm is installed
        if command -v npm >/dev/null 2>&1; then
            # Check if node_modules exists
            if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
                echo "📦 Installing frontend dependencies..."
                npm install
            fi
            npm run dev
        else
            echo "⚠️  npm not found. Skipping frontend startup."
            echo "   Please install Node.js and npm to run the frontend."
        fi
    else
        echo "⚠️  Frontend directory or package.json not found. Skipping frontend startup."
    fi
}

# Parse command line arguments
case "$1" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    *)
        # Default: start backend only
        echo "ℹ️  Starting backend only. Use './scripts/run_dev.sh frontend' to start the frontend."
        start_backend
        ;;
esac 