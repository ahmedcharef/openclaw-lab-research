# HEARTBEAT.md — Monitor

Executed every 60 seconds:

1. Verify MQTT connection
   → if disconnected >30 s → log warning + attempt reconnect

2. Messages since last heartbeat
   → if >120 → handoff rate warning to coordinator

3. Check oldest pending / un-handled batch
   → if >20 min → force handoff timeout batch

4. Device silence check
   → any known device with no message >5 min → handoff "silent-device" alert

5. Periodic batch trigger
   → every 15 min on the clock → handoff 15-min summary batch

6. Daily log size check
   → if daily/YYYY-MM-DD.md >2 MB → summarize old entries & move to archive

Only report problems or actions taken.  
Silence = everything nominal.