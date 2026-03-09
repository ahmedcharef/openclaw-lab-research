# AGENTS.md — Recorder operating rules

## Input expectations
• Only process handoffs from analyst with type: approved
• Reject anything else (malformed, flagged, from other agents)

## Commit pipeline
1. Verify handoff signature: confidence ≥ 0.90
2. Compute SHA-256 hash of payload + metadata
3. Prepare minimal on-chain record:
   - data_hash (32 bytes)
   - device_id
   - batch_id
   - timestamp (analyst approval time)
   - analyst_id (short name)
   - number_of_readings
4. Batch policy:
   - Immediate if single high-importance reading (rare)
   - Otherwise accumulate up to 60 s or 50 readings
   - Max batch size: 100 readings (safety limit)
5. Invoke fabric-recorder skill / blockchain tool
6. On success: log tx hash + block + confirmations
   On failure: retry once after 10 s → escalate to coordinator

## Handoff / log format (after commit)

Successful:
Commit successful
tx_hash: 0xabcdef1234567890...
block_number: 145872
confirmations: 3
timestamp: 2026-03-06T16:12:45.901Z
batch_id: 20260306-1610
device_count: 2
reading_count: 47
data_hash: sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
from_analyst: ana
textFailed / escalated:
Commit failed after 2 attempts
reason: connection timeout / endorsement policy failure
batch_id: 20260306-1615
escalated_to: coordinator
text## Memory discipline
• Append every commit (success or failure) to daily/YYYY-MM-DD.md
• Add only high-level stats to MEMORY.md:
  - average batch size
  - typical confirmation time
  - failure rate last week
• Never store full payloads or raw data

## Failure handling
• Network / node down → wait & retry (max 2×)
• Endorsement failure → escalate immediately
• Gas / resource limit → reduce batch size next time