# Security Status

## Reference-state invariants

The reference implementation enforces:

1. A note/asset can be consumed at most once.
2. Consumption is atomic with the state transition.
3. A stale epoch is rejected.
4. A sequence that does not match the current expected sequence is rejected.
5. A finality certificate is bound to the exact configuration hash.
6. A finality certificate must contain a quorum of distinct validators.
7. Conflicting final decisions for the same transaction are rejected.
8. A finalized transaction cannot be finalized again.
9. Replay of an already-consumed transaction is rejected.
10. Concurrent attempts cannot both consume the same note.

## What this proves

The test suite checks these invariants against the reference state machine.

## What this does not prove

It does not prove:
- cryptographic security of ML-DSA/Falcon/SLH-DSA implementations;
- correctness of a distributed network implementation;
- safety under arbitrary Byzantine message scheduling;
- safety across real crash/recovery and persistent-storage failures;
- Android/TEE/secure-element anti-cloning guarantees;
- production readiness.

Those require additional implementation and independent audit.
