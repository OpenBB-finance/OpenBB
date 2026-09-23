"""Federal Reserve / FFIEC E.16 Country Exposure Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveCountryExposureQueryParams(QueryParams):
    """FFIEC E.16 Country Exposure Query Parameters."""

    __json_schema_extra__ = {
        "group": {
            "x-widget_config": {
                "options": [
                    {"label": "All Banks", "value": "all_banks"},
                    {"label": "Large Financial Institutions (LFI)", "value": "lfi"},
                    {"label": "All Other Banks", "value": "all_others"},
                ]
            }
        },
        "table": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Table 1 — Ultimate-risk claims and off-balance-sheet exposures",
                        "value": "1",
                    },
                    {
                        "label": "Table 2 — Immediate-counterparty claims and risk transfers",
                        "value": "2",
                    },
                    {
                        "label": "Table 3 — Foreign-office liabilities",
                        "value": "3",
                    },
                    {
                        "label": "Table 4.1 — Claims by sector of obligor (ultimate risk)",
                        "value": "4.1",
                    },
                    {
                        "label": "Table 4.2 — Claims by sector of obligor (immediate counterparty)",
                        "value": "4.2",
                    },
                ]
            }
        },
    }

    date: dateType | None = Field(
        default=None,
        description="The report period end date; defaults to the latest release."
        " The survey is quarterly, available ~90 days after the reporting date.",
    )
    group: Literal["all_banks", "lfi", "all_others"] = Field(
        default="all_banks",
        description="The reporting group: all banks, large financial institutions"
        " (LFI), or all other banks.",
    )
    table: Literal["1", "2", "3", "4.1", "4.2"] = Field(
        default="1",
        description="The survey table: 1 (ultimate-risk claims + off-balance"
        " sheet), 2 (immediate-counterparty claims + risk transfers), 3 (foreign"
        " office liabilities), 4.1/4.2 (claims by sector of obligor).",
    )
    country: str | None = Field(
        default=None,
        description="Filter to a single country (case-insensitive).",
    )


class FederalReserveCountryExposureData(Data):
    """FFIEC E.16 Country Exposure Data."""

    date: dateType | None = Field(default=None, description="The report period.")
    group: str = Field(description="The reporting group.")
    table: str = Field(description="The survey table.")
    country_group: str | None = Field(
        default=None, description="The region the country is grouped under."
    )
    country: str = Field(description="The obligor country.")


class FederalReserveCountryExposureFetcher(
    Fetcher[
        FederalReserveCountryExposureQueryParams,
        list[FederalReserveCountryExposureData],
    ]
):
    """FFIEC E.16 Country Exposure Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveCountryExposureQueryParams:
        """Transform the query params."""
        return FederalReserveCountryExposureQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveCountryExposureQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the E.16 workbook and parse the requested group/table sheet."""
        from openbb_federal_reserve.utils.e16 import GROUPS, fetch_e16, parse_sheet

        content = fetch_e16(query.date)
        if not content[:2] == b"PK":
            raise EmptyDataError("The request was returned empty.")

        sheet = f"{GROUPS[query.group]} - Table {query.table}"
        rows, period = parse_sheet(content, sheet)
        if query.country:
            wanted = query.country.strip().lower()
            rows = [row for row in rows if row["country"].lower() == wanted]
        if not rows:
            raise EmptyDataError("The request was returned empty.")

        return [
            {"date": period, "group": query.group, "table": query.table, **row}
            for row in rows
        ]

    @staticmethod
    def transform_data(
        query: FederalReserveCountryExposureQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveCountryExposureData]:
        """Pivot the long rows to wide one-column-per-measure rows."""
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = pivot_wide(
            data,
            index=("date", "group", "table", "country_group", "country"),
            column="label",
            value="value",
        )
        return [
            FederalReserveCountryExposureData.model_validate(record)
            for record in records
        ]
