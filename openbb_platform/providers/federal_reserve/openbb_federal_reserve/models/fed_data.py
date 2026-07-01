"""Federal Reserve Data Download Program (DDP) Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field


class FederalReserveDataDownloadQueryParams(QueryParams):
    """Federal Reserve Data Download (DDP) Query Parameters."""

    __json_schema_extra__ = {
        "dataset": {
            "x-widget_config": {
                "options": [
                    {"label": "H.6 — Money Stock Measures", "value": "H.6"},
                    {
                        "label": "H.8 — Assets and Liabilities of Commercial Banks",
                        "value": "H.8",
                    },
                    {"label": "H.10 — Foreign Exchange Rates", "value": "H.10"},
                    {"label": "H.15 — Selected Interest Rates", "value": "H.15"},
                    {
                        "label": "H.4.1 — Factors Affecting Reserve Balances",
                        "value": "H.4.1",
                    },
                    {
                        "label": "G.17 — Industrial Production and Capacity Utilization",
                        "value": "G.17",
                    },
                    {"label": "G.19 — Consumer Credit", "value": "G.19"},
                    {"label": "G.20 — Finance Companies", "value": "G.20"},
                    {
                        "label": "Z.1 — Financial Accounts of the United States",
                        "value": "Z.1",
                    },
                    {"label": "CP — Commercial Paper", "value": "CP"},
                    {
                        "label": "CHGDEL — Charge-off and Delinquency Rates",
                        "value": "CHGDEL",
                    },
                    {
                        "label": "DSR — Household Debt Service and Financial Obligations Ratios",
                        "value": "DSR",
                    },
                    {
                        "label": "SLOOS — Senior Loan Officer Opinion Survey",
                        "value": "SLOOS",
                    },
                    {
                        "label": "SCOOS — Senior Credit Officer Opinion Survey",
                        "value": "SCOOS",
                    },
                ]
            }
        }
    }

    dataset: Literal[
        "H.6",
        "H.8",
        "H.10",
        "H.15",
        "H.4.1",
        "G.17",
        "G.19",
        "G.20",
        "Z.1",
        "CP",
        "CHGDEL",
        "DSR",
        "SLOOS",
        "SCOOS",
    ] = Field(
        description="The Federal Reserve statistical release to download.",
    )
    table: str | None = Field(
        default=None,
        description="The data table within the release (see `list_datasets`);"
        " defaults to the release's first table.",
    )
    series: str | None = Field(
        default=None,
        description="Optional comma-separated series IDs to filter the table to.",
    )
    seasonally_adjusted: bool | None = Field(
        default=None,
        description="Filter to seasonally adjusted (True) or not seasonally"
        " adjusted (False) series; defaults to both, where applicable.",
    )
    limit: int | None = Field(
        default=1,
        ge=0,
        description="Return only the most recent N observations per series; the"
        " default is the latest observation. Set to 0 or None for the full series."
        " When the full series is already cached, it is sliced from the cache.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class FederalReserveDataDownloadData(Data):
    """Federal Reserve Data Download (DDP) Data."""

    model_config = ConfigDict(extra="allow")

    date: dateType = Field(description="The observation date.")
    series_id: str = Field(description="The DDP series identifier.")
    value: float | None = Field(default=None, description="The observation value.")
    title: str | None = Field(
        default=None, description="Human-readable series description."
    )
    unit: str | None = Field(
        default=None,
        description="The unit of the value, including scale, e.g. 'Millions of"
        " Dollars' or 'Percent: Per Year'. Values are published as-is, not rescaled.",
    )
    unit_multiplier: str | None = Field(
        default=None,
        description="The scale word applied to the value, e.g. 'Millions',"
        " 'Billions', or 'Trillions'; None when the value carries no scale.",
    )
    seasonally_adjusted: bool | None = Field(
        default=None,
        description="Whether the series is seasonally adjusted, where applicable.",
    )


class FederalReserveDataDownloadFetcher(
    Fetcher[
        FederalReserveDataDownloadQueryParams,
        list[FederalReserveDataDownloadData],
    ]
):
    """Federal Reserve Data Download Program Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDataDownloadQueryParams:
        """Transform the query params."""
        return FederalReserveDataDownloadQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDataDownloadQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch and parse the DDP package, applying the optional series filter."""
        from openbb_federal_reserve.utils.ddp import fetch_dataset, resolve_dataset

        try:
            release, package = resolve_dataset(query.dataset, query.table)
        except ValueError as exc:
            raise OpenBBError(exc) from exc

        # A selected series takes priority over the table snapshot: its full
        # history is fetched (ignoring ``limit``) within the date range, then
        # filtered to the requested series.
        rows = fetch_dataset(
            release,
            package,
            query.start_date.isoformat() if query.start_date else None,
            query.end_date.isoformat() if query.end_date else None,
            None if query.series else query.limit,
        )

        if query.series:
            wanted = {s.strip() for s in query.series.split(",") if s.strip()}
            rows = [row for row in rows if row.get("series_id") in wanted]

        if query.seasonally_adjusted is not None:
            rows = [
                row
                for row in rows
                if row.get("seasonally_adjusted") == query.seasonally_adjusted
            ]

        if not rows:
            raise EmptyDataError("The request was returned empty.")

        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveDataDownloadQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDataDownloadData]:
        """Validate the rows into the data model, sorted by date and series."""
        return [
            FederalReserveDataDownloadData.model_validate(row)
            for row in sorted(
                data, key=lambda r: (str(r.get("date")), str(r.get("series_id")))
            )
        ]
