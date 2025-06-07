#!/bin/bash
# Install FFmpeg with comprehensive codec support
# This script is adapted for Render's Ubuntu/Debian environment.

if command -v apt &> /dev/null; then
    echo "Detected apt package manager. Installing FFmpeg using apt..."
    sudo apt update
    sudo apt install -y ffmpeg

# For CentOS/RHEL (not expected on Render, but kept for completeness)
elif command -v yum &> /dev/null; then
    echo "Detected yum package manager. Installing FFmpeg using yum..."
    sudo yum install -y epel-release
    sudo yum update -y
    sudo yum install -y ffmpeg ffmpeg-devel

# For macOS (unlikely for Render deployment)
elif command -v brew &> /dev/null; then
    echo "Detected Homebrew. Installing FFmpeg using brew..."
    # Note: Options like --with-libvpx may no longer be supported in modern Homebrew.
    brew install ffmpeg
else
    echo "Unsupported OS. Please install FFmpeg manually."
    exit 1
fi

echo "FFmpeg installation complete:"
ffmpeg -version
