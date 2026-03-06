"""Macro router mounted under /quant_ml/macro and alias /macro."""

import asyncio
import json
from datetime import UTC, date, datetime
from typing import Any

from cachetools import TTLCache, cached
from fastapi.responses import StreamingResponse
from openbb_core.app.router import Router

from openbb_quant_ml.macro_models import (
    HmmRegimePayload,
    MacroAlertsResponse,
    MacroCatalogRegisterRequest,
    MacroCatalogResponse,
    MacroCatalogSearchRequest,
    MacroDerivedResponse,
    MacroDerivedSaveRequest,
    MacroExpressionRequest,
    MacroExpressionResponse,
    MacroHealthResponse,
    MacroPresetResponse,
    MacroRegimeResponse,
    MacroRegimeStateResponse,
    MacroSeriesMultiResponse,
    MacroSeriesQuery,
    MacroSeriesResponse,
    MacroUpdateRequest,
    MacroUpdateResponse,
    RegimeSchedulerStatusResponse,
    RegimeTransitionResponse,
)
from openbb_quant_ml.service.macro_regime import classify_regime_label
from openbb_quant_ml.service.macro_service import (
    evaluate_expression_response,
    get_alerts_response,
    get_catalog_response,
    get_copper_gold_preset_response,
    get_health_response,
    get_hmm_regime_response,
    get_regime_response,
    get_regime_scheduler_status_response,
    get_regime_state_response,
    get_regime_transitions_response,
    get_series_multi_response,
    get_series_response,
    list_derived_response,
    register_catalog_response,
    save_derived_response,
    search_catalog_response,
    trigger_regime_refresh_response,
    trigger_update_response,
)
from openbb_quant_ml.service.regime_scheduler import ensure_scheduler_started


def _build_macro_router(prefix: str, description: str) -> Router:
    router = Router(prefix=prefix, description=description)

    @router.command(methods=["GET"], path="/catalog")
    def catalog(domain: str | None = None) -> MacroCatalogResponse:
        """List registered macro series catalog."""
        return get_catalog_response(domain=domain)

    @router.command(methods=["GET"], path="/health")
    def health() -> MacroHealthResponse:
        """Return macro data freshness and coverage diagnostics."""
        return get_health_response()

    @router.command(methods=["POST"], path="/catalog/search")
    def catalog_search(request: MacroCatalogSearchRequest) -> MacroCatalogResponse:
        """Search FRED series catalog by keyword."""
        return search_catalog_response(query=request.q, domain=request.domain, limit=request.limit)

    @router.command(methods=["POST"], path="/catalog/register")
    def catalog_register(request: MacroCatalogRegisterRequest) -> MacroCatalogResponse:
        """Register one FRED series into local catalog."""
        return register_catalog_response(
            series_id=request.series_id,
            domain=request.domain,
            publish_lag=request.publish_lag,
            default_transform=request.default_transform,
        )

    @router.command(methods=["GET"], path="/series")
    def series(
        key: str | None = None,
        ids: str | None = None,
        start: date | None = None,
        end: date | None = None,
        transform: str = "level",
        freq: str = "native",
        fill: str = "ffill",
    ) -> MacroSeriesResponse | MacroSeriesMultiResponse:
        """Return one macro/market series with transform options."""
        if ids:
            requested = [item.strip() for item in ids.split(",") if item.strip()]
            return get_series_multi_response(requested, start=start, end=end, transform=transform, freq=freq, fill=fill)
        if not key:
            return MacroSeriesResponse(
                meta={"key": "", "source": "unknown", "transform": transform},
                data=[],
                stats={},
                status="insufficient_data",
                message="Either key or ids must be provided.",
            )
        query = MacroSeriesQuery(
            key=key,
            start=start,
            end=end,
            transform=transform,
            freq=freq,  # type: ignore[arg-type]
            fill=fill,  # type: ignore[arg-type]
        )
        return get_series_response(query)

    @router.command(methods=["POST"], path="/expression")
    def expression(request: MacroExpressionRequest) -> MacroExpressionResponse:
        """Evaluate custom expression over macro + market series."""
        return evaluate_expression_response(request)

    @router.command(methods=["GET"], path="/regime")
    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def regime(
        date: date | None = None,
        start: date | None = None,
        end: date | None = None,
        freq: str = "W",
        fill: str = "ffill",
    ) -> MacroRegimeResponse | MacroRegimeStateResponse:
        """Return 5-axis macro regime scores."""
        if date is not None and start is None and end is None:
            return get_regime_state_response(target_date=date)
        return get_regime_response(start=start, end=end, freq=freq, fill=fill)

    @router.command(methods=["GET"], path="/alerts")
    def alerts(start: date | None = None, end: date | None = None, limit: int = 200) -> MacroAlertsResponse:
        """Return current and historical macro alert events."""
        return get_alerts_response(start=start, end=end, history_limit=max(1, min(limit, 1000)))

    @router.command(methods=["GET"], path="/regime/transitions")
    def regime_transitions(
        start: date | None = None,
        end: date | None = None,
        threshold: float = 10.0,
    ) -> RegimeTransitionResponse:
        """Return macro regime transitions above threshold."""
        return get_regime_transitions_response(
            start=start,
            end=end,
            threshold=threshold,
            freq="W",
            fill="ffill",
        )

    @router.command(methods=["GET"], path="/regime/hmm")
    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def regime_hmm(
        start: date | None = None,
        end: date | None = None,
        n_states: int = 4,
    ) -> HmmRegimePayload:
        """Return HMM regime classification payload."""
        return get_hmm_regime_response(
            start=start,
            end=end,
            n_states=max(2, min(int(n_states), 8)),
            freq="W",
            fill="ffill",
        )

    @router.command(methods=["GET"], path="/regime/scheduler/status")
    def regime_scheduler_status() -> RegimeSchedulerStatusResponse:
        """Return regime scheduler status."""
        return get_regime_scheduler_status_response()

    @router.command(methods=["POST"], path="/regime/refresh")
    def regime_refresh() -> dict[str, str]:
        """Trigger immediate regime refresh."""
        return trigger_regime_refresh_response()

    @router.command(methods=["GET"], path="/regime/stream", response_model=None)
    async def regime_stream(interval_sec: int = 30) -> dict[str, Any]:
        """Stream regime score updates and label transitions as SSE."""
        ensure_scheduler_started()
        interval = max(10, min(int(interval_sec), 300))

        async def event_generator():
            prev_label: str | None = None
            while True:
                try:
                    regime = get_regime_response(freq="W", fill="ffill")
                    latest = regime.latest.model_dump() if regime.latest else {}
                    label = classify_regime_label(latest) if latest else None
                    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
                    payload = {
                        "event_type": "scores_update",
                        "timestamp": timestamp,
                        "data": latest,
                        "label": label,
                    }
                    if label and prev_label and label != prev_label:
                        transition = {
                            "event_type": "transition",
                            "timestamp": timestamp,
                            "data": {},
                            "from_label": prev_label,
                            "to_label": label,
                        }
                        yield f"event: transition\ndata: {json.dumps(transition, ensure_ascii=False)}\n\n"
                    yield f"event: scores_update\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    prev_label = label
                except Exception as exc:  # noqa: BLE001
                    error_payload = {
                        "event_type": "error",
                        "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                        "data": {"message": str(exc)},
                    }
                    yield f"event: error\ndata: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                await asyncio.sleep(interval)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @router.command(methods=["POST"], path="/derived/save")
    def derived_save(request: MacroDerivedSaveRequest) -> MacroDerivedResponse:
        """Save derived expression for reuse."""
        return save_derived_response(
            derived_id=request.derived_id,
            expression=request.expression,
            default_transform=request.default_transform,
        )

    @router.command(methods=["GET"], path="/derived")
    def derived_list() -> MacroDerivedResponse:
        """List saved derived expressions."""
        return list_derived_response()

    @router.command(methods=["POST"], path="/update")
    def update(request: MacroUpdateRequest) -> MacroUpdateResponse:
        """Trigger on-demand macro update."""
        return trigger_update_response(request)

    @router.command(methods=["GET"], path="/presets/copper_gold")
    def copper_gold_preset(
        start: date | None = None,
        end: date | None = None,
        freq: str = "W",
        fill: str = "ffill",
        scale: float = 1000.0,
        adjust_units: bool = True,
        yield_key: str = "FRED:DGS10",
        corr_window: int = 52,
        slope_window: int = 13,
        divergence_min_weeks: int = 4,
        include_corr: bool = True,
    ) -> MacroPresetResponse:
        """Return preset payload for copper/gold ratio versus 10Y yield."""
        return get_copper_gold_preset_response(
            start=start,
            end=end,
            freq=freq,
            fill=fill,
            scale=scale,
            adjust_units=adjust_units,
            yield_key=yield_key,
            corr_window=corr_window,
            slope_window=slope_window,
            divergence_min_weeks=divergence_min_weeks,
            include_corr=include_corr,
        )

    return router


router = _build_macro_router(prefix="/macro", description="Quant Macro analysis endpoints.")
alias_router = _build_macro_router(prefix="", description="Quant Macro alias endpoints.")
