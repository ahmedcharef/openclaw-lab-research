# Fabric Configuration Reference — OpenClaw-Lab

Used by: recorder agent

## Network Basics

Network type:          development / single-org testnet
Orderer:               orderer.example.com:7050
Channel:               labresearch
Chaincode name:        datarecorder
Chaincode version:     1.0 (initial)

## Connection Profile (simplified – real skill uses full JSON)

{
  "name": "lab-testnet",
  "version": "1.0.0",
  "client": {
    "organization": "LabOrgMSP",
    "credentialStore": {
      "path": "~/.fabric/credentials"
    }
  },
  "channels": {
    "labresearch": {
      "orderers": ["orderer.example.com"],
      "peers": {
        "peer0.laborg.example.com": {}
      }
    }
  },
  "organizations": {
    "LabOrgMSP": {
      "mspid": "LabOrgMSP",
      "peers": ["peer0.laborg.example.com"]
    }
  },
  "orderers": {
    "orderer.example.com": {
      "url": "grpcs://localhost:7050",
      "grpcOptions": {
        "ssl-target-name-override": "orderer.example.com"
      }
    }
  },
  "peers": {
    "peer0.laborg.example.com": {
      "url": "grpcs://localhost:7051",
      "grpcOptions": {
        "ssl-target-name-override": "peer0.laborg.example.com"
      }
    }
  }
}

## Important Notes for Recorder

• Use fabric-sdk skill / chain-write tool
• Payload structure expected by chaincode:
  {
    "data_hash": "sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "device_id": "dev-001-labA",
    "batch_id": "20260309-1430",
    "timestamp": "2026-03-09T14:30:00Z",
    "analyst": "ana",
    "readings_count": 42
  }
• Transaction timeout: 30 seconds
• Batch size recommendation: 20–80 readings
• Endorsement policy: AND('LabOrgMSP.member')  (single org for dev)
