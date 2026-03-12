#!/usr/bin/env python3
"""
Simple IoT sensor data simulator for OpenClaw-Lab
- Publishes to MQTT
- Also logs every message to the exact file your MQTT listener skill uses

Dependencies:
    pip install paho-mqtt numpy
"""

import json
import time
import random
import os
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import numpy as np

# ==================== CONFIG ====================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_CLIENT_ID = f"simulator-{random.randint(1000,9999)}"

BASE_TOPIC = "/lab"

# Log file path — matches your skill's location
HOME = os.path.expanduser("~")  # gets /home/node or current user's home
LOG_DIR = os.path.join(HOME, ".openclaw/workspace/skills/mqtt-lab-listener/workspace/daily")


os.makedirs(LOG_DIR, exist_ok=True)

def get_log_filename():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}-mqtt.log")


DEVICES = [
    {
        "id": "dev-001-labA",
        "location": "Lab A - Shelf 3",
        "sensors": ["temperature", "humidity"],
        "temp_base": 23.5,
        "temp_noise": 0.4,
        "humidity_base": 52.0,
        "humidity_noise": 3.5,
        "publish_interval": (8, 18),
    },
    {
        "id": "dev-002-labB",
        "location": "Lab B - Chemical bench",
        "sensors": ["pH", "conductivity"],
        "ph_base": 7.1,
        "ph_noise": 0.08,
        "conductivity_base": 2.4,
        "conductivity_noise": 0.3,
        "publish_interval": (12, 35),
    },
    {
        "id": "dev-003-labC",
        "location": "Incubator",
        "sensors": ["temperature"],
        "temp_base": 37.0,
        "temp_noise": 0.15,
        "publish_interval": (15, 25),
    }
]

# Anomaly probabilities (very low = rare)
ANOMALY_PROB = {
    "sudden_jump":    0.008,    # ~once every ~2 hours per sensor
    "gradual_drift":  0.004,    # rare episode starts
    "freeze":         0.003,    # value stuck for a while
    "outage":         0.002,    # full device silence 2–12 min
    "correlation_break": 0.005, # temp up but humidity doesn't follow
}

SIM_START_TIME = time.time()
ENABLE_JUMPS = True
ENABLE_OUTAGES = True
ENABLE_DRIFT = True

# ==================== STATE ====================

class DeviceState:
    def __init__(self, device):
        self.device = device
        self.last_values = {s: None for s in device["sensors"]}
        self.last_publish = {s: 0 for s in device["sensors"]}
        self.drift_active = {s: False for s in device["sensors"]}
        self.drift_rate = {s: 0.0 for s in device["sensors"]}
        self.freeze_until = {s: 0 for s in device["sensors"]}
        self.outage_until = 0

    def is_outage(self):
        return time.time() < self.outage_until

    def is_frozen(self, sensor):
        return time.time() < self.freeze_until.get(sensor, 0)

    def start_drift(self, sensor):
        self.drift_active[sensor] = True
        self.drift_rate[sensor] = random.uniform(-0.15, 0.15) / 60  # per second, slow

    def stop_drift(self, sensor):
        self.drift_active[sensor] = False
        self.drift_rate[sensor] = 0.0

# ==================== HELPERS ====================

def get_iso_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds') + "Z"

def add_realistic_noise(base, noise_level, drift=0.0):
    noise = np.random.normal(0, noise_level)
    return round(base + noise + drift, 2)
def add_noise(base, noise_level):
    return round(base + np.random.normal(0, noise_level), 3)

def apply_anomaly(state, sensor, base, noise):
    now = time.time()

    # Sudden jump
    if random.random() < ANOMALY_PROB["sudden_jump"]:
        direction = random.choice([-1, 1])
        mag = random.uniform(3.0, 10.0) if "temp" in sensor else random.uniform(0.8, 2.5)
        print(f"   ⚡ SUDDEN JUMP! {sensor} {direction*mag:+.2f}")
        return base + direction * mag

    # Freeze (stuck value)
    if random.random() < ANOMALY_PROB["freeze"] and now > state.freeze_until.get(sensor, 0):
        duration = random.uniform(180, 480)  # 3–8 min
        state.freeze_until[sensor] = now + duration
        print(f"   ❄️ FREEZE started on {sensor} for ~{duration/60:.0f} min")

    # Gradual drift episode
    if random.random() < ANOMALY_PROB["gradual_drift"] and not state.drift_active[sensor]:
        duration = random.uniform(600, 1800)  # 10–30 min
        state.start_drift(sensor)
        print(f"   ↗️ DRIFT episode started on {sensor} for ~{duration/60:.0f} min")

    # Correlation break (only for temp/humidity pair on same device)
    if sensor == "temperature" and "humidity" in state.device["sensors"]:
        if random.random() < ANOMALY_PROB["correlation_break"]:
            print(f"   ⚠️ CORRELATION BREAK triggered (temp changes, humidity stays)")

    return base

def get_drift_factor(elapsed_hours):
    if not ENABLE_DRIFT:
        return 0.0
    drift_rate = random.uniform(-0.10, 0.10) / 3600
    return drift_rate * elapsed_hours * 3600

def simulate_outage():
    if ENABLE_OUTAGES and random.random() < 0.004:
        duration_sec = random.randint(120, 600)
        print(f"   !!! Outage simulation: sleeping {duration_sec}s ...")
        time.sleep(duration_sec)

def log_to_file(topic, payload_dict):
    log_entry = {
        "timestamp": get_iso_timestamp(),
        "topic": topic,
        "message": json.dumps(payload_dict),           # raw JSON string
        "struct_redacted": False,
        "anomaly_scored": False
    }
    log_path = get_log_filename()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

# ==================== PUBLISH + LOG ====================

def publish_message(client, device, sensor_type, value, unit):
    topic = f"{BASE_TOPIC}/{device['id']}/{sensor_type}"
    payload = {
        "device_id": device["id"],
        "sensor_type": sensor_type,
        "value": value,
        "unit": unit,
        "ts": get_iso_timestamp(),
        "location": device["location"],
        "sim_note": "generated by sensor-data-generator.py"
    }
    payload_str = json.dumps(payload)

    # Publish to MQTT
    try:
        result = client.publish(topic, payload_str, qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published → {topic:<35}  {value:>6} {unit}")
        else:
            print(f"Publish failed (rc={result.rc})")
    except Exception as e:
        print(f"Publish error: {e}")

    # Log to the file your skill expects
    log_to_file(topic, payload)

# ==================== MAIN LOOP ====================

def main():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    print(f"Simulator started → broker={MQTT_BROKER}:{MQTT_PORT}")
    print(f"Logging also to: {get_log_filename()}")
    print("Publishing to /lab/# ...  Ctrl+C to stop\n")

    last_publish = {d["id"]: {} for d in DEVICES}
    states = {d["id"]: DeviceState(d) for d in DEVICES}

    try:
        while True:
            now = time.time()

            for device_id, state in states.items():
                device = state.device

                if state.is_outage():
                    time.sleep(1)
                    continue

                # Check if outage should start
                if random.random() < ANOMALY_PROB["outage"]:
                    duration = random.uniform(120, 720)  # 2–12 min
                    state.outage_until = now + duration
                    print(f"   🌑 OUTAGE started for {device_id} (~{duration/60:.0f} min silence)")

                for sensor in device["sensors"]:
                    last_t = state.last_publish[sensor]
                    min_i, max_i = device.get("publish_interval", (10, 20))
                    if now - last_t < random.uniform(min_i, max_i):
                        continue

                    # Get base + apply anomaly logic
                    if sensor == "temperature":
                        base = device["temp_base"]
                        noise = device["temp_noise"]
                        unit = "°C"
                    elif sensor == "humidity":
                        base = device["humidity_base"]
                        noise = device["humidity_noise"]
                        unit = "%"
                    elif sensor == "pH":
                        base = device["ph_base"]
                        noise = device["ph_noise"]
                        unit = "pH"
                    elif sensor == "conductivity":
                        base = device["conductivity_base"]
                        noise = device["conductivity_noise"]
                        unit = "mS/cm"
                    else:
                        continue

                    value = add_noise(base, noise)
                    value = apply_anomaly(state, sensor, value, noise)

                    # Freeze: keep last value if active
                    if state.is_frozen(sensor) and state.last_values[sensor] is not None:
                        value = state.last_values[sensor]

                    publish_message(client, device, sensor, value, unit)

                    state.last_values[sensor] = value
                    state.last_publish[sensor] = now

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()
        print("MQTT client disconnected.")

if __name__ == "__main__":
    main()