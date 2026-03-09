# HEARTBEAT.md — Analyst

Run every 300 seconds (5 min):

1. Scan pending handoffs in TASKS.md
   → if >4 unprocessed (>15 min) → alert coordinator "queue backlog"

2. Review last hour of daily log
   → Compute rolling stats (means, std devs per device)
   → If new drift/trend detected (e.g., temp +0.4 °C/hour) → append to MEMORY.md

3. Memory curation
   → If daily log > 600 lines → summarize: "Extract top 5 patterns/anomalies → append MEMORY.md"

4. Proactive pattern check
   → Scan MEMORY.md for recurring issues (e.g., same anomaly >3× in 24h)
   → If found → handoff to coordinator: "Suggest maintenance on dev-XXX"

5. Feedback loop
   → For recent approvals → check recorder response (tx success?)
   → Log any discrepancies

Silence = healthy operation. Only log actions taken.