#!/usr/bin/env python3
"""
Enhanced IoT sensor data simulator for OpenClaw-Lab
- More frequent, bigger, and longer-lasting anomalies for easier testing
- Publishes to MQTT
- Logs every message to the exact file your MQTT listener skill uses
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

# ────────────────────────────────────────────────
#  INCREASED ANOMALY FREQUENCY & MAGNITUDE
# ────────────────────────────────────────────────
ANOMALY_PROB = {
    "sudden_jump":        0.08,     # ~every 1–2 minutes per sensor
    "gradual_drift":      0.04,     # new drift episode every ~5–15 min
    "freeze":             0.03,     # freeze starts every ~5–10 min
    "outage":             0.015,    # outage every ~10–30 min
    "correlation_break":  0.06,     # correlation break every ~2–5 min
}

# Bigger jumps
JUMP_MAGNITUDE = {
    "temperature":   (6.0, 18.0),   # +6 to +18 °C (very noticeable)
    "humidity":      (15, 40),      # +15 to +40 %
    "pH":            (1.5, 4.0),    # +1.5 to +4 pH units
    "conductivity":  (1.5, 8.0),    # ×2–6 times base
}

# Longer freeze & outage
FREEZE_DURATION_SEC = (300, 1200)     # 5–20 minutes
OUTAGE_DURATION_SEC = (300, 900)      # 5–15 minutes

# Stronger drift
DRIFT_MAX_RATE_PER_SEC = {
    "temperature":   0.008,   # up to ±0.5 °C/min
    "humidity":      0.08,    # up to ±5 %/min
    "pH":            0.015,   # up to ±0.9 pH/min
    "conductivity":  0.12,    # fast changes
}

SIM_START_TIME = time.time()

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
        max_rate = DRIFT_MAX_RATE_PER_SEC.get(sensor, 0.01)
        self.drift_rate[sensor] = random.uniform(-max_rate, max_rate)

    def stop_drift(self, sensor):
        self.drift_active[sensor] = False
        self.drift_rate[sensor] = 0.0

# ==================== HELPERS ====================

def get_iso_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds') + "Z"

def add_noise(base, noise_level):
    return round(base + np.random.normal(0, noise_level), 3)

def apply_anomaly(state, sensor, base, noise):
    now = time.time()

    # Sudden jump – bigger and more frequent
    if random.random() < ANOMALY_PROB["sudden_jump"]:
        direction = random.choice([-1, 1])
        min_mag, max_mag = JUMP_MAGNITUDE.get(sensor, (3.0, 10.0))
        mag = random.uniform(min_mag, max_mag)
        print(f"   🔥 BIG JUMP! {sensor} {direction*mag:+.2f} (new value ~{base + direction*mag:.2f})")
        return base + direction * mag

    # Freeze – longer duration
    if random.random() < ANOMALY_PROB["freeze"] and now > state.freeze_until.get(sensor, 0):
        duration = random.uniform(*FREEZE_DURATION_SEC)
        state.freeze_until[sensor] = now + duration
        print(f"   🧊 FREEZE started on {sensor} for {duration//60:.0f}–{duration//60+1} minutes")

    # Gradual drift – stronger and more frequent
    if random.random() < ANOMALY_PROB["gradual_drift"] and not state.drift_active[sensor]:
        duration = random.uniform(300, 1200)  # 5–20 min
        state.start_drift(sensor)
        print(f"   ↗️ STRONG DRIFT started on {sensor} for {duration//60:.0f}–{duration//60+1} min")

    # Correlation break – more frequent
    if sensor == "temperature" and "humidity" in state.device["sensors"]:
        if random.random() < ANOMALY_PROB["correlation_break"]:
            print(f"   ⚠️ CORRELATION BREAK – temp moving but humidity frozen")

    return base

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
            print(f"Published → {topic:<40}  {value:>6} {unit}")
        else:
            print(f"Publish failed (rc={result.rc})")
    except Exception as e:
        print(f"Publish error: {e}")

    # Log to the exact file your skill uses
    log_path = get_log_filename()
    log_entry = {
        "timestamp": get_iso_timestamp(),
        "topic": topic,
        "message": payload_str,
        "anomaly_flag": "jump" if "JUMP" in str(value) else None  # simple marker
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

# ==================== MAIN LOOP ====================

def main():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    print(f"Simulator started (HIGH ANOMALY MODE) → {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Logging also to: {get_log_filename()}")
    print("Anomalies are now MUCH more frequent and bigger!\n")

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
                    duration = random.uniform(*OUTAGE_DURATION_SEC)
                    state.outage_until = now + duration
                    print(f"   🌑 BIG OUTAGE started for {device_id} ({duration//60:.0f}–{duration//60+1} min silence)")

                for sensor in device["sensors"]:
                    last_t = state.last_publish[sensor]
                    min_i, max_i = device.get("publish_interval", (10, 20))
                    if now - last_t < random.uniform(min_i, max_i):
                        continue

                    # Base value + noise
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

                    # Freeze override
                    if state.is_frozen(sensor) and state.last_values[sensor] is not None:
                        value = state.last_values[sensor]
                        print(f"   (frozen value held: {value} {unit})")

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