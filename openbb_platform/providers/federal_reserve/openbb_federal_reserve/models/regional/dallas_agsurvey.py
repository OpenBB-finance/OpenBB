"""Federal Reserve Bank of Dallas Agricultural Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = "https://www.dallasfed.org/-/media/Documents/research/surveys/AgSurvey/data"

_FILES = {
    "credit": "agcredit.xlsx",
    "lending": "aglending.xlsx",
    "interest_rates": "agrates.xlsx",
    "cash_rents": "agrents.xlsx",
    "land_values": "agvalue.xlsx",
    "loan_volume": "agvolume.xlsx",
}


class FederalReserveDallasAgSurveyQueryParams(QueryParams):
    """Dallas Fed Agricultural Survey Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Farm Credit Conditions", "value": "credit"},
                    {"label": "Loan Demand and Lending", "value": "lending"},
                    {"label": "Interest Rates", "value": "interest_rates"},
                    {"label": "Cash Rents", "value": "cash_rents"},
                    {"label": "Land Values", "value": "land_values"},
                    {"label": "Loan Volume", "value": "loan_volume"},
                ]
            }
        },
    }

    table: Literal[
        "credit",
        "lending",
        "interest_rates",
        "cash_rents",
        "land_values",
        "loan_volume",
    ] = Field(
        default="credit",
        description="The survey table: anticipated farm credit conditions, loan"
        " demand and lending, interest rates, cash rents, land values, or loan"
        " volume.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasAgSurveyData(Data):
    """Dallas Fed Agricultural Survey Data."""

    date: dateType = Field(description="The survey quarter-end date.")


class FederalReserveDallasAgSurveyFetcher(
    Fetcher[
        FederalReserveDallasAgSurveyQueryParams,
        list[FederalReserveDallasAgSurveyData],
    ]
):
    """Dallas Fed Agricultural Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasAgSurveyQueryParams:
        """Transform the query params."""
        return FederalReserveDallasAgSurveyQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasAgSurveyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the requested agricultural survey table from the Dallas Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        filename = _FILES[query.table]

        def _producer() -> bytes:
            """Fetch the raw survey workbook bytes."""
            response = make_request(f"{BASE_URL}/{filename}")
            response.raise_for_status()
            return response.content

        content = cached(
            ("dallas_agsurvey", query.table),
            lambda: seconds_until_next_release("quarterly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasAgSurveyQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasAgSurveyData]:
        """Melt the survey table, then pivot the series to wide ``date`` rows."""
        from openbb_federal_reserve.utils.dallas import find_label_row, melt_two_level
        from openbb_federal_reserve.utils.workbook import pivot_wide

        label_row = find_label_row(data[0]["_raw"], 0)
        records = melt_two_level(
            data[0]["_raw"],
            0,
            label_row=label_row,
            date_kind="quarter",
            start_date=query.start_date,
            end_date=query.end_date,
        )
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveDallasAgSurveyData.model_validate(record) for record in rows
        ]
