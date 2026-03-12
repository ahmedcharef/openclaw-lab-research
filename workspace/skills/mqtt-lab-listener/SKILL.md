---
name: mqtt-lab-listener
description: Persistent MQTT client for /lab/# topics in OpenClaw-Lab
version: 1.1
enabled: true
background: true               # runs continuously
---

# Persistent MQTT Listener for Lab Sensors

This skill maintains a background MQTT subscription to /lab/#

On message received:

1. Parse JSON payload
2. If valid → create structured handoff to monitor agent
3. Log raw message to workspace/daily/$(date +%Y-%m-%d)-mqtt.log
4. If anomaly-looking (very high/low value) → notify coordinator

Example handoff sent to monitor:
Delegate to monitor:
type: raw-reading
timestamp: 2026-03-12T09:45:22.781Z
device: dev-001-labA
sensor: temperature
value: 24.7
unit: °C
topic: /lab/dev-001-labA/temperature
payload: {...full json...}

Implementation notes for skill runner:

- Use paho-mqtt Python client
- Connect to localhost:1883
- Subscribe to "/lab/#"
- On message → write to internal queue or file that monitor can tail
