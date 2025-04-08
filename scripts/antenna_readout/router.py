import subprocess
import time
import paho.mqtt.client as mqtt

# MQTT-instellingen
MQTT_BROKER = "mqtt.iot-ap.be"
MQTT_PORT = 1883
MQTT_TOPIC = "router/1"

# SNMP-instellingen
ROUTER_IP = "192.168.100.1"
COMMUNITY = "public1"
VERSION = "2c"

# De juiste OIDs
OIDS = {
    "rssi": "iso.3.6.1.4.1.14988.1.1.16.1.1.2.4",  # -68
    "rsrq": "iso.3.6.1.4.1.14988.1.1.16.1.1.3.4",  # -12
    "rsrp": "iso.3.6.1.4.1.14988.1.1.16.1.1.4.4",  # -81
    "sinr": "iso.3.6.1.4.1.14988.1.1.16.1.1.7.4"   # 7
}

def get_snmp_value(oid):
    try:
        # -Oqv laat alleen de waarde zelf zien
        output = subprocess.check_output([
            "snmpget", f"-v{VERSION}", "-c", COMMUNITY, "-Oqv", ROUTER_IP, oid
        ], universal_newlines=True)
        return output.strip()
    except Exception as e:
        print(f"Fout bij het ophalen van {oid}: {e}")
        return None

def publish_lte_values():
    # Haal alle LTE-waarden op in één dictionary
    values = {key: get_snmp_value(oid) for key, oid in OIDS.items()}

    # Controleer of er een waarde ontbreekt (None)
    if None in values.values():
        print("❌ Een of meer SNMP-waarden konden niet opgehaald worden.")
        return

    # Bouw het payload-bericht
    payload = f"{values['rssi']},{values['rsrq']},{values['rsrp']},{values['sinr']}"

    # Verzend naar MQTT
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, payload)
    client.disconnect()

    print("✅ Gegevens verzonden:", payload)

if __name__ == "__main__":
    try:
        while True:
            publish_lte_values()
            time.sleep(2)  # Wacht 2 seconden voor de volgende meting
    except KeyboardInterrupt:
        print("Script gestopt door gebruiker.")
