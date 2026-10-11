"""TTL expiry must be independent of wall-clock adjustments."""

from openbb_core.provider.utils import lru


def test_clock_correction_cannot_revive_older_cache(monkeypatch):
    wall = [1000.0]
    elapsed = [100.0]
    monkeypatch.setattr(lru.time, "time", lambda: wall[0])
    monkeypatch.setattr(lru.time, "monotonic", lambda: elapsed[0])
    calls = []

    @lru.ttl_cache(ttl=10)
    def fetch():
        calls.append(len(calls) + 1)
        return calls[-1]

    assert fetch() == 1
    wall[0] += 11
    elapsed[0] += 11
    assert fetch() == 2
    wall[0] -= 11
    elapsed[0] += 1
    assert fetch() == 2
    assert calls == [1, 2]
