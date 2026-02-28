"""Provider utility endpoints (raw query + catalogs).

These endpoints are intended for advanced usage where the OpenBB standardized
models do not cover a provider's full surface area.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal

from fastapi import APIRouter
from openbb_core.api.provider_strategy import (
    compute_confidence,
    normalize_provider,
    resolve_provider_strategy,
)
from openbb_core.provider.utils.errors import OpenBBError
from pydantic import BaseModel, Field

router = APIRouter(prefix="/provider", tags=["Provider"])


def _load_user_credentials() -> dict[str, str]:
    """Load credentials from ~/.openbb_platform/user_settings.json (best-effort)."""
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE") or ""
    p = Path(home) / ".openbb_platform" / "user_settings.json"
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    creds = data.get("credentials", {}) if isinstance(data, dict) else {}
    return creds if isinstance(creds, dict) else {}


class ProviderQueryRequest(BaseModel):
    provider: Literal["tushare", "wind", "auto"] = Field(
        description="Provider name. Use 'auto' to enable server-side fallback."
    )
    method: str = Field(
        description=(
            "Provider native method/API name. "
            "For tushare: api_name for pro.query (e.g., 'daily', 'income'). "
            "For wind: WindPy method name (e.g., 'wsd', 'wss', 'wsi', 'wset', 'edb')."
        )
    )
    args: list[Any] = Field(default_factory=list, description="Positional args.")
    kwargs: dict[str, Any] = Field(default_factory=dict, description="Keyword args.")


class ProviderQueryResponse(BaseModel):
    provider: str
    method: str
    data: Any
    meta: dict[str, Any]


class ProviderCatalogResponse(BaseModel):
    provider: str
    catalog: dict[str, Any]
    meta: dict[str, Any]


def _query_tushare(method: str, kwargs: dict[str, Any]) -> Any:
    from openbb_tushare.utils.helpers import get_pro

    creds = _load_user_credentials()
    token = creds.get("tushare_api_key")
    if not token:
        raise OpenBBError("Missing credential: tushare_api_key")
    pro = get_pro(token)
    try:
        df = pro.query(method, **(kwargs or {}))
    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(f"Tushare query failed: {e}") from e
    return [] if df is None else df.to_dict("records")


def _query_wind(method: str, args: list[Any], kwargs: dict[str, Any]) -> Any:
    from openbb_wind.utils.wind_client import get_wind_client

    client = get_wind_client()
    resp = client.raw(method=method, args=args, kwargs=kwargs)
    return resp.__dict__


def _compute_confidence(fallback_trace: list[dict[str, Any]]) -> float:
    provider_used = next(
        (
            item.get("provider")
            for item in reversed(fallback_trace)
            if item.get("status") == "success"
        ),
        None,
    )
    return compute_confidence(provider_used, fallback_trace)


def _resolve_query_strategy(req: ProviderQueryRequest) -> dict[str, Any]:
    credentials = _load_user_credentials()
    return resolve_provider_strategy(
        route="/provider/query",
        requested_provider=req.provider,
        command_coverage={"/provider/query": ["wind", "tushare"]},
        provider_credentials={"wind": [], "tushare": ["tushare_api_key"]},
        credentials_obj=SimpleNamespace(**credentials),
    )


def _run_query_with_fallback(
    req: ProviderQueryRequest, candidates: list[str]
) -> tuple[str, Any, list[dict]]:
    if not candidates:
        raise OpenBBError("Provider query failed: no candidate provider available.")

    last_error: Exception | None = None
    fallback_trace: list[dict[str, Any]] = []
    for attempt, candidate in enumerate(candidates, start=1):
        try:
            if candidate == "tushare":
                data = _query_tushare(req.method, req.kwargs)
            elif candidate == "wind":
                data = _query_wind(req.method, req.args, req.kwargs)
            else:
                raise OpenBBError(f"Unsupported provider: {candidate}")

            fallback_trace.append(
                {"attempt": attempt, "provider": candidate, "status": "success"}
            )
            return candidate, data, fallback_trace
        except Exception as exc:  # pylint: disable=broad-exception-caught
            fallback_trace.append(
                {
                    "attempt": attempt,
                    "provider": candidate,
                    "status": "failed",
                    "error": str(exc)[:500],
                }
            )
            last_error = exc

    if last_error:
        raise OpenBBError(f"Provider query failed after fallback: {last_error}")
    raise OpenBBError("Provider query failed: no candidate provider available.")

@router.post(
    "/query",
    openapi_extra={
        "mcp_config": {
            "expose": True,
            "mcp_type": "tool",
            "methods": ["POST"],
            "prompts": [
                {
                    "name": "provider_raw_query",
                    "description": "Call a provider's native API (advanced).",
                    "content": "Call provider native method via POST /provider/query with provider={{provider}}, method={{method}} and args/kwargs.",
                }
            ],
        }
    },
)
def provider_query(req: ProviderQueryRequest) -> ProviderQueryResponse:
    """Raw provider query (advanced).

    - `provider=tushare`: calls `pro.query(api_name=req.method, **req.kwargs)` (args ignored)
    - `provider=wind`: calls WindPy via local install or HTTP gateway (args + kwargs)
    """
    strategy = _resolve_query_strategy(req)
    provider_candidates = strategy.get("candidates", [])
    selection_reason = strategy.get("selection_reason", {})
    provider_used, data, fallback_trace = _run_query_with_fallback(req, provider_candidates)
    if isinstance(selection_reason, dict):
        selection_reason = {
            **selection_reason,
            "selected_provider": provider_used,
        }
    return ProviderQueryResponse(
        provider=provider_used,
        method=req.method,
        data=data,
        meta={
            "route": "/provider/query",
            "provider_requested": normalize_provider(req.provider),
            "provider_used": provider_used,
            "provider_candidates": provider_candidates,
            "fallback_trace": fallback_trace,
            "confidence": _compute_confidence(fallback_trace),
            "selection_reason": selection_reason,
        },
    )


@router.get(
    "/catalog",
    openapi_extra={
        "mcp_config": {
            "expose": True,
            "mcp_type": "tool",
            "methods": ["GET"],
            "prompts": [
                {
                    "name": "provider_catalog",
                    "description": "Get provider native catalog/classifications (advanced).",
                    "content": "Fetch /provider/catalog?provider={{provider}} to discover categories and supported native methods.",
                }
            ],
        }
    },
)
def provider_catalog(provider: Literal["tushare", "wind"]) -> ProviderCatalogResponse:
    """Get provider catalogs / classifications (best-effort)."""
    if provider == "tushare":
        try:
            from openbb_tushare.utils.catalog import load_tushare_catalog
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(f"Tushare catalog unavailable: {e}") from e
        return ProviderCatalogResponse(
            provider="tushare",
            catalog=load_tushare_catalog(),
            meta={
                "route": "/provider/catalog",
                "provider_requested": "tushare",
                "provider_used": "tushare",
                "provider_candidates": ["tushare"],
                "fallback_trace": [
                    {"attempt": 1, "provider": "tushare", "status": "success"}
                ],
                "confidence": 0.95,
                "selection_reason": {
                    "mode": "explicit",
                    "route": "/provider/catalog",
                    "requested_provider": "tushare",
                    "selected_provider": "tushare",
                },
            },
        )

    if provider == "wind":
        # WindPy does not publish a full machine-readable catalog; provide a practical method list.
        catalog = {
            "backend": "windpy (local) or http-gateway",
            "env": {
                "OPENBB_WIND_GATEWAY_URL": "If set, OpenBB will call this gateway instead of local WindPy.",
            },
            "methods": [
                {"name": "wsd", "desc": "Time series data (daily/periodic)."},
                {"name": "wsi", "desc": "Intraday time series."},
                {"name": "wss", "desc": "Snapshot / cross-sectional data."},
                {"name": "wset", "desc": "Table datasets."},
                {"name": "edb", "desc": "Macro/economic database series."},
            ],
            "note": "For detailed field lists and dataset names, refer to Wind terminal documentation.",
        }
        return ProviderCatalogResponse(
            provider="wind",
            catalog=catalog,
            meta={
                "route": "/provider/catalog",
                "provider_requested": "wind",
                "provider_used": "wind",
                "provider_candidates": ["wind"],
                "fallback_trace": [
                    {"attempt": 1, "provider": "wind", "status": "success"}
                ],
                "confidence": 0.95,
                "selection_reason": {
                    "mode": "explicit",
                    "route": "/provider/catalog",
                    "requested_provider": "wind",
                    "selected_provider": "wind",
                },
            },
        )

    raise OpenBBError(f"Unsupported provider: {provider}")
