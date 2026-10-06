"""P422 Quorum Certificate V1.

Safety: N >= 3F+1 and Q = 2F+1.
A certificate needs Q distinct committee members, all signing the exact same
domain/epoch/instance/round/digest. This is protocol-level protection only.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Sequence
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN = b"P422-QC-V1"

def quorum_size(n: int, f: int) -> int:
    if n <= 0 or f < 0:
        raise ValueError("invalid committee parameters")
    if n < 3 * f + 1:
        raise ValueError("unsafe committee: require n >= 3f+1")
    return 2 * f + 1

def _message(epoch: int, instance: bytes, round_no: int, digest: bytes) -> bytes:
    if epoch < 0 or round_no < 0:
        raise ValueError("epoch/round must be non-negative")
    return b"|".join((DOMAIN, epoch.to_bytes(8, "big"),
                      len(instance).to_bytes(4, "big"), instance,
                      round_no.to_bytes(8, "big"),
                      len(digest).to_bytes(4, "big"), digest))

@dataclass(frozen=True)
class Vote:
    signer: str
    epoch: int
    instance: bytes
    round_no: int
    digest: bytes
    signature: bytes

@dataclass(frozen=True)
class QuorumCertificate:
    epoch: int
    instance: bytes
    round_no: int
    digest: bytes
    votes: tuple[Vote, ...]
    @property
    def signers(self) -> frozenset[str]:
        return frozenset(v.signer for v in self.votes)

class QuorumError(ValueError):
    pass

def verify_certificate(qc: QuorumCertificate, committee_keys: Mapping[str, bytes], f: int) -> bool:
    n = len(committee_keys)
    q = quorum_size(n, f)
    if len(qc.votes) < q or len(qc.signers) != len(qc.votes):
        return False
    for vote in qc.votes:
        if vote.signer not in committee_keys:
            return False
        if (vote.epoch, vote.instance, vote.round_no, vote.digest) != (
            qc.epoch, qc.instance, qc.round_no, qc.digest):
            return False
        try:
            Ed25519PublicKey.from_public_bytes(committee_keys[vote.signer]).verify(
                vote.signature,
                _message(vote.epoch, vote.instance, vote.round_no, vote.digest))
        except Exception:
            return False
    return True

def make_vote(signer: str, private_key, epoch: int, instance: bytes, round_no: int, digest: bytes) -> Vote:
    return Vote(signer, epoch, instance, round_no, digest,
                private_key.sign(_message(epoch, instance, round_no, digest)))

def certificate(votes: Sequence[Vote], committee_keys: Mapping[str, bytes], f: int) -> QuorumCertificate:
    if not votes:
        raise QuorumError("empty vote set")
    first = votes[0]
    qc = QuorumCertificate(first.epoch, first.instance, first.round_no, first.digest, tuple(votes))
    if not verify_certificate(qc, committee_keys, f):
        raise QuorumError("invalid quorum certificate")
    return qc

def state_digest(state: bytes) -> bytes:
    return sha256(state).digest()
