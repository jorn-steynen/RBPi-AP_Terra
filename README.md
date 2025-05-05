# Uganda PYORC Project (RBPi-AP\_Terra)

This repository contains scripts, services, and documentation for a remote monitoring system deployed on a riverbank in Uganda. The system uses a Raspberry Pi to collect video, solar (MPPT) data, environmental metrics (like temperature/humidity), and LTE signal quality. Data is sent to a remote MQTT broker (`mqtt.iot-ap.be`) for analysis.

---

## 📁 Structure

### `scripts/` — Active scripts for data collection and processing

- **`antenna_readout/router.py`**: Reads LTE metrics (RSSI, RSRQ, RSRP, SINR) from the MikroTik router via SNMP and publishes to topic `router/1`.
- **`camera_toggle/toggle_device.py`**: Toggles the camera power on/off via a relay.
- **`solar_readout/read_mppt.py`**: Reads MPPT data (voltage, current, power, etc.) via serial port and publishes to topic `mppt/data2`.
- **`video_recordings/videoscript.sh`**: Captures video from the camera and stores it on the SSD. The SSD unmounts after this script runs to conserve battery.
- **`dht11\_mqtt.py`**: Reads temperature and humidity data from a DHT11 sensor connected to the Pi and publishes to MQTT.
- **`watchdog\_checker.py`**: Periodically checks system health or connectivity and logs/reports issues. Can be extended to reboot or alert.

### `services/` — Systemd service files to run key scripts on boot

- **`mppt-mqtt.service`** – Runs `read_mppt.py`
- **`router-mqtt.service`** – Runs `router.py`
- **`dht11.service`** – Runs `read_dht11.py`



### `configs/` — Configuration templates

- **`mikrotik_lte_export.rsc`** *(template)* – MikroTik LTE router export config
- Includes a `README.md` with instructions on how to import and adapt the config safely.

### `legacy/` — Old scripts (kept for reference)

- **`solar_readout_old/`**: Contains `read_mppt1.py`, `read_mppt2.py`, and previous versions of MPPT logic.

### `docs/` — Full documentation

- **`guidebook.md`** – Comprehensive guide for installation, configuration, and troubleshooting.

---

## 🕒 Cronjobs

- **Video recording**: `videoscript.sh` runs hourly between 07:00 and 18:00.
- **Camera toggle**: Turns camera on at 06:57–17:57 and off at 07:05–18:05.
- **Watchdog check**: `check_system.py` checks the logs every 10 minutes.
---

## ⚙️ Setup & Installation

Please follow the full installation and configuration instructions in [`docs/guidebook.md`](docs/guidebook.md).

---

## 🤝 Contributing

Contributions are welcome! If you want to suggest improvements or report bugs, feel free to open an issue or submit a pull request.

---

## 📌 Notes

- The project is part of a collaboration with AP Hogeschool, VUB and Mountains of the Moon University in Uganda.
- The setup is optimized for power efficiency and long-term outdoor deployment.
- Data is transmitted via 4G and accessed remotely over a VPN.
- Designed to be low-maintenance and robust against power and network issues.
- Log files are rotated automatically using logrotate to conserve SSD space.

---

## 🧰 Useful Git Commands

```bash
# Clone the repository
git clone https://github.com/jorn-steynen/RBPi-AP_Terra.git

# Check the status of your changes
git status

# Add and commit local changes
git add .
git commit -m "Your message"

# Pull latest changes from GitHub
git pull origin main

# Push your changes back to GitHub
git push origin main
```

