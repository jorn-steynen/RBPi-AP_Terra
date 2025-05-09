#!/bin/bash

echo "===== 📋 System Health Check ====="

# ✅ Function to print detailed service status with clear icons
print_service_status() {
    SERVICE_NAME="$1"
    LABEL="$2"

    echo -e "\n🔧 $LABEL ($SERVICE_NAME):"
    ENABLED=$(systemctl is-enabled "$SERVICE_NAME" 2>/dev/null)
    ACTIVE_STATE=$(systemctl show -p ActiveState --value "$SERVICE_NAME" 2>/dev/null)
    SUB_STATE=$(systemctl show -p SubState --value "$SERVICE_NAME" 2>/dev/null)

    echo "Enabled: $ENABLED"
    echo "ActiveState: $ACTIVE_STATE"
    echo "SubState: $SUB_STATE"

    if [ "$ACTIVE_STATE" = "active" ]; then
        echo -e "\e[32m[✅] $SERVICE_NAME is running\e[0m"
    elif [ "$ACTIVE_STATE" = "inactive" ]; then
        echo -e "\e[33m[⚠️] $SERVICE_NAME is inactive (might be expected)\e[0m"
    elif [ "$ACTIVE_STATE" = "failed" ]; then
        echo -e "\e[31m[❌] $SERVICE_NAME has failed\e[0m"
    else
        echo -e "\e[33m[ℹ️] $SERVICE_NAME status: $ACTIVE_STATE / $SUB_STATE\e[0m"
    fi
}

# 🔐 WireGuard VPN (adjust wg0 if needed)
print_service_status "wg-quick@wg0" "WireGuard VPN"

# 🌡️ DHT11 Sensor Service
print_service_status "dht11" "DHT11 Sensor Service"

# 🔋 MPPT MQTT Service
print_service_status "mppt-mqtt" "MPPT MQTT Service"

# 📡 Router MQTT Service
print_service_status "router-mqtt" "Router MQTT Service"

# 🔄 Logrotate Timer (if it exists)
if systemctl list-units --type=timer | grep -q "logrotate.timer"; then
    print_service_status "logrotate.timer" "Logrotate Timer"
else
    echo -e "\n🔄 Logrotate Timer:"
    echo "[ℹ️] No logrotate.timer found (might be cron-based on this system)."
fi

# 💾 Disk Space (robust)
echo -e "\n💾 Disk Space:"
MOUNTS=("/mnt/ssd" "/media/usb" "/")

for MOUNT in "${MOUNTS[@]}"; do
    if mountpoint -q "$MOUNT"; then
        echo -e "\nDisk usage for $MOUNT:"
        df -h "$MOUNT"
    else
        echo "$MOUNT is not mounted."
    fi
done

# 🧠 Memory usage
echo -e "\n🧠 Memory Usage:"
free -h

# ⚙️ CPU Load
echo -e "\n⚙️ CPU Load (last 1, 5, 15 min):"
uptime | awk -F'load average:' '{ print $2 }'

# 🌡️ CPU Temperature
echo -e "\n🌡️ CPU Temperature:"
if command -v vcgencmd &> /dev/null; then
    TEMP=$(vcgencmd measure_temp | awk -F"=" '{print $2}')
    echo "CPU Temp: $TEMP"
elif [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    RAW_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
    TEMP_C=$(awk "BEGIN {printf \"%.1f°C\", $RAW_TEMP/1000}")
    echo "CPU Temp: $TEMP_C"
else
    echo "[WARNING] Could not determine CPU temperature ❌"
fi

# 📂 Pending uploads
VIDEO_DIR="/mnt/ssd/videos/pending_uploads"
echo -e "\n📂 Pending Uploads in $VIDEO_DIR:"
if [ -d "$VIDEO_DIR" ]; then
    ls -lh "$VIDEO_DIR"
else
    echo "No pending uploads directory found."
fi

# 🗓️ User cronjobs (starting from '# m h  dom mon dow')
echo -e "\n⏲️ User Cronjobs:"
CRONTAB_CONTENT=$(crontab -l 2>/dev/null)
if [ -n "$CRONTAB_CONTENT" ]; then
    # Only display lines starting from '# m h  dom mon dow'
    echo "$CRONTAB_CONTENT" | awk '/^# m h/ {p=1} p'
else
    echo "[WARNING] No cronjobs found for current user ❌"
fi

# 📝 Recent Watchdog Log
WATCHDOG_LOG="/mnt/ssd/logs/watchdog.log"
echo -e "\n📝 Recent Watchdog Log:"
if [ -f "$WATCHDOG_LOG" ]; then
    tail -n 10 "$WATCHDOG_LOG"
else
    echo "No watchdog log file found."
fi

echo -e "\n✅ Health check completed at $(date -Iseconds)."

