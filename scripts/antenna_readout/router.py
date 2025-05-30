import subprocess
import time
import paho.mqtt.client as mqtt
import logging
import os
from datetime import datetime

# MQTT settings
MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "router/1"

# SNMP settings
ROUTER_IP = "192.168.88.1"
COMMUNITY = "public1"
VERSION = "2c"

# OIDs
OIDS = {
    "rssi": "iso.3.6.1.4.1.14988.1.1.16.1.1.2.4",
    "rsrq": "iso.3.6.1.4.1.14988.1.1.16.1.1.3.4",
    "rsrp": "iso.3.6.1.4.1.14988.1.1.16.1.1.4.4",
    "sinr": "iso.3.6.1.4.1.14988.1.1.16.1.1.7.4"
}

# Logging setup
LOG_FILE = "/mnt/ssd/logs/router.log"
STATUS_FILE = "/mnt/ssd/status/router.status"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def write_status(message):
    with open(STATUS_FILE, 'w') as f:
        f.write(message.strip() + "\n")

def get_snmp_value(oid):
    try:
        output = subprocess.check_output([
            "snmpget", f"-v{VERSION}", "-c", COMMUNITY, "-Oqv", ROUTER_IP, oid
        ], universal_newlines=True)
        return output.strip()
    except Exception as e:
        logging.error(f"Failed to get {oid}: {e}")
        write_status(f"ERROR {datetime.utcnow().isoformat()} SNMP failure: {oid}")
        return None

def publish_lte_values():
    values = {key: get_snmp_value(oid) for key, oid in OIDS.items()}
    if None in values.values():
        logging.warning("One or more SNMP values could not be retrieved.")
        write_status(f"ERROR {datetime.utcnow().isoformat()} SNMP read error")
        return

    payload = f"{values['rssi']},{values['rsrq']},{values['rsrp']},{values['sinr']}"
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, payload)
        client.disconnect()
        logging.info(f"Published: {payload}")
        write_status(f"OK {datetime.utcnow().isoformat()} RSSI={values['rssi']}")
    except Exception as e:
        logging.error(f"MQTT publish failed: {e}")
        write_status(f"ERROR {datetime.utcnow().isoformat()} MQTT failure")

if __name__ == "__main__":
    try:
        while True:
            publish_lte_values()
            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Script stopped by user.")

