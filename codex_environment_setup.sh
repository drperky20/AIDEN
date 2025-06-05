#!/bin/bash

# ChatGPT Codex Environment Setup Script
# Place this in the "Advanced Settings" -> "Setup Script" in your Codex environment configuration

set -e

echo "🚀 Setting up AIDEN environment for Codex..."

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

echo "✅ Codex environment setup completed!" 