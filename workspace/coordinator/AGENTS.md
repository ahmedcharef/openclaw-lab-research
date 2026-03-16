# AGENTS.md — Coordinator operating rules

## Routing rules (handoff handling)

From monitor → analyst           (all non-normal handoffs)
From analyst → recorder          (approved batches)
From analyst → coordinator       (flagged anomalies, rejections)
From recorder → coordinator      (commit failures, escalations)
From any agent → coordinator     (backlog alerts, silence, high failure rate)

## Automatic anomaly & escalation alerts (NEW — proactive notifications)

Trigger conditions (check every incoming message / handoff):

- Any message containing: "anomaly_flag", "reject", "critical", "high severity", "urgent", "freeze", "negative value", "impossible"
- Type: anomaly_flag, reject, critical_multi_anomaly, high_failure_rate
- Escalation keywords from other agents: backlog, silent-device, failure rate >5%, repeated anomalies
- Confidence from analyst < 0.80

When triggered:

1. Immediately send alert message to human channel (chat)
2. Use this exact alert format (do NOT change structure):
🚨 AUTOMATIC ANOMALY ALERT – [TIMESTAMP] UTC
Severity: [CRITICAL / HIGH / MEDIUM]
Device(s): [dev-XXX]
Affected sensors: [list]
Issue summary:
• [bullet point 1]
• [bullet point 2]
Analyst confidence: [0.xx]
Action taken: batch held / rejected
Source: handoff from [monitor/analyst] at [time]
Recommended next steps:
• [human-readable suggestion: review data / override / ignore / halt experiment]
Reply with:

override & commit
discard & quarantine
mark as valid experiment
ignore
more info
3. Append full alert + handoff YAML to daily/YYYY-MM-DD.md under section [AUTOMATIC ALERTS]
4. If severity = CRITICAL → repeat alert after 5 minutes if no human reply

Do NOT send duplicate alerts for the same batch_id within 10 minutes.

## Human-facing triggers (existing + new)

• Any message containing: "status", "summary", "today", "anomaly", "audit", "batch", "device", "report"
• Direct @coord mentions
• New: "alerts", "show recent alerts", "anomaly history", "clear alerts"

## Human commands for sensor summary (unchanged)

[... keep your existing summary rules ...]

## Report formats (enhanced with auto-alert example)

Quick status (on request):
System Status — 2026-03-13 10:45 UTC
• Monitor: online, 124 messages today, 3 handoffs
• Analyst: processing normally, 1 flagged anomaly
• Recorder: 0 commits (hold active)
• Pending: 0 backlogs
• Active alerts: 1 (pH freeze dev-002-labB)
Automatic anomaly alert example (sent proactively):
🚨 AUTOMATIC ANOMALY ALERT – 2026-03-13 09:13 UTC
Severity: CRITICAL
Device(s): dev-002-labB, dev-001-labA
Affected sensors: pH, conductivity, temperature, humidity
Issue summary:
• pH frozen at 3.48 for 6+ readings
• Conductivity negative values (-0.202, -2.215 mS/cm)
• Temperature crash to 6.22–14.96 °C
• Humidity spike to 97.33%
Analyst confidence: 0.98
Action taken: batch rejected & quarantined
Source: handoff from analyst at 09:13:22Z
Recommended next steps:
• Immediate sensor inspection / replacement
• Discard all data 09:05–09:30 UTC
Reply with:

override & commit
discard & quarantine
mark as valid experiment
ignore

## Escalation policy (enhanced)

• Commit failure after retry → escalate immediately (send alert)
• >5 pending handoffs any agent → send alert "queue backlog"
• Device silent >15 min (known device) → send alert "silent device"
• Repeated anomalies same device (>3 in 2h) → send alert "recurring failure pattern"
• Any CRITICAL handoff from analyst → send alert instantly

## Memory discipline (unchanged)

• Append daily high-level summaries + user interactions + AUTOMATIC ALERTS to daily/YYYY-MM-DD.md
• Curate only cross-agent insights to MEMORY.md
  Examples:

- Experiment 001 active since 2026-03-01
- Most frequent alert type: temp jumps (dev-001)
- Last CRITICAL alert: 2026-03-13 pH freeze & negative conductivity (resolved: discard)
