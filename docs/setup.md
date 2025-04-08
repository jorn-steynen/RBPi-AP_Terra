# Setup Instructions

## Initial Setup
Follow these steps to set up the Raspberry Pi for the African River Monitoring Project. These instructions are designed to work on Raspberry Pi OS (Debian Bookworm) with Python 3.11 or later.

1. **Install Dependencies:**
   Install all required system packages and Python libraries.

   ```bash
   sudo apt update
   sudo apt install python3-pip python3-paho-mqtt python3-serial python3-rpi.gpio snmp ffmpeg rsync chrony sl vim -y
