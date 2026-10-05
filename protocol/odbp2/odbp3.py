from threading import Lock

class IssuerRegistry:
    def __init__(self):
        self._current={}; self._revoked=set(); self._lock=Lock()
    def provision(self,wallet_id,device_id,public_key):
        with self._lock:
            if wallet_id in self._current: raise ValueError('wallet already provisioned; migration required')
            self._current[wallet_id]=(device_id,public_key)
    def migrate(self,wallet_id,old_device_id,new_device_id,new_public_key):
        with self._lock:
            if self._current.get(wallet_id)!=(old_device_id,self._current[wallet_id][1]): raise ValueError('invalid migration')
            self._revoked.add((wallet_id,old_device_id)); self._current[wallet_id]=(new_device_id,new_public_key)
    def current(self,wallet_id): return self._current.get(wallet_id)
    def is_current(self,wallet_id,device_id,public_key): return self._current.get(wallet_id)==(device_id,public_key) and (wallet_id,device_id) not in self._revoked
