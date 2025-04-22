#!/bin/bash

# Configuration
RTSP_URL="rtsp://admin:DitIsGoed@192.168.100.252:554/Streaming/Channels/101"
VIDEO_DIR="/media/usb/videos"  # Default, will be overridden
LOG_FILE="/media/usb/logs/video_capture.log"  # Default, will be overridden
SERVER_IP="10.8.0.6" # External server IP
SERVER_USER="ape"
SERVER_PATH="/home/ape/uganda_tests/video2"

VIDEO_LENGTH=5  # Length of each captured video in seconds

TEMP_DIR="/dev/shm"  # Temporary RAM storage if USB is unavailable
SSD_MOUNT_POINT="/mnt/ssd"  # New mount point for SSD
SSD_DEVICE="/dev/sda1"  # Adjust based on lsblk output

# Check if SSD is mounted
if mountpoint -q "$SSD_MOUNT_POINT"; then
    echo "[INFO] SSD is already mounted at $SSD_MOUNT_POINT."
    # Ensure USER can write to it
    sudo chown uganda2:uganda2 "$SSD_MOUNT_POINT"
    VIDEO_DIR="$SSD_MOUNT_POINT/videos"
    LOG_FILE="$SSD_MOUNT_POINT/logs/video_capture.log"
else
    echo "[WARNING] SSD not mounted. Attempting to mount..."

    # Ensure mount point exists
    sudo mkdir -p "$SSD_MOUNT_POINT"

    # Attempt to mount the SSD with error output for diagnostics
    if output=$(sudo mount -t ext4 "$SSD_DEVICE" "$SSD_MOUNT_POINT" 2>&1); then
        echo "[INFO] Successfully mounted SSD at $SSD_MOUNT_POINT."
        sudo chown uganda2:uganda2 "$SSD_MOUNT_POINT"  # Ensure USER can write
        VIDEO_DIR="$SSD_MOUNT_POINT/videos"
        LOG_FILE="$SSD_MOUNT_POINT/logs/video_capture.log"
    else
        echo "[ERROR] Failed to mount SSD: $output"
        echo "[ERROR] Falling back to RAM storage at $TEMP_DIR."
        VIDEO_DIR="$TEMP_DIR/videos"
        LOG_FILE="$TEMP_DIR/logs/video_capture.log"
    fi
fi

# Display final storage location
echo "[INFO] Using $VIDEO_DIR for video storage."

# Ensure time is synced
echo "[INFO] Synchronizing time..."
sudo chronyc waitsync
if [ $? -eq 0 ]; then
    echo "[INFO] Time synchronized successfully."
else
    echo "[ERROR] Time sync failed. Proceeding with system time."
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Time sync failed." >> "$LOG_FILE"
fi

# Create necessary directories
mkdir -p "$VIDEO_DIR" "$(dirname "$LOG_FILE")" "$VIDEO_DIR/pending_uploads"

# Check internet connection before attempting upload
echo "[INFO] Checking internet connectivity..."
if ! ping -c 2 8.8.8.8 &> /dev/null; then
    echo "[WARNING] No internet connection. Saving file for later transfer."
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [WARNING] No internet connection detected." >> "$LOG_FILE"
fi

# Check disk space before capturing
#AVAILABLE_SPACE=$(df "$VIDEO_DIR" | tail -1 | awk '{print $4}')
#MIN_REQUIRED_SPACE=50000  # Minimum space in KB (adjust as needed)

#if [ "$AVAILABLE_SPACE" -lt "$MIN_REQUIRED_SPACE" ]; then
#    echo "[ERROR] Not enough disk space to capture video. Required: $MIN_REQUIRED_SPACE KB, Available: $AVAILABLE_SPACE KB"
#   agnes echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Insufficient disk space." >> "$LOG_FILE"
#    sudo reboot
#fi


# Capture video and retry ffmpeg capture up to 3 times if it fails
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
VIDEO_FILE="$VIDEO_DIR/video_$TIMESTAMP.mp4"
CAPTURE_ATTEMPTS=0
MAX_CAPTURE_RETRIES=3

until ffmpeg -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i "$RTSP_URL" -t $VIDEO_LENGTH -c copy -y "$VIDEO_FILE"; do
    ((CAPTURE_ATTEMPTS++))
    echo "[ERROR] ffmpeg capture failed. Attempt $CAPTURE_ATTEMPTS/$MAX_CAPTURE_RETRIES."
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] ffmpeg capture failed on attempt $CAPTURE_ATTEMPTS." >> "$LOG_FILE"
    if [ "$CAPTURE_ATTEMPTS" -ge "$MAX_CAPTURE_RETRIES" ]; then
        echo "[ERROR] Max retries reached. Skipping this cycle."
        exit 1
    fi
    sleep 2
done

# Verify video integrity
if [ ! -s "$VIDEO_FILE" ]; then
    echo "[ERROR] Video file is empty or missing: $VIDEO_FILE"
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Video file is empty or missing: $VIDEO_FILE" >> "$LOG_FILE"
    exit 1
fi

if ! ffprobe "$VIDEO_FILE" > /dev/null 2>&1; then
    echo "[ERROR] Corrupted video file detected: $VIDEO_FILE"
    echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Corrupted video file detected: $VIDEO_FILE" >> "$LOG_FILE"
    exit 1
fi


# Upload the video with retry logic
MAX_RETRIES=3
RETRY_COUNT=0

echo "[INFO] Sending video to network storage..."
until rsync -avz --partial --progress "$VIDEO_FILE" "$SERVER_USER@$SERVER_IP:$SERVER_PATH"; do
    ((RETRY_COUNT++))
    echo "[WARNING] Attempt $RETRY_COUNT of $MAX_RETRIES to reach the server failed." >> "$LOG_FILE"
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "[WARNING] Data transfer failed after $MAX_RETRIES attempts. Saving file for later transfer."
        mv "$VIDEO_FILE" "$VIDEO_DIR/pending_uploads/"
        break
    fi
    echo "[ERROR] Data transfer failed. Retrying in 3 seconds... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

# Clean up if upload was successful
if [ ! -f "$VIDEO_DIR/pending_uploads/$(basename $VIDEO_FILE)" ]; then
    echo "[INFO] Cleaning up uploaded video..."
    rm -f "$VIDEO_FILE"
fi

# Clean up if upload was successful (andere optie)
#if ssh "$SERVER_USER@$SERVER_IP" "test -f $SERVER_PATH/$(basename $VIDEO_FILE)"; then
#    echo "[INFO] Verified upload on server. Cleaning up local copy..."
#    rm -f "$VIDEO_FILE"
#else
#    echo "[WARNING] Upload might not have completed. Keeping file for now."
#fi


# Attempt to upload any pending files from previous sessions
echo "[INFO] Checking for pending uploads..."
for FILE in "$VIDEO_DIR/pending_uploads/"*; do
    [ -e "$FILE" ] || continue
    echo "[INFO] Attempting to upload pending file: $(basename "$FILE")"
    if rsync -avz --partial --progress "$FILE" "$SERVER_USER@$SERVER_IP:$SERVER_PATH"; then
        echo "[INFO] Successfully uploaded pending file: $(basename "$FILE")"
        rm -f "$FILE"
    else
        echo "[ERROR] Failed to upload pending file: $(basename "$FILE")"
        echo "$(date +"%Y-%m-%d %H:%M:%S") - [ERROR] Failed to upload pending file: $(basename "$FILE")" >> "$LOG_FILE"
    fi
done

# If SSD was mounted during this script, unmount it on exit
if [ "$VIDEO_DIR" = "$SSD_MOUNT_POINT/videos" ]; then
    echo "[INFO] Unmounting SSD from $SSD_MOUNT_POINT..."
    sudo umount "$SSD_MOUNT_POINT" && echo "[INFO] SSD unmounted successfully." || echo "[WARNING] Failed to unmount SSD."
fi

# Shutdown gracefully to save power
# echo "[INFO] Shutting down to conserve power..."
# sudo shutdown now
