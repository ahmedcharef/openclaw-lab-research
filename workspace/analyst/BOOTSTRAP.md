# BOOTSTRAP.md — Analyst first run & recovery

On startup or reload:

1. Load shared knowledge:
   - knowledge/areas/validation-rules/validation-baselines.md (strict ranges)
   - knowledge/projects/lab-experiments/sensor-metadata.md (device info)

2. Send ready signal to coordinator:
Analyst online
Validation engine loaded
Strict ranges: temperature 15–40 °C, humidity 25–80 %, pH 5.5–8.5, conductivity 0.05–15 mS/cm
Awaiting structured Delegate to analyst: handoffs
Confidence baseline: 0.92
3. Log startup event:
ANALYST START 2026-03-13Txx:xx:xxZ
Torch ML anomaly detection: [enabled / disabled]
