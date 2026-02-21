"""Tests for stale lock recovery in jobs lock helper."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
from openbb_quant_ml.jobs import lock as lk


def _write_lock(path: Path, pid_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pid_text, encoding="utf-8")


def test_job_lock_recovers_dead_pid_lock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(lk, "ARTIFACT_ROOT", tmp_path)
    lock_path = tmp_path / ".locks" / "bootstrap.lock"
    _write_lock(lock_path, "999999")

    with lk.job_lock("bootstrap", timeout_sec=1, stale_ttl_sec=3600):
        assert lock_path.exists()
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
        assert int(payload["pid"]) == os.getpid()
        assert payload.get("created_at")

    assert lock_path.exists() is False


def test_job_lock_recovers_old_lock_even_if_pid_looks_alive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(lk, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(lk, "_is_pid_running", lambda pid: True)
    lock_path = tmp_path / ".locks" / "bootstrap.lock"
    _write_lock(lock_path, "12345")
    old_ts = time.time() - 7200
    os.utime(lock_path, (old_ts, old_ts))

    with lk.job_lock("bootstrap", timeout_sec=1, stale_ttl_sec=60):
        assert lock_path.exists()
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
        assert int(payload["pid"]) == os.getpid()

    assert lock_path.exists() is False


def test_job_lock_raises_when_live_fresh_lock_is_busy(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(lk, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(lk, "_is_pid_running", lambda pid: True)
    lock_path = tmp_path / ".locks" / "bootstrap.lock"
    _write_lock(lock_path, "12345")

    with pytest.raises(TimeoutError, match="job lock busy: bootstrap"):
        with lk.job_lock("bootstrap", timeout_sec=0, stale_ttl_sec=3600):
            pass


def test_job_lock_reports_permission_denied_reason_for_stale_lock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setattr(lk, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(lk, "_is_pid_running", lambda pid: False)
    lock_path = tmp_path / ".locks" / "bootstrap.lock"
    _write_lock(lock_path, "12345")

    def _raise_permission(*args, **kwargs):  # noqa: ANN002, ARG001
        raise PermissionError("in use")

    monkeypatch.setattr(Path, "unlink", _raise_permission)
    with pytest.raises(
        TimeoutError,
        match="reason=lock_in_use_permission_denied",
    ), lk.job_lock("bootstrap", timeout_sec=0, stale_ttl_sec=3600):
        pass
