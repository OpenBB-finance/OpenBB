"""CFTC COT Movers Model."""

from typing import Any

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_cftc.models.cot_index import (
    EXTREME_HIGH,
    EXTREME_LOW,
    GROUP_LABELS,
    HEDGE_HEATMAP,
    SCORE_HEATMAP,
    TRADER_GROUPS,
    CftcCotIndexFetcher,
    CftcCotIndexQueryParams,
)

DEFAULT_MOVERS = 8


class CftcCotMoversQueryParams(CftcCotIndexQueryParams):
    """CFTC COT Movers Query Parameters."""

    limit: int = Field(
        default=DEFAULT_MOVERS,
        description="Number of largest weekly score moves to return.",
    )


class CftcCotMoversData(Data):
    """CFTC COT Movers Data."""

    market: str = Field(
        description="Market whose score moved.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Market",
                "pinned": "left",
                "cellDataType": "text",
            }
        },
    )
    trader_group: str = Field(
        description="Trader group whose score moved.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Trader Group", "cellDataType": "text"}
        },
    )
    spec_score: float | None = Field(
        default=None,
        description="A speculator group's 0-100 score this week, shading green as they"
        + " crowd in.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Spec Score",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 1,
                **SCORE_HEATMAP,
            }
        },
    )
    commercial_score: float | None = Field(
        default=None,
        description="The commercials' 0-100 score this week, shading red as they hedge"
        + " up.",
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
    change: float | None = Field(
        default=None,
        description="Change in the score from the prior week.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "1w Change",
                "cellDataType": "number",
                "formatterFn": "none",
                "decimalPlaces": 0,
            }
        },
    )
    signal: str = Field(
        description="What the move did to that group's stance.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Signal",
                "cellDataType": "text",
                "width": 320,
            }
        },
    )


def describe_move(group: str, score: float, change: float) -> str:
    """Say in plain terms what a week's score move did to a group's stance."""
    hedging = group == "commercials"

    if score >= EXTREME_HIGH:
        if hedging:
            return "Moved to max hedged"

        return (
            "Pushed into one-year highs" if change > 0 else "Held near one-year highs"
        )

    if score <= EXTREME_LOW:
        if hedging:
            return "Moved to max exposed"

        return "Dropped to one-year lows" if change < 0 else "Held near one-year lows"

    if change > 0:
        return "Eased off max exposed" if hedging else "Lifted off one-year lows"

    return "Eased off max hedged" if hedging else "Pulled back from highs"


def mover_score(mover: dict) -> float:
    """Return whichever of a row's two score columns is filled in."""
    score = mover["spec_score"]

    return mover["commercial_score"] if score is None else score


def build_movers(rows: list[dict], limit: int) -> list[dict]:
    """Rank every group and market by the size of this week's score move."""
    movers: list[dict] = []

    for row in rows:
        for group in TRADER_GROUPS:
            score = row.get(group)
            change = row.get(f"{group}_change")

            if score is None or change is None:
                continue

            hedging = group == "commercials"
            movers.append(
                {
                    "market": row["market"],
                    "trader_group": GROUP_LABELS[group],
                    "spec_score": None if hedging else score,
                    "commercial_score": score if hedging else None,
                    "change": change,
                    "signal": describe_move(group, score, change),
                }
            )

    movers.sort(key=lambda m: (-abs(m["change"]), m["market"]))
    ranked: list[dict] = []
    seen: set[str] = set()

    for mover in movers:
        if mover["market"] in seen:
            continue

        seen.add(mover["market"])
        ranked.append(mover)

    return ranked[:limit] if limit > 0 else ranked


class CftcCotMoversFetcher(Fetcher[CftcCotMoversQueryParams, list[CftcCotMoversData]]):
    """CFTC COT Movers Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcCotMoversQueryParams:
        """Transform the query params."""
        return CftcCotMoversQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcCotMoversQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Score every market in the asset class."""
        return await CftcCotIndexFetcher.aextract_data(query, credentials)

    @staticmethod
    def transform_data(
        query: CftcCotMoversQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[CftcCotMoversData]]:
        """Rank the week's largest score moves and say what each one means."""
        movers = build_movers(data, query.limit)

        return AnnotatedResult(
            result=[CftcCotMoversData.model_validate(m) for m in movers],
            metadata={
                "report_date": data[0]["report_date"] if data else None,
                "lookback_weeks": query.lookback_weeks,
                "markets": len(data),
                "largest_move": movers[0]["change"] if movers else None,
                "extremes": sum(
                    1
                    for m in movers
                    if mover_score(m) >= EXTREME_HIGH or mover_score(m) <= EXTREME_LOW
                ),
            },
        )
