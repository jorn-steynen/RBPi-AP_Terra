#!/bin/bash

# Load .env from script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "[ERROR] .env file not found in $SCRIPT_DIR. Exiting."
    exit 1
fi

# Trap exits or signals for logging
trap 'echo "[ERROR] Script interrupted or failed at $(date -Iseconds)" >> "$LOG_FILE"; exit 1' INT TERM ERR

# Configuration
TEMP_DIR="/dev/shm"
SSD_MOUNT_POINT="/mnt/ssd"
SSD_DEVICE="/dev/sda1"

VIDEO_DIR="/media/usb/videos"
LOG_FILE="/media/usb/logs/video_capture.log"
STATUS_FILE="/mnt/ssd/status/video.status"

# Check SSD device and mount
if [ ! -b "$SSD_DEVICE" ]; then
    echo "[ERROR] SSD device $SSD_DEVICE not found. Falling back to RAM."
    USE_RAM=true
elif mountpoint -q "$SSD_MOUNT_POINT"; then
    echo "[INFO] SSD already mounted at $SSD_MOUNT_POINT."
    USE_RAM=false
else
    echo "[INFO] Attempting to mount SSD..."
    sudo mkdir -p "$SSD_MOUNT_POINT"
    if output=$(sudo mount -t ext4 "$SSD_DEVICE" "$SSD_MOUNT_POINT" 2>&1); then
        echo "[INFO] Mounted SSD successfully."
        sudo chown uganda2:uganda2 "$SSD_MOUNT_POINT"
        USE_RAM=false
    else
        echo "[ERROR] Failed to mount SSD: $output"
        USE_RAM=true
    fi
fi

# Set working paths based on SSD/RAM
if [ "$USE_RAM" = true ]; then
    echo "[INFO] Falling back to RAM at $TEMP_DIR."
    VIDEO_DIR="$TEMP_DIR/videos"
    LOG_FILE="$TEMP_DIR/logs/video_capture.log"
    STATUS_FILE="$TEMP_DIR/status/video.status"
else
    VIDEO_DIR="$SSD_MOUNT_POINT/videos"
    LOG_FILE="$SSD_MOUNT_POINT/logs/video_capture.log"
    STATUS_FILE="$SSD_MOUNT_POINT/status/video.status"
fi

mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$STATUS_FILE")"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[INFO] Using $VIDEO_DIR for video storage."

# Time sync
echo "[INFO] Synchronizing time..."
sudo chronyc waitsync
if [ $? -eq 0 ]; then
    echo "[INFO] Time synchronized successfully."
else
    echo "[ERROR] Time sync failed. Proceeding with system time."
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Time sync failed." >> "$LOG_FILE"
fi

mkdir -p "$VIDEO_DIR" "$VIDEO_DIR/pending_uploads"

# Check internet connectivity
echo "[INFO] Checking internet connectivity..."
if ! ping -c 2 8.8.8.8 &> /dev/null; then
    echo "[WARNING] No internet connection. Saving file for later transfer."
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [WARNING] No internet connection detected." >> "$LOG_FILE"
fi

# MinIO alias setup only if not already defined
if ! mc alias list | grep -q "$MINIO_ALIAS"; then
    mc alias set "$MINIO_ALIAS" "$MINIO_URL" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
fi

# Start video capture
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
VIDEO_FILE="$VIDEO_DIR/video_$TIMESTAMP.mp4"
REMOTE_FILE="$MINIO_PATH/video_$TIMESTAMP.mp4"
CAPTURE_ATTEMPTS=0
MAX_CAPTURE_RETRIES=3

until ffmpeg -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i "$RTSP_URL" -t "$VIDEO_LENGTH" -c copy -y "$VIDEO_FILE"; do
    ((CAPTURE_ATTEMPTS++))
    echo "[ERROR] ffmpeg capture failed. Attempt $CAPTURE_ATTEMPTS/$MAX_CAPTURE_RETRIES."
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] ffmpeg capture failed on attempt $CAPTURE_ATTEMPTS." >> "$LOG_FILE"
    echo "ERROR $(date -Iseconds) ffmpeg capture failed (attempt $CAPTURE_ATTEMPTS)" > "$STATUS_FILE"
    if [ "$CAPTURE_ATTEMPTS" -ge "$MAX_CAPTURE_RETRIES" ]; then
        echo "[ERROR] Max retries reached. Skipping this cycle."
        echo "ERROR $(date -Iseconds) Max capture retries reached" > "$STATUS_FILE"
        exit 1
    fi
    sleep 2
done

# Validate captured video
if [ ! -s "$VIDEO_FILE" ]; then
    echo "[ERROR] Video file is empty or missing: $VIDEO_FILE"
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Empty or missing video file." >> "$LOG_FILE"
    echo "ERROR $(date -Iseconds) empty or missing video file" > "$STATUS_FILE"
    exit 1
fi

if ! ffprobe "$VIDEO_FILE" > /dev/null 2>&1; then
    echo "[ERROR] Corrupted video file: $VIDEO_FILE"
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Corrupted video file." >> "$LOG_FILE"
    echo "ERROR $(date -Iseconds) corrupted video file" > "$STATUS_FILE"
    exit 1
fi

# Upload to MinIO
MAX_RETRIES=3
RETRY_COUNT=0

echo "[INFO] Uploading video to MinIO..."
until mc cp "$VIDEO_FILE" "$MINIO_ALIAS/$MINIO_BUCKET/$REMOTE_FILE"; do
    ((RETRY_COUNT++))
    echo "[WARNING] Upload attempt $RETRY_COUNT of $MAX_RETRIES failed." >> "$LOG_FILE"
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "[WARNING] Upload failed after $MAX_RETRIES attempts. Saving for later."
        mv "$VIDEO_FILE" "$VIDEO_DIR/pending_uploads/"
        echo "ERROR $(date -Iseconds) MinIO upload failed, file moved to pending_uploads" > "$STATUS_FILE"
        break
    fi
    echo "[ERROR] Upload failed. Retrying in 3 seconds... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

# Cleanup or success status
if [ ! -f "$VIDEO_DIR/pending_uploads/$(basename "$VIDEO_FILE")" ]; then
    echo "[INFO] Cleaning up uploaded video."
    rm -f "$VIDEO_FILE"
    echo "OK $(date -Iseconds) last_video=$(basename "$VIDEO_FILE")" > "$STATUS_FILE"
    echo "[INFO] Video processing completed successfully at $(date -Iseconds)" >> "$LOG_FILE"
fi

# Retry any pending uploads
echo "[INFO] Checking for pending uploads..."
for FILE in "$VIDEO_DIR/pending_uploads/"*; do
    [ -e "$FILE" ] || continue
    BASENAME="$(basename "$FILE")"
    echo "[INFO] Trying to upload pending file: $BASENAME"
    if mc cp "$FILE" "$MINIO_ALIAS/$MINIO_BUCKET/$MINIO_PATH/$BASENAME"; then
        echo "[INFO] Uploaded: $BASENAME"
        rm -f "$FILE"
    else
        echo "[ERROR] Failed upload: $BASENAME"
        echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Failed upload: $BASENAME" >> "$LOG_FILE"
        echo "ERROR $(date -Iseconds) pending upload failed: $BASENAME" > "$STATUS_FILE"
    fi
done

