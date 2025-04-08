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
    output = line.strip().split()

    if len(output) >= 2:
        key, value = output[0], output[1]

        try:
            value = int(value)  # Convert to integer
            if key in ["V", "VPV", "PPV"]:  # Scale voltage & power values
             return key, value
        except ValueError:
            return None, None  # Ignore non-numeric values

    return None, None

def read_mppt():
    """ Reads data from MPPT and publishes to MQTT if values change """
    try:
        print(f"[INFO] Connecting to serial port {SERIAL_PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"[INFO] Connected to {SERIAL_PORT}")

        client = mqtt.Client()
        client.on_connect = on_connect
        print(f"[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                print(f"[SERIAL] Raw Data: {line}")  # Print raw serial data
                
                key, value = parse_mppt_data(line)
                if key in last_values and value is not None:
                    last_values[key] = value  # Update stored value

                    # Create CSV-like string: "value,value,value,..."
                    payload = ",".join(str(last_values[k]) if last_values[k] is not None else "0" for k in last_values)

                    # Publish only if something changed
                    client.publish(MQTT_TOPIC, payload)
                    print(f"[MQTT] Published: {MQTT_TOPIC} → {payload}")

            time.sleep(1)  # Adjust based on MPPT update rate

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    read_mppt()

