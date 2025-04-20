# Guidebook for Uganda PYORC project
## Raspberry Pi Setup Guide for AP Terra Project

This guide explains how to install and configure the AP Terra system on a Raspberry Pi. The goal is to make the installation process repeatable and understandable for future contributors or maintainers.

### 1. System Requirements
- Raspberry Pi (tested on Pi 4)
- Raspberry Pi OS (Lite recommended)
- External SSD
- 4G LTE MikroTik router (for SNMP readout)
- MPPT solar charge controller (Victron)
- IP Camera connected via RTSP

### 2. Required Software Packages
Install all system dependencies using `apt` (virtual environments are not used).

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-serial ffmpeg git wireguard -y
```

Install required Python packages globally:

```bash
sudo pip3 install paho-mqtt pyserial pysnmp
```

### 3. Clone the repository

```bash
git clone https://github.com/jorn-steynen/RBPi-AP_Terra.git
cd RBPi-AP_Terra
```

### 4. WireGuard VPN Setup
To enable remote access, the Raspberry Pi connects to a central WireGuard server managed at `wgeasy.iot-ap.be`. Each Raspberry Pi client receives a preconfigured `wg0.conf` file from the server administrator.

Follow these steps to activate the VPN:

1. Ensure WireGuard is installed:
```bash
sudo apt install wireguard -y
```

2. Open the config file location and paste the contents provided by the administrator:
```bash
sudo nano /etc/wireguard/wg0.conf
```

3. Example layout of the configuration file (for illustration only):
```ini
[Interface]
PrivateKey = <REDACTED>
Address = 10.8.0.10/24
DNS = 1.1.1.1

[Peer]
PublicKey = f5jC2dSqTYDpyWRuD+BgbbP8yYnt7JJ7MILZ6N3yxmI=
PresharedKey = <REDACTED>
AllowedIPs = 10.8.0.0/24
PersistentKeepalive = 25
Endpoint = wgeasy.iot-ap.be:51820
```

4. Enable and start the VPN:
```bash
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```

This will establish a persistent, secure connection to the AP Terra VPN network, allowing remote access to the device.

### 5. Services and Scheduled Tasks
Two main scripts run as systemd services. See the `services/` directory for example service files.

To install a service:

```bash
sudo cp services/example.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl enable example.service
sudo systemctl start example.service
```

Repeat this for the relevant services:
- mppt-mqtt.service
- router-mqtt.service

Other scripts, such as those for toggling the camera and recording video, are executed periodically via cronjobs instead of services. Make sure the crontab is configured accordingly.

To edit the crontab:
```bash
crontab -e
```
Then add entries such as:
```cron
# m h  dom mon dow   command
0 7-18 * * * /bin/bash /home/uganda2/uganda_tests/scripts/video_recordings/videoscript.sh
57 6-17 * * * /home/uganda2/uganda_tests/scripts/camera_toggle/toggle_device.py on
5 7-18 * * * /home/uganda2/uganda_tests/scripts/camera_toggle/toggle_device.py off
# Shutdown at 20:00 (uncomment to enable)
# 0 20 * * * /usr/sbin/shutdown -h now
```
Adjust the timing and paths as needed.

### 6. Notes
- Ensure your MQTT broker is reachable and the credentials are configured properly in each script.
- Make sure all USB devices (SSD, MPPT) are correctly mounted and assigned stable device names if needed.

### 7. To Do
- Document how to configure SNMP access on the MikroTik router
- Describe how to properly set up network interfaces for field use
- Add cronjob or watchdog if periodic checking is needed

---
This file is a work in progress. Please add to it whenever installation/configuration steps are updated.

