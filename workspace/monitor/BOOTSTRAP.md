# BOOTSTRAP.md — Monitor first run & recovery

On startup / recovery (current date: March 13, 2026):

1. Confirm primary data source
   • Active log file to tail:
     /home/ahmed/.openclaw/workspace/skills/mqtt-lab-listener/workspace/daily/$(date +%Y-%m-%d)-mqtt.log
   • If file does not exist yet → log warning and wait/retry every 60 s

2. Load shared knowledge & baselines
   → sensor-metadata.md
   → validation-baselines.md
   → fabric-config-reference.md (for future recorder handoff context)

3. Initialize internal state
   - Clear last_values cache (device_id + sensor_type → {value, ts})
   - Set anomaly detection thresholds (jump >4°C temp, >12% hum, >1.0 pH, etc.)
   - Prepare to poll log every 30–90 seconds

4. Send ready message to coordinator (structured):
MONITOR AGENT ONLINE
Date: 2026-03-13
Watching log: /home/ahmed/.openclaw/.../daily/2026-03-13-mqtt.log
Mode: anomaly-aware (big jumps, freezes, outages, drifts)
Known devices from metadata: 3
Polling frequency: ~45 seconds
Ready to parse & check incoming readings
text

5. Write startup line to my own daily log
MONITOR START 2026-03-13Txx:xx:xxZ
Log source: mqtt-lab-listener daily file
Anomaly detection: enabled (jump, freeze, outage, correlation-break)

6. First action after startup

- Immediately read last 100 lines of the log
- Parse any recent readings
- Log them internally
- If anomalies found in last 10 min → create handoff to analyst immediately

Reference shared knowledge:
• projects/lab-experiments/sensor-metadata.md
• areas/validation-rules/validation-baselines.md
• resources/chain/fabric-config-reference.md
