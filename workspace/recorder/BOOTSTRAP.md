# BOOTSTRAP.md — Recorder first run & recovery

On startup:

1. Load blockchain skill: fabric-recorder / chain-write
   - Verify connection to Fabric gateway / test network
   - Load channel, chaincode name from config

2. Send ready signal to coordinator:
Recorder online
Fabric connection: OK
Channel: labresearch
Chaincode: datarecorder
Ready for approved batches
text3. Log startup:
RECORDER START 2026-03-06Txx:xx:xxZ
Batch policy: max 60 s / 50 readings

Reference shared knowledge:
• sensor-metadata.md
• validation-baselines.md
• fabric-config-reference.md
