# Uganda PYORC Project (RBPi-AP_Terra)

This repository contains scripts, services, and documentation for a remote monitoring system deployed on a riverbank in Uganda. The system uses a Raspberry Pi to collect video, solar (MPPT) data, and LTE signal metrics, sending the data to a remote MQTT broker (`mqtt.iot-ap.be`) for analysis.

---

## 📁 Structure

### `scripts/` — Active scripts for data collection and processing
- **`antenna_readout/router.py`**: Reads LTE metrics (RSSI, RSRQ, RSRP, SINR) from the MikroTik router via SNMP and publishes to topic `router/1`.
- **`camera_toggle/toggle_device.py`**: Toggles the camera power on/off via a relay.
- **`solar_readout/read_mppt.py`**: Reads MPPT data (voltage, current, power, etc.) via serial port and publishes to topic `mppt/data2`.
- **`video_recordings/videoscript.sh`**: Captures video from the camera and stores it on the SSD. (The SSD unmounts after this script runs to conserve battery.)

### `services/` — Systemd service files to run key scripts on boot
- **`mppt-mqtt.service`** – Runs `read_mppt.py`
- **`router-mqtt.service`** – Runs `router.py`

### `legacy/` — Old scripts (kept for reference)
- **`solar_readout_old/`**: Contains `read_mppt1.py`, `read_mppt2.py`, and previous versions of MPPT logic.

### `docs/` — Full documentation
- **`guidebook.md`** – Comprehensive guide for installation, configuration, and troubleshooting.

---

## 🕒 Cronjobs
- **Video recording**: `videoscript.sh` runs hourly between 07:00 and 18:00.
- **Camera toggle**: Turns camera on at 06:57–17:57 and off at 07:05–18:05.

---

## ⚙️ Setup & Installation
Please follow the full installation and configuration instructions in [`docs/guidebook.md`](docs/guidebook.md).

---

##  Contributing
Contributions are welcome! If you want to suggest improvements or report bugs, feel free to open an issue or submit a pull request.

---

## 📌 Notes
- The project is part of a collaboration with Mountains of the Moon University in Uganda.
- The setup is optimized for power efficiency and long-term outdoor deployment.
- Data is transmitted via 4G and accessed remotely over a VPN.


