"""Run id generation helpers with feature-flagged schemes."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from openbb_quant_ml.service.constants import RUNS_DIR
from openbb_quant_ml.service.storage import read_registry

DEFAULT_RUN_ID_SCHEME = "compact_v1"
DEFAULT_RUN_ID_TIMEZONE = "Asia/Seoul"
SUPPORTED_RUN_ID_SCHEMES = {"legacy", "compact_v1"}

_JOB_PREFIX: dict[str, str] = {
    "daily": "dly",
    "weekly": "wkl",
    "monthly": "mth",
}


def normalize_run_id_scheme(
    value: str | None, *, default: str = DEFAULT_RUN_ID_SCHEME
) -> str:
    """Normalize run id scheme string."""
    candidate = str(value or "").strip().lower()
    if candidate in SUPPORTED_RUN_ID_SCHEMES:
        return candidate
    return default


def _now_local(timezone_name: str | None) -> datetime:
    zone_name = (
        str(timezone_name or DEFAULT_RUN_ID_TIMEZONE).strip() or DEFAULT_RUN_ID_TIMEZONE
    )
    try:
        zone = ZoneInfo(zone_name)
    except Exception:
        zone = UTC
    return datetime.now(zone).replace(microsecond=0)


def _existing_run_ids() -> set[str]:
    run_ids: set[str] = set()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    for path in RUNS_DIR.iterdir():
        if path.is_dir():
            run_ids.add(path.name)

    payload = read_registry()
    runs = payload.get("runs", {})
    if isinstance(runs, dict):
        run_ids.update(str(item) for item in runs.keys())
    return run_ids


def _next_compact_id(prefix: str, date_token: str, width: int) -> str:
    existing = _existing_run_ids()
    pattern = re.compile(
        rf"^{re.escape(prefix)}-{re.escape(date_token)}-(\d{{{width}}})$"
    )

    highest = 0
    for run_id in existing:
        matched = pattern.match(run_id)
        if not matched:
            continue
        highest = max(highest, int(matched.group(1)))

    max_seq = (10**width) - 1
    for seq in range(highest + 1, max_seq + 1):
        candidate = f"{prefix}-{date_token}-{seq:0{width}d}"
        if candidate not in existing:
            return candidate
    raise ValueError(
        f"run id sequence exhausted for prefix={prefix}, date={date_token}"
    )


def build_job_run_id(
    job_name: str,
    *,
    run_id_scheme: str = DEFAULT_RUN_ID_SCHEME,
    timezone: str = DEFAULT_RUN_ID_TIMEZONE,
) -> tuple[str, str]:
    """Return (run_id, run_date_iso) for job runs."""
    scheme = normalize_run_id_scheme(run_id_scheme)
    local_now = _now_local(timezone)
    run_date = local_now.date().isoformat()

    if scheme == "legacy":
        ts = datetime.now(UTC).replace(microsecond=0).strftime("%Y%m%d-%H%M%S")
        return f"{ts}-{uuid4().hex[:8]}", run_date

    prefix = _JOB_PREFIX.get(str(job_name).strip().lower(), "job")
    date_token = local_now.strftime("%y%m%d")
    return _next_compact_id(prefix, date_token, width=2), run_date


def build_training_run_id(
    *,
    run_id_scheme: str = DEFAULT_RUN_ID_SCHEME,
    timezone: str = DEFAULT_RUN_ID_TIMEZONE,
) -> str:
    """Return run id for model training runs."""
    scheme = normalize_run_id_scheme(run_id_scheme)
    if scheme == "legacy":
        return uuid4().hex

    local_now = _now_local(timezone)
    date_token = local_now.strftime("%y%m%d")
    return _next_compact_id("trn", date_token, width=3)
