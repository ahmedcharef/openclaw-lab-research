# BOOTSTRAP.md — Coordinator first run & recovery

On startup:

1. Verify all other agents have sent "online" messages
   (monitor, analyst, recorder)

2. Send welcome / status to human channel:
🦞 LabClaw Coordinator online!
Date: 2026-03-06
Agents ready: monitor, analyst, recorder
Known experiments: 1 active
Say "status" for overview or ask about any batch/device.

3. Log startup:
COORDINATOR START 2026-03-06Txx:xx:xxZ
Human channel: Telegram @labclaw_bot (or configured)
