# AGENTS.md — Monitor operating rules

## Observation targets
• Primary: MQTT topics matching /lab/#  (configurable via skill)
• Secondary: file drops in ~/incoming/raw/  (if skill enabled)

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