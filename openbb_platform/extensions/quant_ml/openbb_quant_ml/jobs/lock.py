"""Single-machine file lock helpers for scheduled jobs."""

from __future__ import annotations

import json
import os
import socket
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openbb_quant_ml.service.constants import ARTIFACT_ROOT

DEFAULT_STALE_LOCK_TTL_SEC = 6 * 60 * 60


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _read_lock_payload(lock_path: Path) -> dict[str, Any] | None:
    try:
        text = lock_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text:
        return None
    # Backward compatibility: legacy lock files contain PID only.
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            pid = parsed.get("pid")
            try:
                parsed["pid"] = int(pid) if pid is not None else None
            except (TypeError, ValueError):
                parsed["pid"] = None
            return parsed
    except json.JSONDecodeError:
        pass
    try:
        pid = int(text)
        return {"pid": pid, "created_at": None, "host": None, "command": None}
    except ValueError:
        return None


def _read_lock_pid(lock_path: Path) -> int | None:
    payload = _read_lock_payload(lock_path)
    if not isinstance(payload, dict):
        return None
    pid = payload.get("pid")
    try:
        return int(pid) if pid is not None else None
    except (TypeError, ValueError):
        return None


def _is_pid_running(pid: int | None) -> bool:
    if pid is None or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        # PID exists but current user cannot signal it.
        return True
    except OSError:
        return False


def _lock_age_seconds(lock_path: Path) -> float:
    try:
        return max(0.0, time.time() - float(lock_path.stat().st_mtime))
    except OSError:
        return 0.0


def inspect_lock(lock_path: Path, stale_ttl_sec: int) -> dict[str, Any]:
    """Inspect lock payload and return health metadata."""
    if not lock_path.exists():
        return {
            "exists": False,
            "health": "missing",
            "reason": "lock_missing",
            "pid": None,
            "age_sec": 0.0,
            "pid_running": False,
            "stale": False,
        }

    payload = _read_lock_payload(lock_path) or {}
    pid = payload.get("pid")
    pid_running = _is_pid_running(int(pid) if isinstance(pid, int) else None)
    age_sec = _lock_age_seconds(lock_path)
    stale = (not pid_running) or age_sec >= float(max(1, stale_ttl_sec))
    if stale:
        reason = "pid_dead" if not pid_running else "lock_ttl_expired"
        health = "stale"
    else:
        reason = "lock_in_use"
        health = "ok"

    return {
        "exists": True,
        "health": health,
        "reason": reason,
        "pid": pid,
        "age_sec": age_sec,
        "pid_running": pid_running,
        "stale": stale,
        "created_at": payload.get("created_at"),
        "host": payload.get("host"),
        "command": payload.get("command"),
    }


def _is_stale_lock(lock_path: Path, stale_ttl_sec: int) -> bool:
    return bool(inspect_lock(lock_path, stale_ttl_sec).get("stale", False))


@contextmanager
def job_lock(
    job_name: str,
    timeout_sec: int = 1,
    stale_ttl_sec: int = DEFAULT_STALE_LOCK_TTL_SEC,
) -> Iterator[None]:
    """Acquire/release file-based lock for a job name."""
    lock_dir = ARTIFACT_ROOT / ".locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{job_name}.lock"

    started = time.time()
    fd: int | None = None
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            payload = {
                "pid": os.getpid(),
                "created_at": _utc_now_iso(),
                "host": socket.gethostname(),
                "command": " ".join(os.sys.argv),
            }
            os.write(fd, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            break
        except FileExistsError:
            lock_info = inspect_lock(lock_path, stale_ttl_sec=stale_ttl_sec)
            if bool(lock_info.get("stale", False)):
                try:
                    lock_path.unlink(missing_ok=True)
                except PermissionError:
                    if (time.time() - started) > timeout_sec:
                        raise TimeoutError(
                            f"job lock busy: {job_name} (reason=lock_in_use_permission_denied)"
                        ) from None
                    time.sleep(0.1)
                    continue
                except OSError:
                    if (time.time() - started) > timeout_sec:
                        raise TimeoutError(
                            f"job lock busy: {job_name} (reason=lock_remove_failed)"
                        ) from None
                    time.sleep(0.1)
                    continue
                continue
            if (time.time() - started) > timeout_sec:
                reason = str(lock_info.get("reason", "lock_in_use"))
                raise TimeoutError(
                    f"job lock busy: {job_name} (reason={reason})"
                ) from None
            time.sleep(0.1)

    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            Path(lock_path).unlink(missing_ok=True)
        except OSError:
            pass
