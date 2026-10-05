from dataclasses import dataclass
from hashlib import sha256
from threading import Lock
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def h(data): return sha256(data).hexdigest()

@dataclass(frozen=True)
class Spend:
    wallet_id: str
    counter: int
    amount: int
    merchant_id: str
    previous_state_hash: str
    state_hash: str
    signature: bytes

@dataclass(frozen=True)
class PublicWalletState:
    wallet_id: str
    counter: int
    balance: int
    state_hash: str

class SecureElement:
    # Production equivalent: non-exportable key + monotonic hardware counter.
    def __init__(self, wallet_id, initial_balance, private_key=None):
        if initial_balance < 0: raise ValueError("negative initial balance")
        self.wallet_id = wallet_id
        self._balance = initial_balance
        self._counter = 0
        self._key = private_key or Ed25519PrivateKey.generate()
        self._lock = Lock()
        self._state_hash = self._state_hash_for(0, initial_balance)

    @property
    def public_key(self): return self._key.public_key().public_bytes_raw()

    def _state_hash_for(self, counter, balance):
        return h(f"{self.wallet_id}|{counter}|{balance}".encode())

    def public_state(self):
        return PublicWalletState(self.wallet_id, self._counter, self._balance, self._state_hash)

    def spend(self, amount, merchant_id):
        if amount <= 0: raise ValueError("amount must be positive")
        if not merchant_id: raise ValueError("merchant_id required")
        with self._lock:
            if amount > self._balance: raise ValueError("insufficient balance")
            previous = self._state_hash
            counter = self._counter + 1
            balance = self._balance - amount
            state_hash = self._state_hash_for(counter, balance)
            message = f"{self.wallet_id}|{counter}|{amount}|{merchant_id}|{previous}|{state_hash}".encode()
            signature = self._key.sign(message)
            self._counter, self._balance, self._state_hash = counter, balance, state_hash
            return Spend(self.wallet_id, counter, amount, merchant_id, previous, state_hash, signature)

    def export_backup(self):
        return {"wallet_id": self.wallet_id, "counter": self._counter,
                "balance": self._balance, "state_hash": self._state_hash}

def verify_spend(spend, wallet_public_key):
    message = f"{spend.wallet_id}|{spend.counter}|{spend.amount}|{spend.merchant_id}|{spend.previous_state_hash}|{spend.state_hash}".encode()
    try:
        Ed25519PublicKey.from_public_bytes(wallet_public_key).verify(spend.signature, message)
        return True
    except (InvalidSignature, ValueError):
        return False

class Reconciler:
    def __init__(self): self._seen = set()
    def accept(self, spend):
        key = (spend.wallet_id, spend.counter)
        if key in self._seen: return False
        self._seen.add(key)
        return True
