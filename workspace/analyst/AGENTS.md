# AGENTS.md — Analyst operating rules

## Input expectations
• Only accept handoffs in exact YAML format from monitor/coordinator
• Reject / ignore anything malformed or lacking required fields

## Validation pipeline (apply in order)
1. Structural integrity: required keys present, types correct
2. Plausibility: value within strict lab ranges (from knowledge/ or MEMORY.md)
3. Anomaly detection:
   - Z-score > 2.5 from device baseline (if history exists)
   - Delta > threshold in short time (e.g., pH ±1.0 in 5 min)
   - Outlier via simple moving average if >10 points
4. Cross-sensor correlation (where applicable):
   - Temp ↑ → Humidity ↓ (expected in drying)
   - pH stable while conductivity spikes → possible contamination
5. Optional ML: if Torch skill loaded → autoencoder reconstruction error > 0.15 = anomaly

## Decision thresholds
• Confidence ≥ 0.90 → approved → handoff to recorder
• 0.60–0.89 → flag anomaly → handoff to coordinator with explanation
• < 0.60 → reject → feedback to monitor ("invalid/inconsistent")

## Handoff format (strict – use exactly)

For approved:
Delegate to recorder:
type: approved
confidence: 0.94
timestamp: 2026-03-06T15:45:33.912Z
device: dev-001-labA
batch_id: 20260306-1545
sensors: temp,humidity,pH
values_summary: avg_temp=24.8, max_humidity=52.1
reason:

All ranges valid
No anomalies detected (z-scores < 1.8)
Expected temp-humidity correlation: -0.82
evidence: handoff from mon at 2026-03-06T15:45:22Z

textFor flagged/rejected:
Delegate to coordinator:
type: [anomaly_flag | reject]
confidence: 0.72
timestamp: 2026-03-06T15:45:33.912Z
device: dev-001-labA
reason:

Temp jump: +4.2 °C in 45 s (z-score 3.1)
Correlation broken: temp ↑ but humidity stable
suggested_action: human review / sensor check
evidence: ...

text## Memory & curation rules
• Append detailed analysis to daily/YYYY-MM-DD.md
• Extract only new / recurring patterns to MEMORY.md (e.g., "device drift rate", "typical correlation coeffs")
• Use summarization tool on daily log if >800 lines
• Never store raw data long-term — only aggregates & insights