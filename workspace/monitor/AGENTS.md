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

Primary source:

- Tail / read new lines from:
  /home/node/.openclaw/workspace/skills/mqtt-lab-listener/workspace/daily/$(date +%Y-%m-%d)-mqtt.log

Instructions:

1. Every 30–90 seconds, read the last 40–100 lines of the file
2. Look for lines starting with "Published →" followed by topic and JSON
3. Parse the JSON payload inside the line
4. Extract:
   - device_id
   - sensor_type
   - value (convert to float)
   - unit
   - ts
5. Keep track of last value & timestamp per (device_id + sensor_type)
6. Apply checks:
   - missing required fields (device_id, sensor_type, value, unit, ts) → type: incomplete
   - value not numeric or NaN → type: invalid
   - value outside very wide plausible range (temp -150..+200, humidity 0..200, pH -5..20, cond 0..50) → type: soft-range
   - sudden jump from last known value on same (device+type):
     - temperature: > 4 °C in < 120 s
     - humidity:    > 12 % in < 120 s
     - pH:          > 1.0 in < 180 s
     - conductivity > 50% relative change in < 180 s
     → type: jump
   - value unchanged (same as previous) for > 180 seconds → type: freeze
   - no message from known device for > 300 seconds → type: silence
   - message rate > 30 msg/min per device → type: rate
   - new device_id never seen before → type: new-device
   - For dev-001-labA only: if temperature changes > 2 °C but humidity changes < 3 % → type: correlation-break
7. If any of the above → create structured Delegate to analyst YAML
8. Otherwise → append to my daily log only (normal reading)
9. Keep a simple in-memory history (last 20 readings per device+type) to calculate deltas & silence
10. Log every parsed reading with timestamp and "NORMAL" or "FLAGGED: [type]" to my daily/YYYY-MM-DD.md
11. Every 5 minutes → handoff a "health summary" batch even if all normal (type: batch)
