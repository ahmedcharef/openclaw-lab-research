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
  