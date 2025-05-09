#!/bin/bash

echo "===== 📋 System Health Check ====="

# Check WireGuard VPN status (replace wg0 if your interface is different)
echo -e "\n🔐 WireGuard VPN Status:"
if systemctl is-active --quiet wg-quick@wg0; then
    echo "[OK] WireGuard (wg0) is running ✅"
else
    echo "[ERROR] WireGuard (wg0) is NOT running ❌"
fi

# Check DHT11 sensor service
echo -e "\n🌡️ DHT11 Sensor Service:"
if systemctl is-active --quiet dht11; then
    echo "[OK] dht11.service is running ✅"
else
    echo "[ERROR] dht11.service is NOT running ❌"
fi

# Check MPPT MQTT publisher service
echo -e "\n🔋 MPPT MQTT Service:"
if systemctl is-active --quiet mppt-mqtt; then
    echo "[OK] mppt-mqtt.service is running ✅"
else
    echo "[ERROR] mppt-mqtt.service is NOT running ❌"
fi

# Check Router MQTT publisher service
echo -e "\n📡 Router MQTT Service:"
if systemctl is-active --quiet router-mqtt; then
    echo "[OK] router-mqtt.service is running ✅"
else
    echo "[ERROR] router-mqtt.service is NOT running ❌"
fi

# Check Watchdog service
echo -e "\n👀 Watchdog Service:"
if systemctl is-active --quiet watchdog; then
    echo "[OK] watchdog.service is running ✅"
else
    echo "[ERROR] watchdog.service is NOT running ❌"
fi

# Check Disk space (important mounts)
echo -e "\n💾 Disk Space:"
df -h | grep -E 'Filesystem|/mnt/ssd|/media/usb|/dev/root'

# Check Memory usage
echo -e "\n🧠 Memory Usage:"
free -h

# Check CPU load
echo -e "\n⚙️ CPU Load (last 1, 5, 15 min):"
uptime | awk -F'load average:' '{ print $2 }'

# Check pending uploads (adjust if your path is different)
VIDEO_DIR="/mnt/ssd/videos/pending_uploads"
echo -e "\n📂 Pending Uploads in $VIDEO_DIR:"
if [ -d "$VIDEO_DIR" ]; then
    ls -lh "$VIDEO_DIR"
else
    echo "No pending uploads directory found."
fi

# Show recent watchdog log lines
WATCHDOG_LOG="/mnt/ssd/logs/watchdog.log"
echo -e "\n📝 Recent Watchdog Log:"
if [ -f "$WATCHDOG_LOG" ]; then
    tail -n 10 "$WATCHDOG_LOG"
else
    echo "No watchdog log file found."
fi

echo -e "\n✅ Health check completed at $(date -Iseconds)."
