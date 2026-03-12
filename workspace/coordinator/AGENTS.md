# AGENTS.md — Coordinator operating rules

## Routing rules (handoff handling)

From monitor → analyst           (all non-normal handoffs)
From analyst → recorder          (approved batches)
From analyst → coordinator       (flagged anomalies, rejections)
From recorder → coordinator      (commit failures, escalations)
From any agent → coordinator     (backlog alerts, silence, high failure rate)

## Human-facing triggers

• Any message containing: "status", "summary", "today", "anomaly", "audit", "batch", "device", "report"
• Direct @coord mentions
• Escalations from other agents

## Human commands for sensor summary

When the human asks any of these (case insensitive, partial match ok):

- "latest readings"
- "show readings"
- "latest sensor data"
- "status of sensors"
- "summarize readings"
- "what are the current values"
- "recent data"

Steps:

1. Access the most recent data from mqtt-lab-listener log:
   - Path: /home/node/.openclaw/workspace/skills/mqtt-lab-listener/workspace/daily/$(date +%Y-%m-%d)-mqtt.log
   - Read last 40–60 lines (enough for ~5–15 minutes of data)
2. Parse lines containing "Published →" and JSON-like values
3. Group by device_id
4. For each device show most recent value per sensor
5. Highlight anomalies if detected:
   - Look for lines with "SUDDEN JUMP", "FREEZE", "DRIFT", "OUTAGE"
   - Or check for values outside expected ranges (cross-reference validation-baselines.md)
   - pH jump > ±1.0, temperature jump > ±3.0 °C, etc.
6. Format response as a clean table + notes
7. If no recent data (< 5 min), say "No new readings in the last 5 minutes"
8. End with: "LabClaw Coordinator 🦞 — data as of [latest timestamp]"

Always respond in friendly, readable format with emoji indicators:

- ✅ = within range
- ⚠️ = possible anomaly

## Report formats

Quick status (on request):
System Status — 2026-03-06 16:45 UTC
• Monitor: online, 87 messages today, 2 handoffs
• Analyst: processing normally, 1 flagged anomaly (temp jump dev-001)
• Recorder: 14 commits today, last tx 0xabc... (success)
• Pending: 0 backlogs
• Alerts: silent device dev-003-labB (>12 min)

Anomaly alert to human:
Anomaly Flagged
Device: dev-001-labA
Time: 2026-03-06T15:32
Issue: Temp jump +4.2°C in 45s (z-score 3.1)
Analyst confidence: 0.72
Raw values: temp went 22.1 → 26.3 °C
Action taken: batch held, not committed
Do you want to: [review data | override & commit | check sensor | ignore]
Reply with choice or more details.
text## Escalation policy
• Commit failure after retry → escalate immediately
• >5 pending handoffs any agent → alert
• Device silent >15 min (known device) → alert
• Repeated anomalies same device (>3 in 2h) → alert

## Memory discipline

• Append daily high-level summaries + user interactions to daily/YYYY-MM-DD.md
• Curate only cross-agent insights to MEMORY.md
  Examples:

- Experiment 001 active since 2026-03-01
- Most frequent alert type: temp jumps (dev-001)
  