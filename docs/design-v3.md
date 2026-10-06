# Consensus Project v3 — Design Draft

This document is the v3 design draft preserved from the project working documents.

> Status: design/research document, not a production blockchain specification.

## Goals

- Sustainable high throughput
- Mobile validators
- Parallel color/shard architecture
- VRF-based validator selection
- Post-quantum signature research
- Zero-fee operation with quota controls
- Checkpoint/finality mechanisms

## Critical security area

Cross-color atomicity and finality are higher priority than headline TPS. Fast confirmation must not be treated as irreversible finality without the required quorum and challenge/finality rules.

## Performance discipline

TPS claims must be accompanied by transaction size, cross-color ratio, validator participation, and P50/P95/P99 finality/latency measurements.

See the original v3 analysis in the project history for the complete design assumptions and simulation results.
