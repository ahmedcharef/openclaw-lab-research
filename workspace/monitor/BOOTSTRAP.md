# BOOTSTRAP.md — Monitor first run & recovery

On startup / recovery:

1. Load MQTT skill
   broker: localhost:1883  (or from config)
   subscribe pattern: /lab/#

2. Load device metadata & soft ranges
   → from knowledge/projects/lab-experiments/sensor-metadata.md

3. Send ready message to coordinator:
Monitor online
Subscribing to /lab/#
Known devices: 1
text

4. Write startup line to daily log:
MONITOR START 2025-03-06Txx:xx:xxZ

Reference shared knowledge:
• sensor-metadata.md
• validation-baselines.md
• fabric-config-reference.md
