#!/bin/bash
# Start production server on Render

set -e  # Exit immediately if a command exits with a non-zero status

# Install FFmpeg if it is not already installed.
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found. Installing..."
    ./scripts/install_ffmpeg.sh
fi

# Create required directories if they don't exist.
mkdir -p "$UPLOAD_FOLDER"
mkdir -p "$GIF_OUTPUT_DIR"

# Start Gunicorn
echo "Starting Gunicorn on port $PORT..."
gunicorn "app:create_app()" \
  --workers 4 \
  --bind 0.0.0.0:"$PORT" \
  --timeout 300 \
  --worker-class gthread \
  --threads 2 \
  --access-logfile - \
  --error-logfile -
