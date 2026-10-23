"""Federal Reserve Bank of New York Empire State Manufacturing Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.ny_empire_survey import DATASETS

_DATASET_KEYS = tuple(DATASETS)


class FederalReserveNewYorkEmpireStateQueryParams(QueryParams):
    """New York Fed Empire State Manufacturing Survey Query Parameters."""

    __json_schema_extra__ = {
        "dataset": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Seasonally Adjusted Diffusion",
                        "value": "seasonally_adjusted_diffusion",
                    },
                    {
                        "label": "Not Seasonally Adjusted Diffusion",
                        "value": "not_seasonally_adjusted_diffusion",
                    },
                    {
                        "label": "Seasonally Adjusted All Series",
                        "value": "seasonally_adjusted_all_series",
                    },
                    {
                        "label": "Not Seasonally Adjusted All Series",
                        "value": "not_seasonally_adjusted_all_series",
                    },
                ]
            }
        }
    }

    dataset: Literal[_DATASET_KEYS] = Field(  # ty: ignore[invalid-type-form]
        default="seasonally_adjusted_diffusion",
        description="The published file to retrieve. The '_diffusion' files give"
        " one diffusion index per indicator; the '_all_series' files add the"
        " up / down / same response shares behind each index.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkEmpireStateData(Data):
    """New York Fed Empire State Manufacturing Survey Data."""

    date: dateType = Field(description="The survey month, as the month-end date.")


class FederalReserveNewYorkEmpireStateFetcher(
    Fetcher[
        FederalReserveNewYorkEmpireStateQueryParams,
        list[FederalReserveNewYorkEmpireStateData],
    ]
):
    """New York Fed Empire State Manufacturing Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkEmpireStateQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkEmpireStateQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkEmpireStateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Discover the rotating CSV hash and download the requested dataset."""
        import re

        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.ny_empire_survey import (
            BASE_URL,
            DATASETS,
            OVERVIEW_URL,
        )

        stem = DATASETS[query.dataset]

        def _producer() -> str:
            """Scrape the overview page for the dataset CSV, then fetch it."""
            overview = make_request(OVERVIEW_URL)
            overview.raise_for_status()
            match = re.search(
                rf"(/medialibrary/media/survey/empire/data/{stem}\.csv[^\"']*)",
                overview.text,
                re.IGNORECASE,
            )
            if not match:
                return ""
            href = match.group(1).replace("&amp;", "&")
            response = make_request(f"{BASE_URL}{href}")
            response.raise_for_status()
            return response.text

        text = cached(
            ("new_york_empire", query.dataset),
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkEmpireStateQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkEmpireStateData]:
        """Pivot the requested dataset to wide ``date`` + per-series columns."""
        from openbb_federal_reserve.utils.ny_empire_survey import parse
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse(
            data[0]["_raw"],
            start_date=query.start_date,
            end_date=query.end_date,
        )
        return [
            FederalReserveNewYorkEmpireStateData.model_validate(record)
            for record in pivot_wide(
                records, index="date", column="series", value="value"
            )
        ]
