"""Macro catalog services (defaults + search/register)."""

from __future__ import annotations

from datetime import date
from typing import Any

from openbb_quant_ml.service.macro_constants import load_macro_config
from openbb_quant_ml.service.macro_db import get_catalog_item, list_catalog, upsert_catalog_item
from openbb_quant_ml.service.macro_fred_client import FredApiKeyMissingError, FredClient, FredClientError
from openbb_quant_ml.service.macro_transforms import default_publish_lag_days


def _normalize_series_id(series_id: str) -> str:
    return str(series_id or "").strip().upper()


def _domain_defaults() -> list[dict[str, Any]]:
    cfg = load_macro_config()
    defaults: list[dict[str, Any]] = []
    for domain, detail in (cfg.get("domains") or {}).items():
        domain_cfg = detail or {}
        transform = str(domain_cfg.get("default_transform", "level"))
        lag_days = int(domain_cfg.get("default_publish_lag", 30))
        for series_id in domain_cfg.get("default_series", []) or []:
            sid = _normalize_series_id(str(series_id))
            if not sid:
                continue
            defaults.append(
                {
                    "id": f"FRED:{sid}",
                    "source": "FRED",
                    "series_id": sid,
                    "domain": str(domain),
                    "default_transform": transform,
                    "publish_lag": lag_days,
                }
            )
    return defaults


def bootstrap_default_catalog() -> list[dict[str, Any]]:
    """Ensure default catalog rows exist from config."""
    defaults = _domain_defaults()
    existing = {row["id"] for row in list_catalog(active_only=False)}
    inserted: list[dict[str, Any]] = []
    for row in defaults:
        if row["id"] in existing:
            continue
        upsert_catalog_item(row)
        inserted.append(row)
    return inserted


def list_catalog_items(domain: str | None = None) -> list[dict[str, Any]]:
    """List active catalog rows, bootstrapping defaults first."""
    bootstrap_default_catalog()
    return list_catalog(domain=domain, active_only=True)


def register_series(
    series_id: str,
    domain: str | None = None,
    publish_lag: int | None = None,
    default_transform: str | None = None,
) -> dict[str, Any]:
    """Register one FRED series in catalog with metadata autofill."""
    sid = _normalize_series_id(series_id)
    if not sid:
        raise ValueError("series_id is required")

    client = FredClient()
    meta: dict[str, Any] = {}
    try:
        meta = client.get_series_metadata(sid)
    except FredApiKeyMissingError as exc:
        # Allow registration without metadata if key is missing.
        meta = {"series_id": sid}
        if not get_catalog_item(sid):
            # keep fallback row with defaults
            pass
        else:
            raise ValueError("FRED_API_KEY is not configured. Metadata refresh unavailable.") from exc
    except FredClientError as exc:
        raise ValueError(str(exc)) from exc

    inferred_lag = default_publish_lag_days(str(meta.get("frequency") or ""))
    row = {
        "id": f"FRED:{sid}",
        "source": "FRED",
        "series_id": sid,
        "title": meta.get("title"),
        "frequency": meta.get("frequency"),
        "units": meta.get("units"),
        "domain": domain or "Custom",
        "default_transform": default_transform or "level",
        "publish_lag": int(publish_lag if publish_lag is not None else inferred_lag),
        "notes": meta.get("notes"),
        "active": True,
    }
    upsert_catalog_item(row)
    return row


def search_catalog(query: str, domain: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
    """Search remote FRED catalog by keyword."""
    q = str(query or "").strip()
    if not q:
        return []
    client = FredClient()
    rows = client.search_series(q, limit=limit)
    out: list[dict[str, Any]] = []
    for row in rows:
        series_id = _normalize_series_id(str(row.get("series_id", "")))
        if not series_id:
            continue
        out.append(
            {
                "id": f"FRED:{series_id}",
                "source": "FRED",
                "series_id": series_id,
                "title": row.get("title"),
                "frequency": row.get("frequency"),
                "units": row.get("units"),
                "domain": domain,
                "default_transform": "level",
                "publish_lag": default_publish_lag_days(str(row.get("frequency") or "")),
                "notes": row.get("notes"),
                "active": True,
            }
        )
    return out


def resolve_catalog_item(key: str, *, create_if_missing: bool = False) -> dict[str, Any] | None:
    """Resolve by full key (`FRED:UNRATE`) or raw id (`UNRATE`)."""
    key_norm = str(key or "").strip()
    if not key_norm:
        return None
    if key_norm.upper().startswith("FRED:"):
        sid = key_norm.split(":", 1)[1].strip().upper()
    else:
        sid = key_norm.upper()
    item = get_catalog_item(f"FRED:{sid}") or get_catalog_item(sid)
    if item:
        return item
    if not create_if_missing:
        return None
    # create lightweight default row when key is unknown
    fallback = {
        "id": f"FRED:{sid}",
        "source": "FRED",
        "series_id": sid,
        "title": sid,
        "frequency": None,
        "units": None,
        "domain": "Custom",
        "default_transform": "level",
        "publish_lag": default_publish_lag_days(None),
        "notes": None,
        "active": True,
    }
    upsert_catalog_item(fallback)
    return fallback


def all_default_series_ids() -> list[str]:
    """Return distinct default series ids from config."""
    ids: list[str] = []
    seen: set[str] = set()
    for row in _domain_defaults():
        sid = str(row["series_id"])
        if sid in seen:
            continue
        seen.add(sid)
        ids.append(sid)
    return ids


def parse_date_input(value: str | date | None) -> date | None:
    """Parse date-ish value for update helpers."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip().lower()
    if not text:
        return None
    if text == "today":
        return date.today()
    return date.fromisoformat(text)
