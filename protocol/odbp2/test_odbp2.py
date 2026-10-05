import concurrent.futures
import pytest
from odbp2 import SecureElement, Reconciler, verify_spend

def test_sequential_spends_are_unique_and_balance_decreases():
    w = SecureElement("W1", 100)
    a, b = w.spend(60, "M1"), w.spend(40, "M2")
    assert (a.counter, b.counter, w.public_state().balance) == (1, 2, 0)
    assert a.signature != b.signature

def test_replay_is_rejected():
    w, r = SecureElement("W1", 100), Reconciler()
    s = w.spend(25, "M1")
    assert r.accept(s) is True
    assert r.accept(s) is False

@pytest.mark.parametrize("field,value", [
    ("amount", 99), ("merchant_id", "MALICIOUS"), ("counter", 99),
    ("previous_state_hash", "00"*32), ("state_hash", "11"*32)])
def test_tampering_breaks_signature(field, value):
    w = SecureElement("W1", 100)
    s = w.spend(10, "M1")
    d = s.__dict__.copy(); d[field] = value
    forged = type(s)(**d)
    assert verify_spend(s, w.public_key)
    assert not verify_spend(forged, w.public_key)

def test_overspend_is_atomic():
    w = SecureElement("W1", 50)
    with pytest.raises(ValueError, match="insufficient"): w.spend(51, "M1")
    assert w.public_state().counter == 0
    assert w.public_state().balance == 50

def test_concurrent_spends_have_unique_counters():
    w = SecureElement("W1", 1000)
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as ex:
        spends = list(ex.map(lambda _: w.spend(1, "M"), range(1000)))
    counters = [s.counter for s in spends]
    assert len(set(counters)) == 1000
    assert sorted(counters) == list(range(1, 1001))
    assert w.public_state().balance == 0

def test_backup_excludes_spend_key():
    w = SecureElement("W1", 100); w.spend(10, "M1")
    backup = w.export_backup()
    assert "_key" not in backup and "private_key" not in backup and "seed" not in backup

def test_two_merchants_cannot_double_spend_one_secure_element():
    w, r = SecureElement("W1", 100), Reconciler()
    first = w.spend(100, "M1")
    assert r.accept(first)
    with pytest.raises(ValueError, match="insufficient"): w.spend(100, "M2")
    assert w.public_state().balance == 0

def test_clone_boundary_is_explicitly_unprovable_offline():
    w1, w2 = SecureElement("W1", 100), SecureElement("W1", 100)
    s1, s2 = w1.spend(100, "M1"), w2.spend(100, "M2")
    assert s1.counter == s2.counter == 1
    assert s1.wallet_id == s2.wallet_id == "W1"
    assert s1.signature != s2.signature
