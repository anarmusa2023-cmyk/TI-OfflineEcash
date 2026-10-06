"""Minimal deterministic reference state machine for offline-cash safety invariants."""

from dataclasses import dataclass
from threading import Lock


class Reject(Exception):
    pass


@dataclass(frozen=True)
class FinalityCertificate:
    tx_id: str
    epoch: int
    sequence: int
    config_hash: str
    decision: str
    validators: frozenset[str]


class Ledger:
    def __init__(self, *, epoch=1, config_hash="cfg-v1", quorum=3):
        if quorum < 1:
            raise ValueError("quorum must be positive")
        self.epoch = epoch
        self.config_hash = config_hash
        self.quorum = quorum
        self.sequence = 0
        self.consumed = set()
        self.finalized = {}
        self._lock = Lock()

    def consume(self, tx_id, *, epoch, sequence):
        with self._lock:
            if epoch != self.epoch:
                raise Reject("stale epoch")
            if sequence != self.sequence:
                raise Reject("invalid sequence")
            if tx_id in self.consumed:
                raise Reject("double consume")
            self.consumed.add(tx_id)
            self.sequence += 1
            return True

    def finalize(self, cert: FinalityCertificate):
        with self._lock:
            if cert.epoch != self.epoch:
                raise Reject("stale final")
            if cert.sequence < 1 or cert.sequence > self.sequence:
                raise Reject("invalid final sequence")
            if cert.config_hash != self.config_hash:
                raise Reject("cross-config final")
            if len(cert.validators) < self.quorum:
                raise Reject("insufficient quorum")
            if cert.tx_id in self.finalized:
                if self.finalized[cert.tx_id] == cert.decision:
                    raise Reject("double final")
                raise Reject("conflicting final")
            if cert.tx_id not in self.consumed:
                raise Reject("phantom final")
            self.finalized[cert.tx_id] = cert.decision
            return True
