"""Macro router mounted under /quant_ml/macro and alias /macro."""

from datetime import date

from openbb_core.app.router import Router

from openbb_quant_ml.macro_models import (
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
)
from openbb_quant_ml.service.macro_service import (
    evaluate_expression_response,
    get_alerts_response,
    get_catalog_response,
    get_copper_gold_preset_response,
    get_health_response,
    get_regime_response,
    get_regime_state_response,
    get_series_multi_response,
    get_series_response,
    list_derived_response,
    register_catalog_response,
    save_derived_response,
    search_catalog_response,
    trigger_update_response,
)


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
