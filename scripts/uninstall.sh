#!/bin/bash

# Agno Gemini Agent - Uninstall Script
# This script removes dependencies and cleans up the project

echo "🗑️  Uninstalling Agno Gemini Agent..."
echo "====================================="

# Check if we're in the correct directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the AIDEN project root directory"
    exit 1
fi

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/N): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

echo "This will remove:"
echo "  • Python virtual environments and cache files"
echo "  • Node.js modules and build files"
echo "  • Temporary and log files"
echo "  • Configuration files (optional)"
echo ""

if ! confirm "Are you sure you want to continue?"; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🧹 Cleaning up..."

# Clean backend
echo "🔧 Cleaning backend..."
cd backend

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
find . -type f -name ".coverage" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove any virtual environment if present
if [ -d "venv" ]; then
    rm -rf venv
    echo "  ✅ Removed Python virtual environment"
fi

if [ -d ".venv" ]; then
    rm -rf .venv
    echo "  ✅ Removed Python virtual environment (.venv)"
fi

echo "  ✅ Cleaned Python cache files"

cd ..

# Clean frontend
echo "🎨 Cleaning frontend..."
cd frontend

# Remove node_modules
if [ -d "node_modules" ]; then
    rm -rf node_modules
    echo "  ✅ Removed node_modules"
fi

# Remove build files
if [ -d "dist" ]; then
    rm -rf dist
    echo "  ✅ Removed build directory"
fi

if [ -d "build" ]; then
    rm -rf build
    echo "  ✅ Removed build directory"
fi

# Remove lock files
if [ -f "package-lock.json" ]; then
    rm package-lock.json
    echo "  ✅ Removed package-lock.json"
fi

if [ -f "yarn.lock" ]; then
    rm yarn.lock
    echo "  ✅ Removed yarn.lock"
fi

# Remove cache directories
if [ -d ".next" ]; then
    rm -rf .next
    echo "  ✅ Removed .next cache"
fi

if [ -d ".nuxt" ]; then
    rm -rf .nuxt
    echo "  ✅ Removed .nuxt cache"
fi

echo "  ✅ Cleaned frontend files"

cd ..

# Clean root directory
echo "🗂️  Cleaning root directory..."

# Remove log files
find . -maxdepth 1 -name "*.log" -delete 2>/dev/null || true
find . -maxdepth 1 -name "*.log.*" -delete 2>/dev/null || true

# Remove temporary files
find . -maxdepth 1 -name "*.tmp" -delete 2>/dev/null || true
find . -maxdepth 1 -name "*.temp" -delete 2>/dev/null || true

echo "  ✅ Cleaned temporary files"

# Ask about configuration files
echo ""
if confirm "Do you want to remove configuration files (.env, .env.example)?"; then
    if [ -f ".env" ]; then
        rm .env
        echo "  ✅ Removed .env"
    fi
    if [ -f ".env.example" ]; then
        rm .env.example
        echo "  ✅ Removed .env.example"
    fi
    echo "  ✅ Configuration files removed"
else
    echo "  ⏭️  Keeping configuration files"
fi

# Ask about keeping project structure
echo ""
if confirm "Do you want to remove the entire project directory structure (WARNING: This will delete everything)?"; then
    cd ..
    PROJECT_DIR=$(basename "$OLDPWD")
    echo "🗑️  Removing entire project directory: $PROJECT_DIR"
    rm -rf "$PROJECT_DIR"
    echo ""
    echo "🎉 Project completely removed!"
    exit 0
fi

echo ""
echo "🎉 Cleanup completed!"
echo "===================="
echo ""
echo "📋 What was cleaned:"
echo "  ✅ Python cache files (__pycache__, *.pyc)"
echo "  ✅ Node.js modules and dependencies"
echo "  ✅ Build and temporary files"
echo "  ✅ Log files"
echo ""
echo "📋 What was kept:"
echo "  📁 Source code (backend/, frontend/, scripts/)"
echo "  📄 Documentation (README.md, QUICKSTART.md)"
if [ -f ".env" ] || [ -f ".env.example" ]; then
    echo "  ⚙️  Configuration files (if not removed)"
fi
echo ""
echo "💡 To reinstall dependencies:"
echo "   ./scripts/install.sh" 