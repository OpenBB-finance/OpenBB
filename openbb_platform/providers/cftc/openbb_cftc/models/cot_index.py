"""CFTC COT Positioning Index Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

GROUP_LABELS: dict[str, str] = {
    "large_specs": "Large Specs",
    "small_specs": "Small Specs",
    "commercials": "Commercials",
}

TRADER_GROUPS: dict[str, tuple[str, str]] = {
    "large_specs": ("noncomm_positions_long_all", "noncomm_positions_short_all"),
    "small_specs": ("nonrept_positions_long_all", "nonrept_positions_short_all"),
    "commercials": ("comm_positions_long_all", "comm_positions_short_all"),
}

_SCORE_BANDS: tuple[tuple[int, int], ...] = (
    (-1, 15),
    (15, 35),
    (35, 65),
    (65, 85),
    (85, 101),
)

_RAMP: tuple[str, ...] = ("#b91c1c", "#ef8a80", "#d4d4d8", "#86efac", "#15803d")


def _color_rules(ramp: tuple[str, ...]) -> list[dict]:
    """Bind a five-step color ramp to the 0-100 score bands."""
    return [
        {
            "condition": "between",
            "range": {"min": low, "max": high},
            "color": color,
            "fill": True,
        }
        for (low, high), color in zip(_SCORE_BANDS, ramp, strict=True)
    ]


SCORE_RULES: list[dict] = _color_rules(_RAMP)

HEDGE_RULES: list[dict] = _color_rules(tuple(reversed(_RAMP)))

SCORE_HEATMAP: dict = {
    "renderFn": "columnColor",
    "renderFnParams": {"colorRules": SCORE_RULES},
}

HEDGE_HEATMAP: dict = {
    "renderFn": "columnColor",
    "renderFnParams": {"colorRules": HEDGE_RULES},
}

EXTREME_LOW = 15.0

EXTREME_HIGH = 85.0

_SPEC_ZONES = ("under-owned", "neutral", "crowded")

_COMMERCIAL_ZONES = ("exposed", "neutral", "heavily hedged")


def zone_for(score: float | None, group: str) -> str | None:
    """Return the band a score sits in, in that group's own vocabulary."""
    if score is None:
        return None

    zones = _COMMERCIAL_ZONES if group == "commercials" else _SPEC_ZONES

    if score <= EXTREME_LOW:
        return zones[0]

    if score >= EXTREME_HIGH:
        return zones[2]

    return zones[1]


def _exposure_score(score: float | None, group: str) -> float | None:
    """Put a group's score on the shared exposure scale, inverting the hedging side."""
    if score is None or group != "commercials":
        return score

    return round(100.0 - score, 1)


def positioning_score(nets: list[float]) -> float | None:
    """Return where the latest net position sits in its own range, from 0 to 100."""
    if not nets:
        return None

    low = min(nets)
    high = max(nets)

    if high == low:
        return 50.0

    return round(100.0 * (nets[-1] - low) / (high - low), 1)


def _number(value) -> float | None:
    """Coerce a reported figure to a number, or None when it is not one."""
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _net_series(rows: list[dict], group: str) -> list[float]:
    """Net position per report, oldest first, for one trader group."""
    long_field, short_field = TRADER_GROUPS[group]

    series: list[float] = []

    for row in rows:
        longs = _number(row.get(long_field))
        shorts = _number(row.get(short_field))

        if longs is not None and shorts is not None:
            series.append(longs - shorts)

    return series


class CftcCotIndexQueryParams(QueryParams):
    """CFTC COT Positioning Index Query Parameters."""

    __json_schema_extra__ = {
        "asset_class": {"multiple_items_allowed": False},
    }

    asset_class: Literal[
        "all",
        "indices_bonds",
        "currencies",
        "hard_commodities",
        "soft_commodities",
    ] = Field(
        default="all",
        description="Asset class of the curated markets to score.",
        json_schema_extra={
            "x-widget_config": {
                "options": [
                    {"label": label, "value": value}
                    for label, value in (
                        ("All", "all"),
                        ("Indices & Bonds", "indices_bonds"),
                        ("Currencies", "currencies"),
                        ("Hard Commodities", "hard_commodities"),
                        ("Soft Commodities", "soft_commodities"),
                    )
                ]
            }
        },
    )
    lookback_weeks: int = Field(
        default=52,
        description="Weeks of history the score ranks the latest net position within."
        + " 52 puts each reading in its own one-year range.",
    )
    futures_only: bool = Field(
        default=True,
        description="Score the futures-only report, the basis COT positioning work"
        + " conventionally uses. False scores the combined futures-and-options report,"
        + " whose larger open interest dilutes every net-to-open-interest share.",
    )
    use_cache: bool = Field(
        default=True,
        description="Cache each market's report history locally.",
    )


class CftcCotIndexData(Data):
    """CFTC COT Positioning Index Data."""

    report_date: dateType = Field(
        description="Date of the CFTC report the scores are taken from.",
        json_schema_extra={"x-widget_config": {"headerName": "Report Date"}},
    )
    market: str = Field(
        description="Curated market name.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Market", "cellDataType": "text"}
        },
    )
    open_interest: int | None = Field(
        default=None,
        description="Total open interest on the report date.",
        json_schema_extra={"x-widget_config": {"headerName": "Open Interest"}},
    )
    large_specs: float | None = Field(
        default=None,
        description="Large speculators' net position as a 0-100 score within its own"
        + " lookback range. 0 is the range low, 100 the range high.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Large Specs",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 1,
                **SCORE_HEATMAP,
            }
        },
    )
    large_specs_change: float | None = Field(
        default=None,
        description="Change in the large speculators' score since the prior report.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Large Δ1w",
                "cellDataType": "number",
                "decimalPlaces": 1,
            }
        },
    )
    large_specs_net_pct_oi: float | None = Field(
        default=None,
        description="Large speculators' net position as a percent of open interest.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Large Net/OI %",
                "cellDataType": "number",
                "decimalPlaces": 2,
            }
        },
    )
    large_specs_zone: str | None = Field(
        default=None,
        description="Band the large speculators' score sits in.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Large Zone", "cellDataType": "text"}
        },
    )
    small_specs: float | None = Field(
        default=None,
        description="Small speculators' net position as a 0-100 score within its own"
        + " lookback range.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Small Specs",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 1,
                **SCORE_HEATMAP,
            }
        },
    )
    small_specs_change: float | None = Field(
        default=None,
        description="Change in the small speculators' score since the prior report.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Small Δ1w",
                "cellDataType": "number",
                "decimalPlaces": 1,
            }
        },
    )
    small_specs_net_pct_oi: float | None = Field(
        default=None,
        description="Small speculators' net position as a percent of open interest.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Small Net/OI %",
                "cellDataType": "number",
                "decimalPlaces": 2,
            }
        },
    )
    small_specs_zone: str | None = Field(
        default=None,
        description="Band the small speculators' score sits in.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Small Zone", "cellDataType": "text"}
        },
    )
    commercials: float | None = Field(
        default=None,
        description="Commercials' net position as a 0-100 score within its own"
        + " lookback range. A high score is their least-hedged reading, not a bullish"
        + " one.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commercials",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 1,
                **HEDGE_HEATMAP,
            }
        },
    )
    commercials_change: float | None = Field(
        default=None,
        description="Change in the commercials' score since the prior report.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Comm Δ1w",
                "cellDataType": "number",
                "decimalPlaces": 1,
            }
        },
    )
    commercials_net_pct_oi: float | None = Field(
        default=None,
        description="Commercials' net position as a percent of open interest.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Comm Net/OI %",
                "cellDataType": "number",
                "decimalPlaces": 2,
            }
        },
    )
    commercials_zone: str | None = Field(
        default=None,
        description="Band the commercials' score sits in, in hedging terms.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Comm Zone", "cellDataType": "text"}
        },
    )


def is_extreme(row: dict) -> bool:
    """Whether any of a market's groups sits at or beyond the 15/85 bands."""
    scores = [row.get(group) for group in TRADER_GROUPS]

    return any(
        score is not None and (score <= EXTREME_LOW or score >= EXTREME_HIGH)
        for score in scores
    )


def score_market(market: dict, rows: list[dict], lookback_weeks: int) -> dict | None:
    """Score one market's trader groups against their own lookback range."""
    if not rows:
        return None

    ordered = sorted(rows, key=lambda r: r.get("report_date_as_yyyy_mm_dd") or "")
    window = ordered[-lookback_weeks:]
    prior_window = (
        ordered[-lookback_weeks - 1 : -1]
        if len(ordered) > lookback_weeks
        else ordered[:-1]
    )
    latest = window[-1]
    open_interest = _number(latest.get("open_interest_all"))
    scored: dict = {
        "report_date": (latest.get("report_date_as_yyyy_mm_dd") or "")[:10],
        "market": market["label"],
        "open_interest": int(open_interest) if open_interest is not None else None,
    }

    for group in TRADER_GROUPS:
        nets = _net_series(window, group)
        score = _exposure_score(positioning_score(nets), group)
        prior = _exposure_score(
            positioning_score(_net_series(prior_window, group)), group
        )
        scored[group] = score
        scored[f"{group}_change"] = (
            round(score - prior, 1) if score is not None and prior is not None else None
        )
        scored[f"{group}_net_pct_oi"] = (
            round(100.0 * nets[-1] / open_interest, 2)
            if nets and open_interest
            else None
        )
        scored[f"{group}_zone"] = zone_for(score, group)

    return scored


class CftcCotIndexFetcher(Fetcher[CftcCotIndexQueryParams, list[CftcCotIndexData]]):
    """CFTC COT Positioning Index Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcCotIndexQueryParams:
        """Transform the query params."""
        return CftcCotIndexQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcCotIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch each curated market's report history and score its trader groups."""
        import asyncio

        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_cftc.models.cot import CftcCotFetcher, CftcCotQueryParams
        from openbb_cftc.utils.cot_markets import markets_for

        markets = markets_for(query.asset_class)

        async def _one(market: dict) -> dict | None:
            cot_query = CftcCotQueryParams(
                code=market["code"],
                report_type="legacy",
                measure="positions",
                futures_only=query.futures_only,
                limit=query.lookback_weeks + 1,
            )

            try:
                rows = await CftcCotFetcher.aextract_data(cot_query, credentials)
            except (OpenBBError, EmptyDataError):
                return None

            return score_market(market, rows, query.lookback_weeks)

        scored = await asyncio.gather(*[_one(market) for market in markets])
        results = [row for row in scored if row]

        if not results:
            raise EmptyDataError(
                "No curated COT market returned a scoreable report history."
            )

        return results

    @staticmethod
    def transform_data(
        query: CftcCotIndexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[CftcCotIndexData]]:
        """Order the scored markets and summarize the week's largest moves."""
        from openbb_cftc.utils.cot_markets import COT_ASSET_CLASSES

        classes = {m["label"]: m["asset_class"] for m in _curated_order()}
        order = {m["label"]: n for n, m in enumerate(_curated_order())}
        rows = sorted(data, key=lambda r: order.get(r["market"], 0))
        movers: list[dict] = []

        for row in rows:
            for group in TRADER_GROUPS:
                change = row.get(f"{group}_change")

                if change is not None:
                    movers.append(
                        {
                            "market": row["market"],
                            "trader_group": group,
                            "score": row.get(group),
                            "change": change,
                        }
                    )

        movers.sort(key=lambda m: abs(m["change"]), reverse=True)

        return AnnotatedResult(
            result=[CftcCotIndexData.model_validate(r) for r in rows],
            metadata={
                "report_date": rows[0]["report_date"] if rows else None,
                "lookback_weeks": query.lookback_weeks,
                "asset_classes": {
                    key: COT_ASSET_CLASSES[key]
                    for key in dict.fromkeys(
                        classes[r["market"]] for r in rows if r["market"] in classes
                    )
                },
                "markets": len(rows),
                "extremes": sum(1 for r in rows if is_extreme(r)),
                "largest_changes": movers[:8],
            },
        )


def _curated_order() -> tuple:
    """Curated market order, so the table reads in its published grouping."""
    from openbb_cftc.utils.cot_markets import COT_MARKETS

    return COT_MARKETS
