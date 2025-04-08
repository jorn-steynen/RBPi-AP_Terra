# Uganda PYORC Project (RBPi-AP_Terra)

This repository contains scripts, services, and documentation for a remote monitoring system deployed on a riverbank in Uganda. The system uses a Raspberry Pi to collect video, solar (MPPT) data, and LTE signal metrics, sending the data to a remote MQTT broker (`mqtt.iot-ap.be`) for analysis.

## Structure
- **scripts/**: Active scripts for data collection and processing.
  - **antenna_readout/**: `router.py` - Reads LTE metrics (RSSI, RSRQ, RSRP, SINR) from the MikroTik router via SNMP and publishes to MQTT topic `router/1`.
  - **camera_toggle/**: `toggle_device.py` - Toggles the camera power on/off via a relay.
  - **solar_readout/**: `read_mppt.py` - Reads MPPT data (voltage, current, power, etc.) via serial port and publishes to MQTT topic `mppt/data2`.
  - **video_recordings/**:
    - `videoscript.sh` - Captures video from the camera and stores it on the SSD. (The SSD unmounts after this script runs to conserve battery!)
- **services/**: Systemd service files to run scripts on boot.
  - `mppt-mqtt.service` - Runs `read_mppt.py`.
  - `router-mqtt.service` - Runs `router.py`.
- **legacy/**: Older versions of scripts, kept for reference.
  - **solar_readout_old/**: Older MPPT scripts (`read_mppt1.py`, `read_mppt2.py`, `read_mppt.py`).
- **docs/**: Documentation.
  - `guidebook.md` - Step-by-step guides for setup and troubleshooting.
  - `setup.md` - Initial setup instructions.
  - `troubleshooting.md` - Common issues and solutions.

## Cronjobs
- Video recording: Runs `videoscript.sh` hourly from 7:00 to 18:00.
- Camera toggle: Turns the camera on at 6:57–17:57 and off at 7:05–18:05 to conserve battery

## Setup
See `docs/setup.md` for installation instructions.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue.
