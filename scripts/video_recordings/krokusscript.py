#!/bin/bash

# Configuration
RTSP_URL="rtsp://admin:DitIsGoed!@192.168.88.9:554/Streaming/Channels/101"
SERVER_IP="10.8.0.6" # External server IP
SERVER_USER="ape"
SERVER_PATH="/home/ape/video"
VIDEO_LENGTH=5  # Length of each captured video in seconds
CAPTURE_INTERVAL=1800  # Capture every 30 minutes (1800 seconds)
TEMP_DIR="/dev/shm"  # Temporary RAM storage

while true; do
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    VIDEO_FILE="$TEMP_DIR/video_$TIMESTAMP.mp4"

    # Capture video
    ffmpeg -rtsp_transport tcp -i "$RTSP_URL" -t $VIDEO_LENGTH -c copy -y "$VIDEO_FILE"
    
    # Upload the video
    rsync -avz --partial --progress "$VIDEO_FILE" "$SERVER_USER@$SERVER_IP:$SERVER_PATH" && rm -f "$VIDEO_FILE"
    
    # Sleep until next capture
    sleep $CAPTURE_INTERVAL
done

