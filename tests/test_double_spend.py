import threading
import unittest

from reference.ledger import FinalityCertificate, Ledger, Reject


class SecurityTests(unittest.TestCase):
    def cert(self, tx="tx1", decision="COMMIT", **kw):
        return FinalityCertificate(
            tx_id=tx,
            epoch=kw.get("epoch", 1),
            sequence=kw.get("sequence", 1),
            config_hash=kw.get("config_hash", "cfg-v1"),
            decision=decision,
            validators=frozenset(kw.get("validators", {"v1", "v2", "v3"})),
        )

    def test_concurrent_double_consume(self):
        ledger = Ledger()
        results = []
        barrier = threading.Barrier(32)

        def worker():
            barrier.wait()
            try:
                ledger.consume("tx1", epoch=1, sequence=0)
                results.append(True)
            except Reject:
                results.append(False)

        threads = [threading.Thread(target=worker) for _ in range(32)]
        for t in threads: t.start()
        for t in threads: t.join()

        self.assertEqual(sum(results), 1)
        self.assertEqual(ledger.sequence, 1)

    def test_replay_and_double_final_rejected(self):
        ledger = Ledger()
        ledger.consume("tx1", epoch=1, sequence=0)
        ledger.finalize(self.cert())
        with self.assertRaises(Reject):
            ledger.consume("tx1", epoch=1, sequence=1)
        with self.assertRaises(Reject):
            ledger.finalize(self.cert())

    def test_stale_epoch_rejected(self):
        ledger = Ledger(epoch=7)
        with self.assertRaises(Reject):
            ledger.consume("tx1", epoch=6, sequence=0)
        with self.assertRaises(Reject):
            ledger.finalize(self.cert(epoch=6))

    def test_cross_config_final_rejected(self):
        ledger = Ledger()
        ledger.consume("tx1", epoch=1, sequence=0)
        with self.assertRaises(Reject):
            ledger.finalize(self.cert(config_hash="cfg-attacker"))

    def test_insufficient_quorum_rejected(self):
        ledger = Ledger(quorum=3)
        ledger.consume("tx1", epoch=1, sequence=0)
        with self.assertRaises(Reject):
            ledger.finalize(self.cert(validators={"v1", "v2"}))

    def test_phantom_final_rejected(self):
        ledger = Ledger()
        with self.assertRaises(Reject):
            ledger.finalize(self.cert("never-consumed"))

    def test_conflicting_final_rejected(self):
        ledger = Ledger()
        ledger.consume("tx1", epoch=1, sequence=0)
        ledger.finalize(self.cert(decision="COMMIT"))
        with self.assertRaises(Reject):
            ledger.finalize(self.cert(decision="ABORT"))


if __name__ == "__main__":
    unittest.main()
