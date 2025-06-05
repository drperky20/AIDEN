#!/bin/bash

# AIDEN Installation Script for ChatGPT Codex Environment
# Based on OpenAI Codex environment limitations and capabilities

set -e  # Exit on any error

echo "🚀 Installing AIDEN for ChatGPT Codex..."

# Note: In Codex environment, scripts run as root already - no sudo needed
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
echo "📋 Next steps:"
echo "1. Set up your environment variables (.env file)"
echo "2. Configure your API keys"
echo "3. Run: python aiden_cli.py" 