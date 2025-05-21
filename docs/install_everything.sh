#!/bin/bash
set -e

echo "============================"
echo "   AP Terra Install Script  "
echo "============================"

# 0. Clone repo if not present
REPO_URL="https://github.com/jorn-steynen/RBPi-AP_Terra.git"
TARGET_DIR="/home/$USER/RBPi-AP_Terra"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Cloning project repo into $TARGET_DIR..."
    git clone "$REPO_URL" "$TARGET_DIR"
else
    echo "Project repo already exists at $TARGET_DIR"
fi

cd "$TARGET_DIR"

# 1. Ask for user
CURRENT_USER=$(whoami)
echo "Current user detected: $CURRENT_USER"
read -p "Do you want to use this user? [Y/n]: " USER_CONFIRM
if [[ "$USER_CONFIRM" =~ ^[Nn]$ ]]; then
    read -p "Enter new username: " NEW_USER
    if id "$NEW_USER" &>/dev/null; then
        echo "User exists. Continuing as $NEW_USER"
        USERNAME="$NEW_USER"
    else
        echo "Creating new user $NEW_USER..."
        sudo adduser "$NEW_USER"
        USERNAME="$NEW_USER"
    fi
else
    USERNAME="$CURRENT_USER"
fi

# 2. Install system dependencies
echo "Installing system packages..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git cron logrotate

# 3. Detect SSD UUID and update /etc/fstab
echo "Detecting SSD device..."
SSD_UUID=$(blkid | grep -E "/dev/sd[a-z][0-9]*" | grep ext4 | head -n1 | sed -n 's/.*UUID="\([^"]*\)".*/\1/p')
if [ -z "$SSD_UUID" ]; then
    echo "No SSD with ext4 found. Skipping fstab update."
else
    MOUNT_LINE="UUID=$SSD_UUID  /mnt/ssd  ext4  defaults,nofail,x-systemd.device-timeout=10  0  2"
    if ! grep -q "$SSD_UUID" /etc/fstab; then
        echo "Adding SSD to /etc/fstab..."
        echo "$MOUNT_LINE" | sudo tee -a /etc/fstab
    else
        echo "SSD already in /etc/fstab."
    fi
    sudo mkdir -p /mnt/ssd
    sudo mount -a
fi

# 4. Set up systemd services
SERVICE_DIR="./services"
SYSTEMD_DIR="/etc/systemd/system"

declare -A SERVICES=(
    ["antenna-mqtt.service"]="scripts/antenna_readout/router.py"
    ["solar-mqtt.service"]="scripts/solar_readout/read_mppt.py"
    ["dht11.service"]="scripts/dht11_mqtt.py"
)

echo "Setting up systemd services..."
for SERVICE_NAME in "${!SERVICES[@]}"; do
    SCRIPT_PATH="${SERVICES[$SERVICE_NAME]}"
    SERVICE_FILE="$SERVICE_DIR/$SERVICE_NAME"

    if [ -f "$SCRIPT_PATH" ]; then
        echo "Creating systemd service for $SERVICE_NAME..."
        sudo tee "$SYSTEMD_DIR/$SERVICE_NAME" > /dev/null <<EOF
[Unit]
Description=$SERVICE_NAME
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/$USERNAME/RBPi-AP_Terra/$SCRIPT_PATH
Restart=always
RestartSec=10
User=$USERNAME
WorkingDirectory=/home/$USERNAME/RBPi-AP_Terra/$(dirname $SCRIPT_PATH)
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
EOF
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        sudo systemctl start "$SERVICE_NAME"
    else
        echo "Warning: Script $SCRIPT_PATH not found!"
    fi
done

# 5. Install cronjobs
echo "Installing cronjobs..."
CRON_FILE="/tmp/new_cron"
crontab -l 2>/dev/null > "$CRON_FILE" || true

echo "* * * * * /home/$USERNAME/RBPi-AP_Terra/scripts/video_recordings/final_hakim.sh" >> "$CRON_FILE"
echo "57 6-17 * * * /usr/bin/python3 /home/$USERNAME/RBPi-AP_Terra/scripts/camera_toggle/toggle_device.py on" >> "$CRON_FILE"
echo "5 7-18 * * * /usr/bin/python3 /home/$USERNAME/RBPi-AP_Terra/scripts/camera_toggle/toggle_device.py off" >> "$CRON_FILE"
echo "*/10 * * * * /usr/bin/python3 /home/$USERNAME/RBPi-AP_Terra/scripts/watchdog_checker.py" >> "$CRON_FILE"
echo "0 7-18 * * * /home/$USERNAME/RBPi-AP_Terra/scripts/video_recordings/final_hakim.sh" >> "$CRON_FILE"

crontab "$CRON_FILE"
rm "$CRON_FILE"

# 6. Logrotate setup
LOGROTATE_CONF="/etc/logrotate.d/uganda_watchdog"
if [ ! -f "$LOGROTATE_CONF" ]; then
    echo "Setting up logrotate..."
    sudo tee "$LOGROTATE_CONF" > /dev/null <<EOF
/mnt/ssd/logs/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
fi

# 7. WireGuard VPN setup
read -p "Do you want to set up WireGuard now? [y/N]: " VPN_CONFIRM
if [[ "$VPN_CONFIRM" =~ ^[Yy]$ ]]; then
    sudo mkdir -p /etc/wireguard
    echo "Paste your WireGuard config below (end with CTRL+D):"
    sudo tee /etc/wireguard/wg0.conf > /dev/null
    sudo systemctl enable wg-quick@wg0
    sudo systemctl start wg-quick@wg0
    echo "WireGuard enabled."
else
    echo "Skipping VPN setup."
fi

# 8. Final system check
echo "Running final system health check..."
python3 scripts/system_health.py || echo "Health check failed!"

echo "✅ Installation complete."
