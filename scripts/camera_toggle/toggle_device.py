#!/usr/bin/env python3
import subprocess
import sys
import fcntl
import os

GPIO_PIN = 3  # GPIO 3 (BCM numbering, physical pin 5)
LOCK_FILE = "/tmp/toggle_device.lock"

# Acquire a lock to prevent multiple instances from running
lock_fd = open(LOCK_FILE, "w")
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print("Another instance of toggle_device.py is already running. Exiting.")
    sys.exit(1)

# Toggle the device based on the command-line argument
try:
    if len(sys.argv) != 2 or sys.argv[1] not in ["on", "off"]:
        print("Usage: toggle_device.py [on|off]")
        sys.exit(1)

    state = sys.argv[1]
    if state == "on":
        subprocess.run(["raspi-gpio", "set", str(GPIO_PIN), "op", "dh"], check=True)
        print("Device powered ON (GPIO 18 set HIGH)")
    else:
        subprocess.run(["raspi-gpio", "set", str(GPIO_PIN), "op", "dl"], check=True)
        print("Device powered OFF (GPIO 18 set LOW)")

finally:
    fcntl.flock(lock_fd, fcntl.LOCK_UN)  # Release the lock
    lock_fd.close()
    os.remove(LOCK_FILE)  # Remove the lock file
