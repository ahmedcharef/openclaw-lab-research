# OpenClaw-Lab

[![License:
MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw
Version](https://img.shields.io/badge/OpenClaw-v1.0-blue)](https://github.com/openclaw/openclaw)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)](https://www.python.org/)

OpenClaw-Lab is an agentic AI framework that integrates OpenClaw with **simulated** IoT sensors, MQTT middleware, multi-agent workflows, and Hyperledger Fabric blockchain. It demonstrates autonomous, secure, and traceable handling of laboratory-style research data — from generation and real-time observation through validation and immutable recording.

The system is currently built around **software simulation** of IoT devices (temperature, humidity, pH, etc.) and is designed as a clean, modular prototype that can later be extended to real hardware.

## Features

- **Multi-Agent System**: Four specialized agents (Monitor, Analyst,
    Recorder, Coordinator) for data observation, validation, blockchain
    commits, and orchestration.
- **Simulated IoT Sensors**: Python-based simulators for environmental
    (temperature, humidity, pressure) and chemical (pH, conductivity)
    sensors with realistic noise and patterns.
- **Middleware Integration**: MQTT for real-time data streaming and
    queuing.
- **Blockchain for Integrity**: Hyperledger Fabric for immutable,
    timestamped data storage with smart contracts for recording and
    auditing.
- **Custom Skills**: OpenClaw tools for MQTT subscription, data
    validation, and Fabric interactions.
- **Memory Management**: Layered memory (daily logs, curated
    MEMORY.md) with heartbeat-driven curation to prevent context rot.
- **Human Interface**: Coordinator agent handles user queries via chat
    (e.g., Telegram) for status, audits, and alerts.
- **Security Focus**: Strict boundaries in agent SOUL.md files,
    sandboxed tools, and no direct data modification.
- **Extensibility**: Modular workspaces, configurable YAML for
    sensors/ranges, and easy transition to real hardware (e.g.,
    Raspberry Pi).

## Architecture Overview

The system follows a modular, agentic pipeline:

1. **Simulated Sensors** → Publish data to MQTT topics (e.g.,
    `/lab/env/temp`).
2. **Monitor Agent** → Observes streams, performs lightweight checks,
    hands off batches/anomalies.
3. **Analyst Agent** → Validates integrity, detects
    anomalies/correlations, assigns confidence.
4. **Recorder Agent** → Batches approved data, computes hashes, commits
    to Fabric blockchain.
5. **Coordinator Agent** → Orchestrates handoffs, summarizes status,
    interfaces with users.

For detailed agent behaviors, see the Markdown files in
`workspace/<agent>/`.

```html
Simulated IoT Sensors
        │
        ▼
   MQTT Broker
        │
        ▼
  Monitor Agent
        │
        ▼
  Analyst Agent
        │
        ▼
 Recorder Agent ──► Hyperledger Fabric
        │
        ▼
Coordinator Agent ◄──► User (Chat / Telegram)
```
## Prerequisites

- Python 3.10+
- OpenClaw installed (via
    `curl -fsSL https://openclaw.ai/install.sh | bash`)
- MQTT broker (e.g., Mosquitto:
    `docker run -p 1883:1883 eclipse-mosquitto`)
- Hyperledger Fabric test network (setup via Fabric samples or Docker)
- Optional: Docker for containerized deployment

## Installation

1. Clone the repository:

    ``` bash
    git clone https://github.com/ahmedcharef/openclaw-lab-research
    cd openclaw-lab-research
    ```

2. Set up OpenClaw workspace (copy project files to live location):

    ``` bash
    cp -r workspace ~/.openclaw/workspace
    cp -r skills ~/.openclaw/skills
    cp -r knowledge ~/.openclaw/knowledge
    cp -r config/*.yaml ~/.openclaw/config/
    ```

3. Install Python dependencies for simulators:

    ``` bash
    pip install paho-mqtt numpy scipy
    ```

4. Start supporting services (MQTT and Fabric):

    ``` bash
    docker run -d -p 1883:1883 --name mqtt-broker eclipse-mosquitto
    ./scripts/setup-fabric.sh
    ```

5. Start OpenClaw:

    ``` bash
    openclaw start --workspace ~/.openclaw/workspace
    ```

## Usage

### Running the Simulator

Start simulated sensors to publish data:

``` bash
python src/hardware/simulators/gateway_sim.py
```

### Interacting with Agents

Use OpenClaw chat (e.g., Telegram integration): - "status" → Get system
overview. - "audit batch 20260306-1545" → Retrieve transaction
details. - "show anomalies today" → List flagged issues.

Example response:

    System Status — 2026-03-06
    • Active devices: 2 (dev-001-labA, dev-002-labB)
    • Commits today: 12 (last tx: 0xabc...)
    • Anomalies: 1 (temp jump on dev-001)

### Example Workflow

1. Simulator publishes temp=26.8 to MQTT.
2. Monitor checks and hands off batch.
3. Analyst validates (confidence 0.94) → approves to recorder.
4. Recorder commits hash to Fabric → logs tx.
5. Coordinator alerts if anomaly flagged.

## Configuration

Key configs:

- `config/sim/sensors.yaml`
- `knowledge/projects/lab-experiments/validation-baselines.md`
- `config/agents.yaml`
- `skills/fabric-recorder/connection_profile.yaml`

Customize agent behaviors by editing Markdown files in
`workspace/<agent>/`.

## API Reference

### Custom Skills

- **mqtt-lab**
- **fabric-recorder**
- **lab-validator**

Full docs in `skills/<skill>/manifest.json` and `docs/skills.md`.

## Contributing

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/new-skill`.
3. Commit changes.
4. Push and open a Pull Request.

## Roadmap

- Integrate real IoT hardware
- Add ML-enhanced anomaly detection
- Dashboard UI
- Multi-lab federation
- Full security audit

## Acknowledgments

- Built on OpenClaw by xAI community.
- Inspired by agentic AI patterns.
- Thanks to Hyperledger Fabric.

## License

MIT License
