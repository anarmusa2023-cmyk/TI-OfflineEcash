# P422 Quorum V1

For N validators tolerating F Byzantine validators:
- N >= 3F + 1
- Q = 2F + 1
- Q distinct signer identities are required
- every vote binds epoch, instance, round and state digest
- signatures use domain separation
- duplicate signers are invalid
- mixed digest/epoch/round certificates are invalid

Two Q-sized quorums intersect in at least F+1 members when N=3F+1.
Therefore, if at most F members are Byzantine, two conflicting certificates
must share at least one honest signer. Honest validators must not sign two
different digests for the same epoch/instance/round.

Liveness requires Q <= N-F. With N=3F+1, Q=2F+1 satisfies the boundary.

This quorum mechanism does NOT solve disconnected offline double-spending.
It protects a replicated decision when the committee can communicate.

Status: protocol-level quorum rules implemented and adversarially tested.
Real-device testing is intentionally out of scope at this stage.
