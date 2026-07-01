"""Federal Reserve Bank of Richmond Fifth District Manufacturing Survey Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.richmondfed.org/-/media/RichmondFedOrg/region_communities"
    "/regional_data_analysis/regional_economy/surveys_of_business_conditions"
    "/manufacturing/data/mfg_historicaldata.xlsx"
)
SHEET = "Mfg Historical Series"


class FederalReserveRichmondManufacturingQueryParams(QueryParams):
    """Richmond Fed Fifth District Manufacturing Survey Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveRichmondManufacturingData(Data):
    """Richmond Fed Fifth District Manufacturing Survey Data.

    One row per (date, adjustment, horizon), with one column per survey indicator
    carrying that indicator's diffusion-index value. The indicators are pivoted to
    wide, so the indicator columns are dynamic.
    """

    date: dateType = Field(description="The survey month.")
    adjustment: str | None = Field(
        default=None, description="The seasonal adjustment (NSA or SA)."
    )
    horizon: str | None = Field(
        default=None, description="Current conditions or six-month-ahead expectations."
    )


class FederalReserveRichmondManufacturingFetcher(
    Fetcher[
        FederalReserveRichmondManufacturingQueryParams,
        list[FederalReserveRichmondManufacturingData],
    ]
):
    """Richmond Fed Fifth District Manufacturing Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveRichmondManufacturingQueryParams:
        """Transform the query params."""
        return FederalReserveRichmondManufacturingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveRichmondManufacturingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the manufacturing-survey workbook from the Richmond Fed."""
        from openbb_federal_reserve.utils.richmond_surveys import fetch_survey_workbook

        content = fetch_survey_workbook("manufacturing")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveRichmondManufacturingQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveRichmondManufacturingData]:
        """Decode the manufacturing-survey sheet into wide indicator records."""
        from openbb_federal_reserve.utils.richmond_surveys import parse_survey_wide

        records = parse_survey_wide(
            data[0]["_raw"], SHEET, query.start_date, query.end_date
        )
        return [
            FederalReserveRichmondManufacturingData.model_validate(record)
            for record in records
        ]
