"""ECB Economic Calendar Model (statistical release calendar).

The ECB calendar of statistical releases — when each dataset is next published.
Sourced by scraping the statscal page (see ``utils.non_sdmx``); mapped onto the
standard ``EconomicCalendar`` model.
"""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

# A few statscal "Dataset" labels are domain abbreviations that differ from the
# SDMX dataflow id the rest of the provider queries. Canonicalize them so the
# calendar's click-to-explore flow lands on a real dataflow. (Quarterly sector
# accounts — "QSA" — has no single ECB dataflow and is intentionally left as-is.)
_DATAFLOW_ALIASES = {"BPS": "BOP", "GFS": "GST", "RAS": "RA"}


class ECBEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """ECB Economic Calendar Query."""

    dataflow: str | None = Field(
        default=None,
        exclude=True,
        description="Dummy field so a clicked release can group by dataflow.",
    )


class ECBEconomicCalendarData(EconomicCalendarData):
    """ECB Economic Calendar Data."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            # The ``category`` cell holds the dataflow id (e.g. ``BSI``); clicking
            # it sets the shared ``dataflow`` parameter, so the dataflow-dimensions
            # and series-builder widgets explore that release's data. The calendar
            # is the dashboard's entry point.
            "category": {
                "x-widget_config": {
                    "headerName": "Dataset",
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        "actionType": "groupBy",
                        "groupByParamName": "dataflow",
                    },
                }
            }
        },
    )


class ECBEconomicCalendarFetcher(
    Fetcher[ECBEconomicCalendarQueryParams, list[ECBEconomicCalendarData]]
):
    """Fetch the ECB statistical release calendar."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBEconomicCalendarQueryParams:
        """Transform query."""
        return ECBEconomicCalendarQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBEconomicCalendarQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Scrape the raw release-calendar rows."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.non_sdmx import fetch_release_calendar

        async def loader() -> list[dict]:
            return await fetch_release_calendar()

        return await cached_records("calendar", make_key("calendar"), loader)

    @staticmethod
    def transform_data(
        query: ECBEconomicCalendarQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBEconomicCalendarData]:
        """Filter by date range, sort, and validate."""
        start = query.start_date.isoformat() if query.start_date else None
        end = query.end_date.isoformat() if query.end_date else None
        filtered = [
            row
            for row in data
            if (not start or row["date"][:10] >= start)
            and (not end or row["date"][:10] <= end)
        ]
        if not filtered:
            raise EmptyDataError("No ECB calendar releases found for the query.")
        filtered.sort(key=lambda r: r["date"])
        return [
            ECBEconomicCalendarData.model_validate(
                {
                    **d,
                    "category": _DATAFLOW_ALIASES.get(
                        d.get("category", ""), d.get("category")
                    ),
                }
            )
            for d in filtered
        ]
