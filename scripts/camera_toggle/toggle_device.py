#!/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime

GPIO_PIN = 3  # BCM numbering (physical pin 5)
LOG_FILE = "/mnt/ssd/logs/toggle_device.log"

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as logf:
        logf.write(f"{timestamp} - {message}\n")

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
    log(f"Toggled {state.upper()} - {status}")
except Exception as e:
    log(f"Error toggling GPIO: {e}")
    print(f"Failed to toggle device: {e}")
    sys.exit(1)

