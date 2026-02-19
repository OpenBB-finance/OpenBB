"""In-memory and on-disk run status registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from threading import RLock
from typing import Any

from openbb_quant_ml.service.constants import MAX_LOG_LINES
from openbb_quant_ml.service.run_id import (
    DEFAULT_RUN_ID_SCHEME,
    DEFAULT_RUN_ID_TIMEZONE,
    build_training_run_id,
    normalize_run_id_scheme,
)
from openbb_quant_ml.service.storage import (
    get_run_dir,
    read_registry,
    utc_now_iso,
    write_registry,
)


@dataclass
class RunState:
    """Run lifecycle state."""

    run_id: str
    status: str
    progress: int
    stage: str
    created_at: str
    updated_at: str
    logs_tail: list[str]
    error: str | None
    artifact_root: str


_RUN_STATES: dict[str, RunState] = {}
_LOCK = RLock()


def _load_states_from_disk() -> None:
    """Hydrate in-memory state cache from disk registry."""
    payload = read_registry()
    runs = payload.get("runs", {})
    for run_id, state in runs.items():
        _RUN_STATES[run_id] = RunState(
            run_id=run_id,
            status=state.get("status", "failed"),
            progress=int(state.get("progress", 0)),
            stage=state.get("stage", ""),
            created_at=state.get("created_at", utc_now_iso()),
            updated_at=state.get("updated_at", utc_now_iso()),
            logs_tail=list(state.get("logs_tail", [])),
            error=state.get("error"),
            artifact_root=state.get("artifact_root", str(get_run_dir(run_id))),
        )


def _persist_states_to_disk(extra: dict[str, Any] | None = None) -> None:
    """Persist all run states to disk registry."""
    runs: dict[str, Any] = {}
    for run_id, state in _RUN_STATES.items():
        runs[run_id] = asdict(state)
        if extra and run_id in extra:
            runs[run_id].update(extra[run_id])
    write_registry({"runs": runs})


def initialize_registry() -> None:
    """Initialize run registry cache."""
    with _LOCK:
        if not _RUN_STATES:
            _load_states_from_disk()


def create_run(
    *,
    run_id_scheme: str = DEFAULT_RUN_ID_SCHEME,
    timezone: str = DEFAULT_RUN_ID_TIMEZONE,
) -> RunState:
    """Create and persist a new queued run."""
    with _LOCK:
        initialize_registry()
        scheme = normalize_run_id_scheme(run_id_scheme)
        run_id = build_training_run_id(run_id_scheme=scheme, timezone=timezone)
        now = utc_now_iso()
        run_dir = get_run_dir(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        state = RunState(
            run_id=run_id,
            status="queued",
            progress=0,
            stage="queued",
            created_at=now,
            updated_at=now,
            logs_tail=["Run queued and registered."],
            error=None,
            artifact_root=str(run_dir),
        )
        _RUN_STATES[run_id] = state
        _persist_states_to_disk()
        return state


def append_log(run_id: str, message: str) -> None:
    """Append log line for a run."""
    with _LOCK:
        state = _RUN_STATES.get(run_id)
        if not state:
            return
        state.logs_tail.append(message)
        state.logs_tail = state.logs_tail[-MAX_LOG_LINES:]
        state.updated_at = utc_now_iso()
        _persist_states_to_disk()


def update_run(
    run_id: str,
    *,
    status: str | None = None,
    progress: int | None = None,
    stage: str | None = None,
    error: str | None = None,
) -> RunState | None:
    """Update run lifecycle fields."""
    with _LOCK:
        state = _RUN_STATES.get(run_id)
        if not state:
            return None
        if status is not None:
            state.status = status
        if progress is not None:
            state.progress = max(0, min(100, int(progress)))
        if stage is not None:
            state.stage = stage
        if error is not None:
            state.error = error
        state.updated_at = utc_now_iso()
        _persist_states_to_disk()
        return state


def get_run_state(run_id: str) -> RunState | None:
    """Return run state by id."""
    with _LOCK:
        initialize_registry()
        return _RUN_STATES.get(run_id)


def get_run_state_dict(run_id: str) -> dict[str, Any] | None:
    """Return run state as dictionary."""
    state = get_run_state(run_id)
    return asdict(state) if state else None
