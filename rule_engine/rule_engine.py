# module8/rule_engine.py

import json
import time
import requests
import paho.mqtt.client as mqtt

# Load rule configurations
with open("rules.json") as f:
    RULES = json.load(f)

# Optional: switch between HTTP API or MQTT command
USE_MQTT = False  # set True to publish to MQTT topic instead of calling REST API
MQTT_BROKER = "mqtt"  # or "localhost" if running separately
MQTT_PORT = 1883

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def evaluate_rule(rule, data):
    try:
        condition = rule["condition"]
        action = rule["action"]
        # Basic threshold evaluation
        if condition["field"] in data:
            value = data[condition["field"]]
            operator = condition["operator"]
            threshold = condition["value"]

            passed = False
            if operator == ">":
                passed = value > threshold
            elif operator == "<":
                passed = value < threshold
            elif operator == "==":
                passed = value == threshold

            if passed:
                # Perform action
                if USE_MQTT:
                    topic = f"iot/devices/{action['device_id']}/cmd"
                    msg = json.dumps({"command": action["command"]})
                    client.publish(topic, msg)
                    print(f"[MQTT] Sent command to {topic}: {msg}")
                else:
                    url = f"http://fastapi_backend:8000/control/{action['device_id']}/{action['command']}"
                    resp = requests.post(url)
                    print(f"[HTTP] Triggered {url}, status: {resp.status_code}")
    except Exception as e:
        print(f"[!] Error evaluating rule: {e}")

# Example: Simulate receiving sensor data
def main():
    while True:
        # In real case, you would consume from Kafka or other stream
        # This example just simulates input
        mock_data = {
            "device_id": "sensor-bdu-001",
            "temperature": 32.0,
            "humidity": 55.5,
            "timestamp": int(time.time())
        }

        for rule in RULES:
            evaluate_rule(rule, mock_data)

        time.sleep(10)

if __name__ == "__main__":
    main()
