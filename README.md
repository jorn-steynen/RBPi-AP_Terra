# Uganda PYORC (RBPi-AP_Terra)

This repository contains scripts, services, and documentation for a remote monitoring system deployed on a riverbank in Uganda. The system uses a Raspberry Pi to collect video, solar (MPPT) data, and LTE signal metrics, sending the data to a remote server for analysis.

## Structure
- **scripts/**: Scripts for data collection and processing.
  - **antenna_readout/**: Scripts for reading LTE metrics from the router.
  - **camera_toggle/**: Scripts for controlling the camera power.
  - **solar_readout/**: Scripts for reading MPPT data.
  - **solar_readout_old/**: Older versions of MPPT scripts.
  - **video_recordings/**: Scripts for capturing and uploading videos.
- **services/**: Systemd service files to run scripts on boot.
- **docs/**: Documentation, including setup guides and troubleshooting.

## Setup
See `docs/setup.md` for installation instructions.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue.
