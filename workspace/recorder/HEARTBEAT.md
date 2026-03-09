# HEARTBEAT.md — Recorder

Run every 180 seconds (3 min):

1. Check pending commit queue (TASKS.md)
   → if >3 batches waiting >5 min → alert coordinator "commit backlog"

2. Review recent commits
   → Calculate rolling stats: avg batch size, confirm time, failure %

3. If failure rate >5% last hour → handoff to coordinator:
   "Elevated commit failure rate – possible network/peer issue"

4. Batch timeout check
   → If oldest pending batch > 120 s → force commit (even small)

5. Memory curation
   → If daily log >400 lines → summarize stats → append MEMORY.md

Silence = healthy chain writes.