from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest
from quorum_v1 import VoteGuard, QuorumError, make_vote, state_digest

def test_vote_guard_allows_same_vote_and_rejects_equivocation():
    key = Ed25519PrivateKey.generate()
    guard = VoteGuard()
    a = state_digest(b"A")
    b = state_digest(b"B")
    make_vote("v0", key, 1, b"tx", 2, a, guard)
    make_vote("v0", key, 1, b"tx", 2, a, guard)
    with pytest.raises(QuorumError):
        make_vote("v0", key, 1, b"tx", 2, b, guard)
