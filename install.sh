#!/bin/bash

# AIDEN Installation Script
# This script installs system dependencies and Python packages for AIDEN

set -e  # Exit on any error

echo "🚀 Installing AIDEN..."

# Check if running as root for system package installation
if [[ $EUID -eq 0 ]]; then
    echo "📦 Installing system dependencies..."
    
    # Update package list
    apt-get update
    
    # Install FFmpeg development libraries (required for PyAV/av package)
    apt-get install -y \
        ffmpeg \
        libavformat-dev \
        libavcodec-dev \
        libavdevice-dev \
        libavutil-dev \
        libavfilter-dev \
        libswscale-dev \
        libswresample-dev
    
    # Install audio libraries (required for PyAudio)
    apt-get install -y \
        portaudio19-dev \
        python3-pyaudio \
        libasound2-dev
    
    # Install build tools
    apt-get install -y \
        build-essential \
        pkg-config \
        python3-dev
    
    echo "✅ System dependencies installed successfully!"
else
    echo "⚠️  Note: Not running as root. If you encounter build errors, you may need to install system dependencies:"
    echo "   sudo apt-get update"
    echo "   sudo apt-get install -y ffmpeg libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libswresample-dev portaudio19-dev libasound2-dev build-essential pkg-config python3-dev"
fi

echo "🐍 Setting up Python environment..."

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

echo "📚 Installing Python dependencies..."

# Install Python packages
pip install -r requirements.txt

echo "🎉 AIDEN installation completed successfully!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To start AIDEN, run:"
echo "  python aiden_cli.py" 