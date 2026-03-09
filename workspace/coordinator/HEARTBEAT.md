# HEARTBEAT.md — Coordinator

Run every 600 seconds (10 min):

1. Collect status from all agents
   → Check last message / activity timestamp

2. Review pending queues
   → Any agent with >3 pending items >10 min → alert human

3. Daily summary trigger
   → If after 19:00 UTC and not yet sent → generate & send end-of-day report

4. Health rollup
   → If any agent silent >20 min → escalate "agent unresponsive"

5. Memory curation
   → Extract key events from daily log → append MEMORY.md
   → If daily >700 lines → summarize & archive

Only report problems or scheduled summaries.  
Silence = nominal operation.