#!/usr/bin/env python3

import Adafruit_DHT
from Adafruit_DHT import Raspberry_Pi as platform
import paho.mqtt.client as mqtt
import time

# DHT11 config
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # GPIO4

# MQTT settings
MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "DHT11/1"

# Read interval (in seconds)
INTERVAL_SECONDS = 5

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
        # print("✅ Data sent to MQTT broker.")
    except Exception as e:
        # print(f"⚠️ MQTT send failed: {e}")
        pass

if __name__ == "__main__":
    # print(f"📡 Starting DHT11 MQTT reporting every {INTERVAL_SECONDS} seconds...")
    while True:
        temp, hum = read_dht11()
        if temp is not None and hum is not None:
            # print(f"\n🌡️  Temperature: {temp:.1f}°C")
            # print(f"💧 Humidity: {hum:.1f}%")
            send_mqtt(temp, hum)
        else:
            # print("\n❌ Failed to retrieve data from DHT11 sensor.")
            pass
        time.sleep(INTERVAL_SECONDS)

