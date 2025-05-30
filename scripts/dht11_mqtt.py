#!/usr/bin/env python3

import Adafruit_DHT
from Adafruit_DHT import Raspberry_Pi as platform
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import logging
import os
from datetime import datetime

# ---------------- Config ----------------
# DHT11 instellingen
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # BCM pin voor DHT11 datapin

# Fan instellingen
FAN_GPIO = 12  # GPIO pin 12 is BCM 18
TEMP_THRESHOLD = 35 # graden Celsius
FAN_ON_DURATION = 5  # fan blijft minimaal 60 sec draaien na activering

# MQTT instellingen
MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "DHT11/1"

# Interval in seconden
INTERVAL_SECONDS = 5

# Logging
LOG_FILE = "/mnt/ssd/logs/dht11.log"
STATUS_FILE = "/mnt/ssd/status/dht11.status"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------------- Setup ----------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_GPIO, GPIO.OUT)
GPIO.output(FAN_GPIO, GPIO.LOW)

last_fan_on_time = 0

def write_status(line):
    with open(STATUS_FILE, 'w') as f:
        f.write(line.strip() + "\n")

def read_dht11():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN, platform)
    if humidity is not None and temperature is not None:
        corrected_temp = temperature - 2.0  # offset voor DHT11
        return corrected_temp, humidity
    else:
        return None, None

def send_mqtt(temperature, humidity):
    payload = f'{temperature:.1f},{humidity:.1f}'
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 10)
        client.publish(MQTT_TOPIC, payload)
        client.disconnect()
        logging.info(f"Published: {payload}")
        write_status(f"OK {datetime.utcnow().isoformat()} T={temperature:.1f} H={humidity:.1f}")
    except Exception as e:
        logging.error(f"MQTT send failed: {e}")
        write_status(f"ERROR {datetime.utcnow().isoformat()} mqtt send failed")

def control_fan(temperature):
    global last_fan_on_time
    now = time.time()

    if temperature >= TEMP_THRESHOLD:
        GPIO.output(FAN_GPIO, GPIO.HIGH)
        last_fan_on_time = now
        logging.info(f"Fan ON (T={temperature:.1f}°C)")
    elif now - last_fan_on_time < FAN_ON_DURATION:
        # Fan blijft nog aan, want minder dan FAN_ON_DURATION geleden ingeschakeld
        GPIO.output(FAN_GPIO, GPIO.HIGH)
    else:
        GPIO.output(FAN_GPIO, GPIO.LOW)
        logging.info(f"Fan OFF (T={temperature:.1f}°C)")

# ---------------- Main loop ----------------
try:
    while True:
        temp, hum = read_dht11()
        if temp is not None and hum is not None:
            control_fan(temp)
            send_mqtt(temp, hum)
        else:
            logging.warning("Sensor read failed")
            write_status(f"ERROR {datetime.utcnow().isoformat()} sensor read failed")
        time.sleep(INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("Script gestopt.")
finally:
    GPIO.output(FAN_GPIO, GPIO.LOW)
    GPIO.cleanup()
