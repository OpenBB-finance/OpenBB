"""In-memory and on-disk run status registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import time
from threading import RLock
from typing import Any

from openbb_quant_ml.service.constants import MAX_LOG_LINES
from openbb_quant_ml.service.run_id import (
    DEFAULT_RUN_ID_SCHEME,
    DEFAULT_RUN_ID_TIMEZONE,
    build_training_run_id,
    normalize_run_id_scheme,
)
from openbb_quant_ml.service.run_context import get_run_uid
from openbb_quant_ml.service.run_index import rebuild_runs_index, upsert_run_index_entry
from openbb_quant_ml.service.registry.audit_log import append_audit_event
from openbb_quant_ml.service.registry.migration_json_to_sqlite import (
    migrate_json_registry_to_sqlite,
)
from openbb_quant_ml.service.registry.run_registry_db import (
    ensure_registry_db,
    upsert_run_record,
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
    run_uid: str
    status: str
    progress: int
    stage: str
    created_at: str
    updated_at: str
    last_heartbeat_at: str
    logs_tail: list[str]
    error: str | None
    stale_reason: str | None
    artifact_root: str


_RUN_STATES: dict[str, RunState] = {}
_LOCK = RLock()
_DB_MIGRATED = False


def _sync_state_to_db(state: RunState) -> None:
    try:
        upsert_run_record(
            run_id=state.run_id,
            run_uid=state.run_uid,
            status=state.status,
            progress=state.progress,
            stage=state.stage,
            created_at_utc=state.created_at,
            updated_at_utc=state.updated_at,
            error=state.error,
            artifact_root=state.artifact_root,
        )
    except Exception:
        return


def _audit(
    run_id: str, *, event_type: str, payload: dict[str, Any], severity: str = "info"
) -> None:
    try:
        append_audit_event(
            run_id,
            event_type=event_type,
            severity=severity,
            payload=payload,
        )
    except Exception:
        return


def _state_from_payload(run_id: str, state: dict[str, Any]) -> RunState:
    now = utc_now_iso()
    run_dir = get_run_dir(run_id)
    run_uid = str(state.get("run_uid", "")).strip() or get_run_uid(run_dir, run_id)
    return RunState(
        run_id=run_id,
        run_uid=run_uid,
        status=str(state.get("status", "failed")),
        progress=int(state.get("progress", 0)),
        stage=str(state.get("stage", "")),
        created_at=str(state.get("created_at", now)),
        updated_at=str(state.get("updated_at", now)),
        last_heartbeat_at=str(
            state.get("last_heartbeat_at", state.get("updated_at", now))
        ),
        logs_tail=list(state.get("logs_tail", [])),
        error=state.get("error"),
        stale_reason=state.get("stale_reason"),
        artifact_root=str(state.get("artifact_root", str(get_run_dir(run_id)))),
    )


def _load_states_from_disk() -> None:
    """Hydrate in-memory state cache from disk registry."""
    payload = read_registry()
    runs = payload.get("runs", {})
    if not isinstance(runs, dict):
        return
    for run_id, state in runs.items():
        if not isinstance(state, dict):
            continue
        _RUN_STATES[str(run_id)] = _state_from_payload(str(run_id), state)


def _persist_run_state_to_disk(run_id: str, state: RunState, retries: int = 5) -> None:
    """Persist one run state with merge-write semantics."""
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            payload = read_registry()
            runs = payload.get("runs", {})
            if not isinstance(runs, dict):
                runs = {}
            existing = runs.get(run_id, {})
            merged = dict(existing) if isinstance(existing, dict) else {}
            merged.update(asdict(state))
            runs[run_id] = merged
            payload["runs"] = runs
            write_registry(payload)
            return
        except OSError as exc:
            last_exc = exc
            time.sleep(0.05 * attempt)
    if last_exc is not None:
        raise last_exc


def initialize_registry() -> None:
    """Initialize run registry cache."""
    global _DB_MIGRATED
    with _LOCK:
        if not _RUN_STATES:
            ensure_registry_db()
            if not _DB_MIGRATED:
                migrate_json_registry_to_sqlite()
                _DB_MIGRATED = True
            _load_states_from_disk()
            rebuild_runs_index()


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
        run_uid = get_run_uid(run_dir, run_id)
        state = RunState(
            run_id=run_id,
            run_uid=run_uid,
            status="queued",
            progress=0,
            stage="queued",
            created_at=now,
            updated_at=now,
            last_heartbeat_at=now,
            logs_tail=["Run queued and registered."],
            error=None,
            stale_reason=None,
            artifact_root=str(run_dir),
        )
        _RUN_STATES[run_id] = state
        _persist_run_state_to_disk(run_id, state)
        _sync_state_to_db(state)
        _audit(
            run_id,
            event_type="run_created",
            payload={"stage": state.stage, "status": state.status},
        )
        upsert_run_index_entry(
            run_id,
            status=state.status,
            stage=state.stage,
            created_at=state.created_at,
            updated_at=state.updated_at,
        )
        return state


def append_log(run_id: str, message: str) -> None:
    """Append log line for a run."""
    with _LOCK:
        state = _RUN_STATES.get(run_id)
        if not state:
            return
        state.logs_tail.append(message)
        state.logs_tail = state.logs_tail[-MAX_LOG_LINES:]
        now = utc_now_iso()
        state.updated_at = now
        state.last_heartbeat_at = now
        _persist_run_state_to_disk(run_id, state)
        _sync_state_to_db(state)
        _audit(
            run_id,
            event_type="run_log",
            payload={"message": message},
        )


def update_run(
    run_id: str,
    *,
    status: str | None = None,
    progress: int | None = None,
    stage: str | None = None,
    error: str | None = None,
    stale_reason: str | None = None,
) -> RunState | None:
    """Update run lifecycle fields."""
    with _LOCK:
        state = _RUN_STATES.get(run_id)
        if not state:
            return None
        previous_status = state.status
        if status is not None:
            state.status = status
        if progress is not None:
            state.progress = max(0, min(100, int(progress)))
        if stage is not None:
            state.stage = stage
        if error is not None:
            state.error = error
        if stale_reason is not None:
            state.stale_reason = stale_reason
        elif status is not None and status != "failed":
            state.stale_reason = None
        now = utc_now_iso()
        state.updated_at = now
        state.last_heartbeat_at = now
        _persist_run_state_to_disk(run_id, state)
        _sync_state_to_db(state)
        if previous_status != state.status or stage is not None or error is not None:
            _audit(
                run_id,
                event_type="run_status_update",
                severity="warning" if state.status == "failed" else "info",
                payload={
                    "status": state.status,
                    "stage": state.stage,
                    "progress": state.progress,
                    "error": state.error,
                    "stale_reason": state.stale_reason,
                },
            )
        upsert_run_index_entry(
            run_id,
            status=state.status,
            stage=state.stage,
            created_at=state.created_at,
            updated_at=state.updated_at,
        )
        return state


def heartbeat_run(
    run_id: str,
    *,
    stage: str | None = None,
    message: str | None = None,
) -> RunState | None:
    """Record heartbeat for long-running stages."""
    with _LOCK:
        state = _RUN_STATES.get(run_id)
        if not state:
            return None
        now = utc_now_iso()
        if stage is not None:
            state.stage = stage
        state.updated_at = now
        state.last_heartbeat_at = now
        if message:
            state.logs_tail.append(message)
            state.logs_tail = state.logs_tail[-MAX_LOG_LINES:]
        _persist_run_state_to_disk(run_id, state)
        _sync_state_to_db(state)
        upsert_run_index_entry(
            run_id,
            status=state.status,
            stage=state.stage,
            created_at=state.created_at,
            updated_at=state.updated_at,
        )
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
