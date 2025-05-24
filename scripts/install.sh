#!/bin/bash

# AIDEN Agent Platform - Installation Script
# This script installs all dependencies for both backend and frontend

set -e  # Exit on any error

echo "🚀 Installing AIDEN Agent Platform..."
echo "====================================="

# Check if we're in the correct directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the AIDEN project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Error: Python 3 is required but not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ Error: Node.js and npm are required but not installed"
    echo "Please install Node.js 16 or higher"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in backend directory"
    exit 1
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "✅ Backend dependencies installed (including Agno, FastAPI, and Database support)"

# Go back to root and install frontend dependencies
cd ..
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend

if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in frontend directory"
    exit 1
fi

npm install

# Install Tailwind CSS if not already installed
if ! npm list tailwindcss >/dev/null 2>&1; then
    echo "📦 Installing Tailwind CSS..."
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
fi

# Install marked for markdown rendering if not already installed
if ! npm list marked >/dev/null 2>&1; then
    echo "📦 Installing marked for markdown rendering..."
    npm install marked
    npm install @types/marked -D
fi

echo "✅ Frontend dependencies installed"

# Go back to root
cd ..

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo ""
    echo "📝 Creating .env.example file..."
    cat > .env.example << EOF
# Copy this file to .env and fill in your actual API key
# Get your API key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-google-api-key-here

# Optional: Set environment
ENVIRONMENT=development

# Optional: API configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Database configuration (SQLite file)
# DB_FILE=conversation_history.db
EOF
fi

echo ""
echo "🎉 Installation completed successfully!"
echo "====================================="
echo ""
echo "📋 New features installed:"
echo "  • Long-term memory with SQLite database"
echo "  • Real-time streaming of agent responses"
echo "  • Live tool execution visualization"
echo "  • Custom AIDEN branding and UI improvements"
echo ""
echo "📋 Next steps:"
echo "1. Get your Google API key from: https://aistudio.google.com/app/apikey"
echo "2. Copy .env.example to .env and add your API key:"
echo "   cp .env.example .env"
echo "   # Edit .env file and add your GOOGLE_API_KEY"
echo ""
echo "3. Run the platform:"
echo "   ./scripts/run.sh"
echo ""
echo "🔗 URLs after starting:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs" 