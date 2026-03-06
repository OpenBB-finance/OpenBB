"""Discovery and registry state for custom algorithms."""

from __future__ import annotations

import importlib
import pkgutil
from datetime import UTC, datetime
from typing import Any

from openbb_quant_ml.service.trading.config_manager import get_trading_config
from openbb_quant_ml.service.trading.custom_algorithm_adapter import (
    VALID_ALGORITHM_STATUSES,
    BaseCustomAlgorithm,
)
from openbb_quant_ml.service.trading.registry import (
    list_algorithm_records,
    upsert_algorithm_record,
)
from openbb_quant_ml.service.trading.storage import (
    algorithm_registry_path,
    load_runtime_json,
    save_runtime_json,
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _load_module_algorithms(module_name: str) -> list[BaseCustomAlgorithm]:
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return []
    rows: list[BaseCustomAlgorithm] = []
    explicit = getattr(module, "ALGORITHM", None)
    if isinstance(explicit, BaseCustomAlgorithm):
        rows.append(explicit)
    for value in module.__dict__.values():
        if isinstance(value, type) and issubclass(value, BaseCustomAlgorithm) and value is not BaseCustomAlgorithm:
            try:
                rows.append(value())
            except Exception:
                continue
    deduped: dict[tuple[str, str], BaseCustomAlgorithm] = {}
    for item in rows:
        deduped[(item.name, item.version)] = item
    return list(deduped.values())


def discover_custom_algorithms() -> list[BaseCustomAlgorithm]:
    """Discover in-repo custom algorithms from openbb_quant_ml.algorithms."""
    package_name = "openbb_quant_ml.algorithms"
    try:
        package = importlib.import_module(package_name)
    except Exception:
        return []
    discovered: list[BaseCustomAlgorithm] = []
    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.name.startswith("_"):
            continue
        discovered.extend(_load_module_algorithms(f"{package_name}.{module_info.name}"))
    deduped: dict[tuple[str, str], BaseCustomAlgorithm] = {}
    for item in discovered:
        deduped[(item.name, item.version)] = item
    return list(deduped.values())


def _load_registry_overrides() -> dict[str, Any]:
    payload = load_runtime_json(algorithm_registry_path(), default={"items": []})
    if not isinstance(payload, dict):
        return {"items": []}
    items = payload.get("items", [])
    return {"items": items if isinstance(items, list) else []}


def _save_registry_overrides(items: list[dict[str, Any]]) -> None:
    save_runtime_json(algorithm_registry_path(), {"items": items})


def sync_custom_algorithm_registry() -> list[dict[str, Any]]:
    """Sync discovered algorithms with persisted registry overrides."""
    config = get_trading_config()
    custom_cfg = config.get("custom_algorithms", {})
    default_status = str(custom_cfg.get("default_status", "sandbox") or "sandbox")
    if default_status not in VALID_ALGORITHM_STATUSES:
        default_status = "sandbox"
    discovered = discover_custom_algorithms()
    overrides = _load_registry_overrides().get("items", [])
    override_map = {
        (str(item.get("name")), str(item.get("version"))): item
        for item in overrides
        if isinstance(item, dict)
    }
    current_db = {
        (item["name"], item["version"]): item
        for item in list_algorithm_records()
    }
    merged: list[dict[str, Any]] = []
    for algorithm in discovered:
        key = (algorithm.name, algorithm.version)
        override = override_map.get(key, {})
        existing = current_db.get(key, {})
        status = str(override.get("status") or existing.get("status") or default_status)
        if status not in VALID_ALGORITHM_STATUSES:
            status = default_status
        row = {
            "name": algorithm.name,
            "version": algorithm.version,
            "description": algorithm.description,
            "required_columns": list(algorithm.required_columns),
            "parameters": dict(getattr(algorithm, "parameters", {}) or {}),
            "status": status,
            "active": bool(override.get("active", existing.get("active", status == "active"))),
            "sandbox_mode": bool(
                override.get("sandbox_mode", existing.get("sandbox_mode", status in {"sandbox", "validated"}))
            ),
            "signal_only": bool(
                override.get("signal_only", existing.get("signal_only", status in {"draft", "dev", "sandbox"}))
            ),
            "validation_result": existing.get("validation_result", {}),
            "recent_run_result": existing.get("recent_run_result", {}),
            "recent_error": existing.get("recent_error"),
            "performance_summary": existing.get("performance_summary", {}),
            "last_run_at": existing.get("last_run_at"),
            "created_at": existing.get("created_at") or _now_iso(),
            "modified_at": _now_iso(),
        }
        upsert_algorithm_record(row)
        merged.append(row)
    _save_registry_overrides(merged)
    return list_algorithm_records()


def update_algorithm_toggle(
    *,
    name: str,
    version: str | None = None,
    active: bool | None = None,
    sandbox_mode: bool | None = None,
    signal_only: bool | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Update persisted toggle state for one custom algorithm."""
    items = sync_custom_algorithm_registry()
    selected_version = version
    if not selected_version:
        versions = [item["version"] for item in items if item["name"] == name]
        if not versions:
            return items
        selected_version = sorted(versions)[-1]
    updated_items: list[dict[str, Any]] = []
    for item in items:
        row = dict(item)
        if row["name"] == name and row["version"] == selected_version:
            if active is not None:
                row["active"] = bool(active)
            if sandbox_mode is not None:
                row["sandbox_mode"] = bool(sandbox_mode)
            if signal_only is not None:
                row["signal_only"] = bool(signal_only)
            if status is not None and status in VALID_ALGORITHM_STATUSES:
                row["status"] = status
            row["modified_at"] = _now_iso()
            upsert_algorithm_record(row)
        updated_items.append(row)
    _save_registry_overrides(updated_items)
    return list_algorithm_records()
