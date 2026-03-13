# AGENTS.md — Analyst operating rules

## Input expectations

• Only accept handoffs in exact YAML format from monitor or coordinator
• Reject / ignore anything malformed, missing required fields, or not starting with "Delegate to analyst:"
• Log rejected inputs to daily log with reason

## Validation pipeline (apply in strict order)

1. Structural integrity
   - Required keys present: type, timestamp, device, sensors, values or values_summary
   - All values numeric where expected
   - Timestamps valid ISO 8601 and recent (< 15 min old)

2. Physical plausibility (immediate reject if violated)
   - No negative values for: temperature, humidity, pH, conductivity (unless documented exception)
   - No frozen values: if same value repeated ≥4 times in <10 min → flag freeze
   - Extreme outliers: temp < 0 or > 60 °C, humidity < 0 or > 100 %, pH < 0 or > 14, conductivity < 0

3. Range check (from knowledge/areas/validation-rules/validation-baselines.md)
   - Temperature: 15.0 – 40.0 °C
   - Humidity: 25 – 80 %
   - pH: 5.5 – 8.5
   - Conductivity: 0.05 – 15.0 mS/cm

4. Delta / jump detection
   - Max delta in 60 s: temp ±4.0 °C, humidity ±15 %, pH ±1.0, conductivity ±3.0 mS/cm
   - Z-score > 2.8 from device baseline (if ≥10 prior points in memory)

5. Cross-sensor correlation (when both sensors present in batch)
   - Temperature ↑ + Humidity ↓ → expected (coeff between -0.60 and -0.95)
   - pH stable + conductivity spike → suspicious (possible contamination)
   - Broken correlation → lower confidence

6. Optional ML (if Torch skill available)
   - Autoencoder reconstruction error > 0.18 → anomaly
   - Use device-specific model from MEMORY.md if trained

## Decision thresholds & actions

• Confidence ≥ 0.92 → approved → handoff to recorder
• 0.65 – 0.91 → flag anomaly → handoff to coordinator with explanation + suggested action
• < 0.65 or physically impossible → reject → feedback to monitor ("invalid/inconsistent") + escalate to coordinator
• Any negative value, frozen sensor, or pH < 4 or > 10 → auto-reject + high-priority flag to coordinator

## Handoff formats (strict – copy exactly)

Approved:
Delegate to recorder:
type: approved
confidence: 0.94
timestamp: 2026-03-13T09:15:22.781Z
device: dev-001-labA
batch_id: 20260313-0910
sensors: temperature,humidity
values_summary: avg_temp=23.4, max_humidity=56.1
reason:

All ranges valid
No jumps (max delta 1.2 °C)
Expected temp-humidity correlation: -0.81
evidence: handoff from mon at 2026-03-13T09:14:55Z

Flagged (anomaly):
Delegate to coordinator:
type: anomaly_flag
confidence: 0.71
timestamp: 2026-03-13T09:13:00Z
device: dev-002-labB
reason:

pH frozen at 3.48 for 6 consecutive readings
Conductivity negative values detected (-0.202 mS/cm)
severity: high
suggested_action: immediate human review + possible sensor replacement
evidence: ...

Rejected (invalid):
Delegate to monitor:
type: reject
reason: physically impossible data (negative conductivity)
confidence: 0.22
feedback: invalid/inconsistent – review device calibration

## Memory & curation rules

• Append full analysis (including confidence, reasons, correlations) to daily/YYYY-MM-DD.md
• Extract only new patterns / baselines to MEMORY.md:

- "dev-002-labB pH freeze detected 2026-03-13"
- "dev-001-labA humidity-temp correlation updated: -0.84"
• Run summarization tool if daily log > 700 lines
• Never store full raw payloads long-term — only aggregates, patterns, and anomaly summaries
