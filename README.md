# OpenClaw-Lab 🦞🔬

Agentic laboratory data integrity system built on OpenClaw

## Architecture
- monitor 📡 → analyst 🔍 → recorder ⛓️ → coordinator 🧭

## Agents (in workspace/)
- monitor      first-line stream observer
- analyst      validator & anomaly detector
- recorder     blockchain batch writer
- coordinator  orchestrator & human interface

## Setup
1. Make sure OpenClaw is installed
2. Symlink workspace: `ln -s ~/.openclaw/workspace workspace`
3. (optional) Install custom skills
4. Run: `openclaw start`

## License
MIT
