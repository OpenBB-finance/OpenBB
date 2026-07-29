"""CFTC COT Positioning History Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_cftc.models.cot_index import (
    EXTREME_HIGH,
    EXTREME_LOW,
    HEDGE_HEATMAP,
    SCORE_HEATMAP,
    TRADER_GROUPS,
    _exposure_score,
    _number,
    positioning_score,
    zone_for,
)

REPORTS_PER_MONTH = 4

api_prefix = SystemService().system_settings.api_settings.prefix


class CftcCotPositioningQueryParams(QueryParams):
    """CFTC COT Positioning History Query Parameters."""

    __json_schema_extra__ = {
        "code": {
            "multiple_items_allowed": False,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/cftc/cot_choices",
                "style": {"popupWidth": 650},
            },
        },
    }

    code: str = Field(
        default="CFTC_13874+",
        description="CFTC contract market code to score, as printed on the search table.",
    )
    lookback_weeks: int = Field(
        default=52,
        description="Weeks each week's score ranks its net position within.",
    )
    futures_only: bool = Field(
        default=True,
        description="Score the futures-only report, the basis COT positioning work"
        + " conventionally uses. False scores the combined futures-and-options report,"
        + " whose larger open interest dilutes every net-to-open-interest share.",
    )


class CftcCotPositioningData(Data):
    """CFTC COT Positioning History Data."""

    report_date: dateType = Field(
        description="Date of the CFTC report.",
        json_schema_extra={"x-widget_config": {"headerName": "Report Date"}},
    )
    open_interest: int | None = Field(
        default=None,
        description="Total open interest on the report date.",
        json_schema_extra={"x-widget_config": {"headerName": "Open Interest"}},
    )
    large_specs_net: int | None = Field(
        default=None,
        description="Large speculators' net position, in contracts.",
        json_schema_extra={"x-widget_config": {"headerName": "Large Net"}},
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
    large_specs_score: float | None = Field(
        default=None,
        description="Large speculators' 0-100 score within the trailing window.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Large Score",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 1,
                **SCORE_HEATMAP,
            }
        },
    )
    small_specs_net: int | None = Field(
        default=None,
        description="Small speculators' net position, in contracts.",
        json_schema_extra={"x-widget_config": {"headerName": "Small Net"}},
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
    small_specs_score: float | None = Field(
        default=None,
        description="Small speculators' 0-100 score within the trailing window.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Small Score",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 1,
                **SCORE_HEATMAP,
            }
        },
    )
    commercials_net: int | None = Field(
        default=None,
        description="Commercials' net position, in contracts.",
        json_schema_extra={"x-widget_config": {"headerName": "Comm Net"}},
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
    commercials_score: float | None = Field(
        default=None,
        description="Commercials' 0-100 score within the trailing window, on the same"
        + " exposure scale as the specs. A high score is their most-hedged reading.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Comm Score",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 1,
                **HEDGE_HEATMAP,
            }
        },
    )


def _rolling_scores(
    nets: list[float | None], lookback_weeks: int, group: str
) -> list[float | None]:
    """Score each week's net position against its own trailing window."""
    scores: list[float | None] = []

    for index in range(len(nets)):
        window = [
            value
            for value in nets[max(0, index - lookback_weeks + 1) : index + 1]
            if value is not None
        ]
        scores.append(
            _exposure_score(positioning_score(window), group) if window else None
        )

    return scores


def build_series(rows: list[dict], lookback_weeks: int) -> list[dict]:
    """Build the weekly positioning series, oldest first."""
    ordered = sorted(rows, key=lambda r: r.get("report_date_as_yyyy_mm_dd") or "")
    dates = [(r.get("report_date_as_yyyy_mm_dd") or "")[:10] for r in ordered]
    interest = [_number(r.get("open_interest_all")) for r in ordered]
    series: dict[str, list] = {}

    for group, (long_field, short_field) in TRADER_GROUPS.items():
        nets: list[float | None] = []

        for row in ordered:
            longs = _number(row.get(long_field))
            shorts = _number(row.get(short_field))
            nets.append(None if longs is None or shorts is None else longs - shorts)

        series[group] = nets
        series[f"{group}_score"] = _rolling_scores(nets, lookback_weeks, group)

    built: list[dict] = []

    for index, report_date in enumerate(dates):
        if not report_date:
            continue

        open_interest = interest[index]
        row: dict = {
            "report_date": report_date,
            "open_interest": int(open_interest) if open_interest else None,
        }

        for group in TRADER_GROUPS:
            net = series[group][index]
            row[f"{group}_net"] = int(net) if net is not None else None
            row[f"{group}_net_pct_oi"] = (
                round(100.0 * net / open_interest, 2)
                if net is not None and open_interest
                else None
            )
            row[f"{group}_score"] = series[f"{group}_score"][index]

        built.append(row)

    return built


def readout(series: list[dict], group: str) -> dict:
    """Summarize a group's latest reading against the window on show."""
    scores = [r[f"{group}_score"] for r in series if r[f"{group}_score"] is not None]
    pcts = [
        r[f"{group}_net_pct_oi"] for r in series if r[f"{group}_net_pct_oi"] is not None
    ]
    latest = series[-1] if series else {}
    score = latest.get(f"{group}_score")
    prior = series[-2][f"{group}_score"] if len(series) > 1 else None
    month = (
        series[-1 - REPORTS_PER_MONTH][f"{group}_score"]
        if len(series) > REPORTS_PER_MONTH
        else None
    )

    return {
        "score": score,
        "zone": zone_for(score, group),
        "is_extreme": score is not None
        and (score <= EXTREME_LOW or score >= EXTREME_HIGH),
        "net": latest.get(f"{group}_net"),
        "net_pct_oi": latest.get(f"{group}_net_pct_oi"),
        "change_1w": (
            round(score - prior, 1) if score is not None and prior is not None else None
        ),
        "change_1m": (
            round(score - month, 1) if score is not None and month is not None else None
        ),
        "score_low": min(scores) if scores else None,
        "score_high": max(scores) if scores else None,
        "net_pct_oi_low": min(pcts) if pcts else None,
        "net_pct_oi_high": max(pcts) if pcts else None,
    }


class CftcCotPositioningFetcher(
    Fetcher[CftcCotPositioningQueryParams, list[CftcCotPositioningData]]
):
    """CFTC COT Positioning History Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcCotPositioningQueryParams:
        """Transform the query params."""
        return CftcCotPositioningQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcCotPositioningQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> tuple[dict, list[dict]]:
        """Fetch one curated market's full report history."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_cftc.models.cot import CftcCotFetcher, CftcCotQueryParams
        from openbb_cftc.utils.cot_markets import market_for_code

        market = market_for_code(query.code)
        rows = await CftcCotFetcher.aextract_data(
            CftcCotQueryParams(
                code=market["code"],
                report_type="legacy",
                measure="positions",
                futures_only=query.futures_only,
            ),
            credentials,
        )

        if rows and market["label"] == market["code"]:
            named = rows[0].get("contract_market_name") or rows[0].get(
                "market_and_exchange_names"
            )

            if named:
                market = {**market, "label": named.strip(), "contract": named.strip()}

        if not rows:
            raise EmptyDataError(
                f"No CFTC report history was returned for {market['label']}."
            )

        return market, rows

    @staticmethod
    def transform_data(
        query: CftcCotPositioningQueryParams,
        data: tuple[dict, list[dict]],
        **kwargs: Any,
    ) -> AnnotatedResult[list[CftcCotPositioningData]]:
        """Score the history week by week and summarize the latest reading."""
        market, rows = data
        series = build_series(rows, query.lookback_weeks)

        return AnnotatedResult(
            result=[CftcCotPositioningData.model_validate(r) for r in series],
            metadata={
                "market": market["label"],
                "contract": market["contract"],
                "asset_class": market["asset_class"],
                "lookback_weeks": query.lookback_weeks,
                "weeks": len(series),
                "report_date": series[-1]["report_date"] if series else None,
                "window_start": series[0]["report_date"] if series else None,
                **{group: readout(series, group) for group in TRADER_GROUPS},
            },
        )
