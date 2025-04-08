#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import sys

GPIO_PIN = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

def toggle_device(state):
    if state.lower() == "on":
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        print(f"Device powered ON (GPIO {GPIO_PIN} set HIGH)")
    elif state.lower() == "off":
        GPIO.output(GPIO_PIN, GPIO.LOW)
        print(f"Device powered OFF (GPIO {GPIO_PIN} set LOW)")
    else:
        print("Usage: ./toggle_device.py [on|off]")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./toggle_device.py [on|off]")
        sys.exit(1)
    try:
        toggle_device(sys.argv[1])
    except KeyboardInterrupt:
        print("\nScript interrupted")
