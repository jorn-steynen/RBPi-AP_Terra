#!/usr/bin/env python3
import subprocess
import sys
import os
import logging
from datetime import datetime

GPIO_PIN = 3  # BCM numbering (physical pin 5)
LOG_FILE = "/mnt/ssd/logs/toggle_device.log"

# Zorg dat de logdirectory bestaat
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Logging configureren (consistent met andere scripts)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def usage():
    print("Usage: toggle_device.py [on|off]")
    sys.exit(1)

if len(sys.argv) != 2 or sys.argv[1] not in ["on", "off"]:
    usage()

state = sys.argv[1]
action = "dh" if state == "on" else "dl"

try:
    subprocess.run(["raspi-gpio", "set", str(GPIO_PIN), "op", action], check=True)
    status = subprocess.check_output(["raspi-gpio", "get", str(GPIO_PIN)], text=True).strip()
    print(f"Device powered {'ON' if state == 'on' else 'OFF'} ({status})")
    logging.info(f"Toggled {state.upper()} - {status}")
except Exception as e:
    logging.error(f"Error toggling GPIO: {e}")
    print(f"Failed to toggle device: {e}")
    sys.exit(1)
