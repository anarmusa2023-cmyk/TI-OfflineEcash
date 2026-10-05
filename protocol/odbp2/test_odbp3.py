import pytest
from odbp2_v3 import SecureElement
from odbp3 import IssuerRegistry

def test_one_wallet_one_device():
    r=IssuerRegistry(); SecureElement('W1','D1',100,r)
    with pytest.raises(ValueError): SecureElement('W1','D2',100,r)

def test_migration_revokes_old_device():
    r=IssuerRegistry(); old=SecureElement('W1','D1',100,r); new=SecureElement('W2','D2',1,r)
    r.migrate('W1','D1','D2',new.public_key)
    assert not r.is_current('W1','D1',old.public_key)
    assert r.is_current('W1','D2',new.public_key)

def test_old_device_cannot_be_current_after_migration():
    r=IssuerRegistry(); old=SecureElement('W1','D1',100,r); new=SecureElement('W2','D2',1,r)
    r.migrate('W1','D1','D2',new.public_key)
    assert r.current('W1')[0]=='D2'
