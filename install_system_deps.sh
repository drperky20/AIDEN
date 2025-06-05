#!/bin/bash

# Install system dependencies for AIDEN
echo "Installing system dependencies for AIDEN..."

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

echo "System dependencies installed successfully!" 