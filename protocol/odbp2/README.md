# ODBP-2 Offline Double-Spend Bound Protocol

The protocol prevents replay, counter reuse, rollback, transaction tampering,
overspending, and concurrent double-spending when one wallet spend root is
held by one non-exportable Secure Element or TEE.

It does not claim an impossible property: two already-independent devices with
the same economic state and independent signing roots can both spend while
disconnected. Absolute prevention requires a non-clonable hardware root or
shared/online state.

State transition:
1. Check amount is positive and within balance.
2. Increment the monotonic counter.
3. Compute the next state hash.
4. Sign the complete transition.
5. Atomically commit counter, balance, and state hash.

The private spend key is never part of a backup. Device replacement must be
issuer-mediated and must provision a new hardware root rather than restoring
spend authority.

Run: pytest -q
