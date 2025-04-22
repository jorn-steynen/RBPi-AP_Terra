#!/usr/bin/env python3

import Adafruit_DHT
from Adafruit_DHT import Raspberry_Pi as platform
import paho.mqtt.client as mqtt
import time
import logging
import os
from datetime import datetime

# DHT11 config
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # GPIO4

# MQTT settings
MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "DHT11/1"

# Read interval (in seconds)
INTERVAL_SECONDS = 5

# Log and status paths
LOG_FILE = "/mnt/ssd/logs/dht11.log"
STATUS_FILE = "/mnt/ssd/status/dht11.status"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def write_status(line):
    with open(STATUS_FILE, 'w') as f:
        f.write(line.strip() + "\n")

def read_dht11():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN, platform)
    if humidity is not None and temperature is not None:
        return temperature, humidity
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

if __name__ == "__main__":
    while True:
        temp, hum = read_dht11()
        if temp is not None and hum is not None:
            send_mqtt(temp, hum)
        else:
            logging.warning("Sensor read failed")
            write_status(f"ERROR {datetime.utcnow().isoformat()} sensor read failed")
        time.sleep(INTERVAL_SECONDS)

