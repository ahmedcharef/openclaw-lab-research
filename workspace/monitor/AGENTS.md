# AGENTS.md — Monitor operating rules

## MQTT observation

Use the "mqtt-lab-iot" skill to subscribe and receive messages.
Forward parsed readings directly into observation loop.

## Mandatory lightweight checks (applied to every message)

1. Has minimal structure? (at minimum: device_id, sensor_type, value, unit)
2. Value is numeric when expected for that sensor_type
3. Within very wide physics-plausible range?
   temp:     -100 … +200 °C
   humidity:   0 … 150 %
   pH:         0 …  20
   pressure: 300 … 1100 hPa
   etc.
4. Sudden jump from previous same-sensor reading (>50% in <30 s) → flag
5. Message rate from same device (>20 msg / 60 s) → rate-limit warning

## When to hand off (only these cases trigger delegation)

A. Value outside soft range (from knowledge/ or MEMORY.md)  
B. Jump >40% in <60 s on same device  
C. Incomplete fields that were previously present  
D. Rate limit / flood detected (>20 msg/min same device)  
E. Every 15 minutes → handoff 15-min batch summary (even if normal)  
F. New device appeared (first message from unknown device_id)

## Handoff message format (MUST follow exactly)

Delegate to analyst:
type: [soft-range | jump | incomplete | rate | batch | new-device]
timestamp: 2025-03-06T14:35:22.781Z
device: dev-001-labA
sensors: temp,humidity
values: {temp: 26.8, humidity: 48.2}
delta_prev: +1.4 °C / +2.1 %
reason: value above soft upper limit (25 °C)
source_topic: /labA/env/temp
payload_excerpt: {"device_id":"dev-001-labA","ts":"2025-03-06T14:35:22Z","temp":26.8,"humidity":48.2}
batch_id: 20250306-1430  (only for batch type)

## Logging & memory discipline

• Append ALL plausible readings to daily/YYYY-MM-DD.md (structured)
• Append only significant events / new devices / patterns to MEMORY.md
• Examples of allowed MEMORY.md entries:

- 2025-03-06 new device: dev-B02-labC
- Typical rate dev-001-labA: 1 msg / 12–18 s
- Observed soft range violation threshold hit 3× last week on pH

## Observation sources

Primary source (preferred):

- Use mqtt-lab-listener skill logs
- Tail or read: /home/node/.openclaw/workspace/skills/mqtt-lab-listener/workspace/daily/$(date +%Y-%m-%d)-mqtt.log

Fallback (if skill not responding):

- Directly use mqtt_subscribe on /lab/# if tool available

How to process:

1. Read new lines every 30–60 seconds (use tail -n 20 or similar)
2. Parse each line that contains JSON payload
3. Extract fields: device_id, sensor_type, value, unit, ts
4. Apply lightweight checks:
   - required fields present?
   - value numeric?
   - within very wide plausible range?
   - sudden jump from previous same-sensor reading?
   - rate too high (>20 msg/min per device)?
5. If normal → log quietly to my daily/YYYY-MM-DD.md
6. If interesting/suspicious → create Delegate to analyst YAML
7. If new device → handoff "new-device" type
