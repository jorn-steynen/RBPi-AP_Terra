# AP Terra – Raspberry Pi Installation Guide 🚀

This guide installs all required services, scripts, and configurations for the **AP Terra** Raspberry Pi setup in one go — no need to manually clone or configure anything.

---

## 📦 Requirements

- Raspberry Pi with Raspbian/Debian-based OS
- Internet access
- SSH or terminal access with sudo permissions

---

## 🛠 Quick Install

1. **Install Git** (if not already installed):
```bash
sudo apt update && sudo apt install git -y
```

2. **Download and run the install script**:
```bash
curl -O https://raw.githubusercontent.com/jorn-steynen/RBPi-AP_Terra/main/install.sh
chmod +x install.sh
./install.sh
```

3. **Follow the prompts**:
   - Confirm or change the username
   - The script auto-clones the project into `/home/<user>/RBPi-AP_Terra`
   - Sets up services, cronjobs, log rotation, and optional VPN

---

## 🔧 What Gets Installed

- Systemd services:
  - `antenna-mqtt.service` – reads LTE antenna signal
  - `solar-mqtt.service` – reads MPPT solar data
  - `dht11.service` – reads DHT11 sensor data
- Cronjobs:
  - Scheduled video recordings
  - Camera power toggling
  - Watchdog monitoring every 10 min
- SSD mount config (via `/etc/fstab`)
- Log rotation for `/mnt/ssd/logs/*.log`
- Health check with `system_health.py`
- Optional WireGuard VPN tunnel

---

## 🧠 Good to Know

- The install script is safe to re-run anytime.
- Logs go to SSD to preserve SD card life.
- If the repo folder already exists, cloning is skipped.
- Make sure your SSD is connected before running.

---

Ready to go? You're one command away from getting your remote Pi setup rolling! 🌍📡⚡
