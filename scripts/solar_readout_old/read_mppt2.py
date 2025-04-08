#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import serial
import time

# MQTT Configuration
MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "mppt/data"

# Serial Configuration
SERIAL_PORT = "/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.1:1.0-port0"
BAUD_RATE = 19200  # Matches your Node-RED settings

# Store previous values to detect changes
last_values = {
    "V": None, "I": None, "VPV": None, "PPV": None,
    "IL": None, "H19": None, "H20": None, "H21": None, "H22": None, "HSDS": None
}

def on_connect(client, userdata, flags, rc):
    """ Callback function for MQTT connection """
    if rc == 0:
        print(f"[MQTT] Connected successfully to {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"[MQTT] Connection failed with code {rc}")

def parse_mppt_data(line):
    """ Parse MPPT serial data and extract values """
    print(f"[DEBUG] Raw Serial Data: {line}")  # Debug print

    data = line.strip().split()
    parsed_data = {}

    for item in data:
        try:
            key, value = item.split("=")
            parsed_data[key] = float(value) if '.' in value else int(value)
        except ValueError:
            pass  # Ignore any malformed data

    # Debugging: Check if missing values exist
    for key in last_values.keys():
        if key not in parsed_data:
            parsed_data[key] = 0  # Ensure all values are always present

    print(f"[DEBUG] Parsed Data: {parsed_data}")  # Debug print
    return parsed_data

def publish_changes(client, data):
    """ Publish only changed values to MQTT """
    global last_values
    changed_data = {k: v for k, v in data.items() if last_values.get(k) != v}

    if changed_data:
        payload = str(changed_data)
        result = client.publish(MQTT_TOPIC, payload)

        if result.rc == 0:
            print(f"[MQTT] Published: {payload}")
            last_values.update(changed_data)
        else:
            print("[MQTT ERROR] Failed to publish message.")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
            print(f"[INFO] Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")

            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    parsed_data = parse_mppt_data(line)
                    publish_changes(client, parsed_data)

    except serial.SerialException as e:
        print(f"[ERROR] Serial error: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] Stopping script.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

