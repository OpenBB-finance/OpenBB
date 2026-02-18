"""Single-machine file lock helpers for scheduled jobs."""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from openbb_quant_ml.service.constants import ARTIFACT_ROOT


@contextmanager
def job_lock(job_name: str, timeout_sec: int = 1) -> Iterator[None]:
    """Acquire/release file-based lock for a job name."""
    lock_dir = ARTIFACT_ROOT / ".locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{job_name}.lock"

    started = time.time()
    fd: int | None = None
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            break
        except FileExistsError:
            if (time.time() - started) > timeout_sec:
                raise TimeoutError(f"job lock busy: {job_name}") from None
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
