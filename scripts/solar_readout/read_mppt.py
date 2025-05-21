#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import serial
import glob
import time
import logging
import os
from datetime import datetime

MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "mppt/data2"
BAUD_RATE = 19200

LOG_FILE = "/mnt/ssd/logs/mppt.log"
STATUS_FILE = "/mnt/ssd/status/mppt.status"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

last_values = {
    "V": None, "I": None, "VPV": None, "PPV": None,
    "IL": None, "H19": None, "H20": None, "H21": None, "H22": None, "HSDS": None
}

def write_status(status_line):
    with open(STATUS_FILE, 'w') as f:
        f.write(status_line.strip() + "\n")

def on_connect(client, userdata, flags, rc):
    logging.info(f"[MQTT] Connected with result code {rc}")

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
            logging.info(f"[INFO] Connected to {port}")
            return ser
        except Exception as e:
            logging.error(f"Serial connection failed: {e}. Retrying in 5s...")
            write_status(f"ERROR {datetime.utcnow().isoformat()} serial connect fail")
            time.sleep(5)

def connect_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            logging.info(f"[MQTT] Connected to {MQTT_BROKER}")
            return client
        except Exception as e:
            logging.error(f"MQTT connection failed: {e}. Retrying in 5s...")
            write_status(f"ERROR {datetime.utcnow().isoformat()} mqtt connect fail")
            time.sleep(5)

def read_mppt():
    ser = connect_serial()
    client = connect_mqtt()
    update_interval = 10  # Publish every x seconds
    last_publish = time.time()

    try:
        while True:
            while ser.in_waiting:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    key, value = parse_mppt_data(line)
                    if key and value is not None:
                        last_values[key] = value

            current_time = time.time()
            if current_time - last_publish >= update_interval:
                payload = ",".join(str(last_values[k]) if last_values[k] is not None else "0" for k in last_values)
                client.publish(MQTT_TOPIC, payload, qos=1)
                logging.info(f"Published: {payload}")
                print(f"[MQTT] Published: {MQTT_TOPIC} → {payload}")
                status_summary = f"OK {datetime.utcnow().isoformat()} V={last_values['V']} I={last_values['I']} PPV={last_values['PPV']}"
                write_status(status_summary)
                last_publish = current_time

            time.sleep(1.0)

    except KeyboardInterrupt:
        logging.info("[INFO] Shutting down...")
    except Exception as e:
        logging.error(f"[ERROR] Unexpected error: {e}")
        write_status(f"ERROR {datetime.utcnow().isoformat()} runtime exception")
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()
        logging.info("[INFO] Connections closed")

if __name__ == "__main__":
    read_mppt()

