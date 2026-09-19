"""Federal Reserve Bank of Kansas City Archived Ag Finance Databook Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.kansascityfed.org/documents/7273"
    "/Ag_Finance_Databook_Archived_-_Historical_Data.xlsx"
)

_TABLES = (
    [f"afdr_a{index}" for index in range(1, 15)]
    + [f"afdr_b{index}" for index in range(1, 10)]
    + [f"afdr_c{index}" for index in range(1, 8)]
)
_TABLE_KEYS = tuple(_TABLES)


class FederalReserveKansasCityAgDatabookArchivedQueryParams(QueryParams):
    """Kansas City Fed Archived Ag Finance Databook Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Table A.1", "value": "afdr_a1"},
                    {"label": "Table A.2", "value": "afdr_a2"},
                    {"label": "Table A.3", "value": "afdr_a3"},
                    {"label": "Table A.4", "value": "afdr_a4"},
                    {"label": "Table A.5", "value": "afdr_a5"},
                    {"label": "Table A.6", "value": "afdr_a6"},
                    {"label": "Table A.7", "value": "afdr_a7"},
                    {"label": "Table A.8", "value": "afdr_a8"},
                    {"label": "Table A.9", "value": "afdr_a9"},
                    {"label": "Table A.10", "value": "afdr_a10"},
                    {"label": "Table A.11", "value": "afdr_a11"},
                    {"label": "Table A.12", "value": "afdr_a12"},
                    {"label": "Table A.13", "value": "afdr_a13"},
                    {"label": "Table A.14", "value": "afdr_a14"},
                    {"label": "Table B.1", "value": "afdr_b1"},
                    {"label": "Table B.2", "value": "afdr_b2"},
                    {"label": "Table B.3", "value": "afdr_b3"},
                    {"label": "Table B.4", "value": "afdr_b4"},
                    {"label": "Table B.5", "value": "afdr_b5"},
                    {"label": "Table B.6", "value": "afdr_b6"},
                    {"label": "Table B.7", "value": "afdr_b7"},
                    {"label": "Table B.8", "value": "afdr_b8"},
                    {"label": "Table B.9", "value": "afdr_b9"},
                    {"label": "Table C.1", "value": "afdr_c1"},
                    {"label": "Table C.2", "value": "afdr_c2"},
                    {"label": "Table C.3", "value": "afdr_c3"},
                    {"label": "Table C.4", "value": "afdr_c4"},
                    {"label": "Table C.5", "value": "afdr_c5"},
                    {"label": "Table C.6", "value": "afdr_c6"},
                    {"label": "Table C.7", "value": "afdr_c7"},
                ]
            }
        }
    }

    table: Literal[_TABLE_KEYS] = Field(  # ty: ignore[invalid-type-form]
        default="afdr_a1",
        description="The archived databook table. Section A tables cover farm debt"
        " outstanding, section B interest rates and terms, and section C the"
        " condition of agricultural banks.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveKansasCityAgDatabookArchivedData(Data):
    """Kansas City Fed Archived Ag Finance Databook Data."""

    date: dateType = Field(description="The observation period-end date.")
    frequency: str = Field(
        description="The observation frequency, either 'annual' or 'quarter'. The"
        " archived sheets stack annual averages and quarterly observations, whose"
        " year-end and Q4 dates coincide."
    )
    section: int = Field(
        default=1,
        description="The report section within the sheet (1-based). The detailed"
        " survey tables stack several sections that reuse the same row labels under"
        " a different, unlabeled statistic; this keeps each one distinct.",
    )


class FederalReserveKansasCityAgDatabookArchivedFetcher(
    Fetcher[
        FederalReserveKansasCityAgDatabookArchivedQueryParams,
        list[FederalReserveKansasCityAgDatabookArchivedData],
    ]
):
    """Kansas City Fed Archived Ag Finance Databook Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityAgDatabookArchivedQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityAgDatabookArchivedQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityAgDatabookArchivedQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the archived databook from the Kansas City Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city

        content = cached(
            "kansas_city_ag_databook_archived",
            lambda: seconds_until_next_release("annual"),
            lambda: fetch_kansas_city(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityAgDatabookArchivedQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityAgDatabookArchivedData]:
        """Melt the table, then pivot each series to a wide column per period."""
        from openbb_federal_reserve.utils.kansas_city_ag import parse_kc_annual_table
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_kc_annual_table(
            data[0]["_raw"],
            query.table,
            start_date=query.start_date,
            end_date=query.end_date,
        )
        rows = pivot_wide(
            records,
            index=("date", "frequency", "section"),
            column="series",
            value="value",
        )
        return [
            FederalReserveKansasCityAgDatabookArchivedData.model_validate(record)
            for record in rows
        ]
