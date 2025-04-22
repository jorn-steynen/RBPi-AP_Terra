#!/usr/bin/env python3
import RPi.GPIO as GPIO
import sys
import os
import fcntl

GPIO_PIN = 3  # BCM numbering (physical pin 5)
LOCK_FILE = "/tmp/toggle_device.lock"

# Acquire lock to avoid concurrent executions
lock_fd = open(LOCK_FILE, "w")
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print("Another instance is already running. Exiting.")
    sys.exit(1)

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Command-line parsing
try:
    if len(sys.argv) != 2 or sys.argv[1] not in ["on", "off"]:
        print("Usage: toggle_device.py [on|off]")
        sys.exit(1)

    state = sys.argv[1]
    if state == "on":
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        print(f"Device powered ON (GPIO {GPIO_PIN} set HIGH)")
    else:
        GPIO.output(GPIO_PIN, GPIO.LOW)
        print(f"Device powered OFF (GPIO {GPIO_PIN} set LOW)")

finally:
    GPIO.cleanup(GPIO_PIN)
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()
    os.remove(LOCK_FILE)

