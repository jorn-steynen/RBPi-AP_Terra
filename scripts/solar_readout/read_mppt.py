#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import serial
import glob
import time
import logging

MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "mppt/data2"
BAUD_RATE = 19200

last_values = {
    "V": None, "I": None, "VPV": None, "PPV": None,
    "IL": None, "H19": None, "H20": None, "H21": None, "H22": None, "HSDS": None
}

logging.basicConfig(filename="/dev/shm/logs/mppt.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    pass

def find_serial_port():
    ports = glob.glob("/dev/ttyUSB*")
    for port in ports:
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=2)
            for _ in range(5):
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if any(key in line for key in last_values):
                    ser.close()
                    return port
            ser.close()
        except serial.SerialException:
            continue
    raise Exception("No suitable serial port found")

def parse_mppt_data(line):
    try:
        key, value = line.strip().split(maxsplit=1)
        if key in last_values:
            value = int(value)
            if key in ["V", "VPV"]:
                return key, value / 1000.0
            elif key in ["I", "IL"]:
                return key, value / 1000.0
            elif key == "PPV":
                return key, value
            elif key in ["H19", "H20", "H21", "H22"]:
                return key, value / 10.0 if key != "H21" else value
            elif key == "HSDS":
                return key, value
        return None, None
    except (ValueError, IndexError):
        return None, None

def connect_serial():
    while True:
        try:
            port = find_serial_port()
            ser = serial.Serial(port, BAUD_RATE, timeout=2)
            print(f"[INFO] Connected to {port}")
            return ser
        except Exception as e:
            print(f"[ERROR] Serial connection failed: {e}. Retrying in 5s...")
            time.sleep(5)

def connect_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            print(f"[MQTT] Connected to {MQTT_BROKER}")
            return client
        except Exception as e:
            print(f"[ERROR] MQTT connection failed: {e}. Retrying in 5s...")
            time.sleep(5)

def read_mppt():
    ser = connect_serial()
    client = connect_mqtt()
    update_interval = 15  # Publish every 15 seconds
    last_publish = time.time()

    try:
        while True:
            while ser.in_waiting:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    # print(f"[SERIAL] Raw Data: {line}")
                    key, value = parse_mppt_data(line)
                    if key and value is not None:
                        last_values[key] = value

            current_time = time.time()
            if current_time - last_publish >= update_interval:
                payload = ",".join(str(last_values[k]) if last_values[k] is not None else "0" for k in last_values)
                logging.info(f"Published: {payload}")
                client.publish(MQTT_TOPIC, payload, qos=1)
                print(f"[MQTT] Published: {MQTT_TOPIC} → {payload}")
                last_publish = current_time

            time.sleep(1.0)  # Check every 1 second

    except KeyboardInterrupt:
        print("[INFO] Shutting down...")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()
        print("[INFO] Connections closed")

if __name__ == "__main__":
    read_mppt()
