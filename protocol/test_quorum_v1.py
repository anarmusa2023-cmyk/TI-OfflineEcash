from dataclasses import replace
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from quorum_v1 import QuorumError, QuorumCertificate, certificate, make_vote, quorum_size, state_digest, verify_certificate

def committee(n):
    priv, keys = {}, {}
    for i in range(n):
        k = Ed25519PrivateKey.generate()
        name = f"v{i}"
        priv[name] = k
        keys[name] = k.public_key().public_bytes_raw()
    return priv, keys

def test_quorum_formula():
    assert quorum_size(4, 1) == 3
    assert quorum_size(7, 2) == 5
    assert quorum_size(10, 3) == 7

def test_reject_unsafe_committee():
    with pytest.raises(ValueError):
        quorum_size(3, 1)

def test_valid_certificate():
    priv, keys = committee(4)
    d = state_digest(b"A")
    votes = [make_vote(x, priv[x], 1, b"tx1", 7, d) for x in ("v0","v1","v2")]
    assert verify_certificate(certificate(votes, keys, 1), keys, 1)

def test_duplicate_signer_rejected():
    priv, keys = committee(4)
    d = state_digest(b"A")
    v = make_vote("v0", priv["v0"], 1, b"tx1", 7, d)
    with pytest.raises(QuorumError):
        certificate([v, v, make_vote("v1", priv["v1"], 1, b"tx1", 7, d)], keys, 1)

def test_mixed_digest_rejected():
    priv, keys = committee(4)
    a, b = state_digest(b"A"), state_digest(b"B")
    votes = [make_vote("v0", priv["v0"], 1, b"tx1", 7, a),
             make_vote("v1", priv["v1"], 1, b"tx1", 7, a),
             make_vote("v2", priv["v2"], 1, b"tx1", 7, b)]
    with pytest.raises(QuorumError):
        certificate(votes, keys, 1)

def test_wrong_epoch_rejected():
    priv, keys = committee(4)
    d = state_digest(b"A")
    votes = [make_vote("v0", priv["v0"], 1, b"tx1", 7, d),
             make_vote("v1", priv["v1"], 2, b"tx1", 7, d),
             make_vote("v2", priv["v2"], 1, b"tx1", 7, d)]
    with pytest.raises(QuorumError):
        certificate(votes, keys, 1)

def test_tampered_signature_rejected():
    priv, keys = committee(4)
    d = state_digest(b"A")
    v = make_vote("v0", priv["v0"], 1, b"tx1", 7, d)
    bad = QuorumCertificate(1, b"tx1", 7, d, (replace(v, signature=b"bad"),))
    assert not verify_certificate(bad, keys, 1)

def test_conflicting_quorums_intersect_in_more_than_f():
    # N=4,F=1,Q=3. Any two Q-sized sets intersect in >=2 > F.
    a = {"v0","v1","v2"}
    candidates = [{"v0","v1","v3"},{"v0","v2","v3"},{"v1","v2","v3"}]
    assert all(len(a & c) >= 2 for c in candidates)

def test_old_epoch_cannot_be_relabelled():
    priv, keys = committee(4)
    d = state_digest(b"A")
    old = make_vote("v0", priv["v0"], 4, b"tx1", 1, d)
    forged = QuorumCertificate(5, b"tx1", 1, d, (old,))
    assert not verify_certificate(forged, keys, 1)
