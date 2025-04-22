#!/usr/bin/env python3
import os
import time
from datetime import datetime, timedelta
import logging

STATUS_DIR = "/mnt/ssd/status"
LOG_FILE = "/mnt/ssd/logs/watchdog.log"

# Custom max age for each file (in minutes)
FILE_TIMEOUTS = {
    "video.status": 130,    # allow 2+ hours
    "mppt.status": 5,
    "dht11.status": 5,
    "router.status": 5,
    "camera.status": 130    # camera toggles around same time as video
}

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def write_log(level, message):
    if level == "warning":
        logging.warning(message)
    else:
        logging.info(message)

def check_status_file(file):
    now = datetime.now()
    full_path = os.path.join(STATUS_DIR, file)

    if not os.path.isfile(full_path):
        write_log("warning", f"Missing status file: {file}")
        return

    # Night mode: skip checks for video/camera status outside of solar hours
    if file in ["video.status", "camera.status"]:
        if now.hour < 7 or now.hour > 19:
            write_log("info", f"Skipping {file} check (outside active hours)")
            return

    mtime = os.path.getmtime(full_path)
    age = now - datetime.fromtimestamp(mtime)
    max_age = timedelta(minutes=FILE_TIMEOUTS.get(file, 10))

    if age > max_age:
        write_log("warning", f"Stale file: {file} is {age} old (limit: {max_age})")
        # Uncomment to enable reboot:
        # os.system("sudo reboot")
        return

    with open(full_path, "r") as f:
        line = f.readline().strip()
        if line.startswith("ERROR"):
            write_log("warning", f"Error in {file}: {line}")
            # Uncomment to enable reboot:
            # os.system("sudo reboot")
        else:
            write_log("info", f"OK: {file}: {line}")

def main():
    for file in FILE_TIMEOUTS:
        check_status_file(file)

if __name__ == "__main__":
    main()

