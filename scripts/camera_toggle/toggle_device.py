#!/usr/bin/env python3
import RPi.GPIO as GPIO
import sys

GPIO_PIN = 3  # GPIO pin 3 (BCM numbering)

# Set up the GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Toggle the device based on the command-line argument
try:
    if len(sys.argv) != 2 or sys.argv[1] not in ["on", "off"]:
        print("Usage: toggle_device.py [on|off]")
        sys.exit(1)

    state = sys.argv[1]
    if state == "on":
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        print("Device powered ON (GPIO 3 set HIGH)")
    else:
        GPIO.output(GPIO_PIN, GPIO.LOW)
        print("Device powered OFF (GPIO 3 set LOW)")

finally:
    GPIO.cleanup()  # Reset GPIO pins to avoid warnings in future runs
