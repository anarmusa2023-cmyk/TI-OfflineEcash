# TI-OfflineEcash

Offline electronic-cash / consensus security research project.

## Current repository state

This repository now contains the current design documents plus a small, auditable **reference state machine** for the critical double-spend / double-finality invariants.

### Security focus

- Atomic consume
- Exactly-once consumption
- Epoch and sequence validation
- Configuration binding
- Quorum-gated finality
- Replay rejection
- Concurrent-consume resistance
- Conflicting-final rejection

The reference implementation is intentionally small and deterministic so the security invariants can be reviewed and attacked independently of networking, cryptography libraries, Android/TEE integration, or production storage.

## Important limitation

Passing the reference tests does **not** mean the production protocol is cryptographically or operationally production-ready. Real deployment still requires real signature verification, Byzantine-network testing, persistent crash/recovery testing, hardware-backed key protection, network adversarial testing, and an independent security audit.

## Layout

- `reference/ledger.py` — minimal reference state machine
- `tests/test_double_spend.py` — adversarial/concurrency tests
- `docs/design-v3.md` — v3 design
- `docs/v4-analysis.txt` — v4 security/architecture analysis
- `docs/security.md` — security scope and current claims

## Run

```bash
python -m unittest discover -s tests -v
```
