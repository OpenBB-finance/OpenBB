"""Federal Reserve Bank of New York SCE Housing Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.sce import HOUSING_SHEETS, topic_map

URL = (
    "https://www.newyorkfed.org/medialibrary/interactives/sce/sce"
    "/downloads/data/frbny_sce_housing_chartdata.xlsx?sc_lang=en"
)

_TOPICS = topic_map(HOUSING_SHEETS)
_TOPIC_KEYS = tuple(_TOPICS)
_HEADER_ROW = 4


class FederalReserveNewYorkConsumerHousingQueryParams(QueryParams):
    """New York Fed SCE Housing Survey Query Parameters."""

    __json_schema_extra__ = {
        "topic": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Home Price Expectations",
                        "value": "home_price_expectations",
                    },
                    {
                        "label": "Home Price Expectations (Demographics)",
                        "value": "home_price_expectations_demo",
                    },
                    {
                        "label": "Home Price Change Distr",
                        "value": "home_price_change_distr",
                    },
                    {
                        "label": "Home Price Change Distr (Demographics)",
                        "value": "home_price_change_distr_demo",
                    },
                    {
                        "label": "Rent Change Expectations",
                        "value": "rent_change_expectations",
                    },
                    {
                        "label": "Rent Change Expectations (Demographics)",
                        "value": "rent_change_expectations_demo",
                    },
                    {
                        "label": "Housing As Investment",
                        "value": "housing_as_investment",
                    },
                    {
                        "label": "Housing As Investment (Demographics)",
                        "value": "housing_as_investment_demo",
                    },
                    {
                        "label": "Probability of Moving",
                        "value": "probability_of_moving",
                    },
                    {
                        "label": "Probability of Moving (Demographics)",
                        "value": "probability_of_moving_demo",
                    },
                    {
                        "label": "Probability of Buying",
                        "value": "probability_of_buying",
                    },
                    {
                        "label": "Probability of Buying (Demographics)",
                        "value": "probability_of_buying_demo",
                    },
                    {"label": "Rate Perceptions", "value": "rate_perceptions"},
                    {
                        "label": "Rate Perceptions (Demographics)",
                        "value": "rate_perceptions_demo",
                    },
                    {"label": "Rate Expectations", "value": "rate_expectations"},
                    {
                        "label": "Rate Expectations (Demographics)",
                        "value": "rate_expectations_demo",
                    },
                    {"label": "Rate Distribution", "value": "rate_distribution"},
                    {
                        "label": "Rate Distribution (Demographics)",
                        "value": "rate_distribution_demo",
                    },
                    {
                        "label": "Probability of Refinancing",
                        "value": "probability_of_refinancing",
                    },
                    {
                        "label": "Probability of Refinancing (Demographics)",
                        "value": "probability_of_refinancing_demo",
                    },
                    {
                        "label": "Prob of Home Investments",
                        "value": "prob_of_home_investments",
                    },
                    {
                        "label": "Prob of Home Investments (Demographics)",
                        "value": "prob_of_home_investments_demo",
                    },
                    {
                        "label": "Home Tenure Expectations",
                        "value": "home_tenure_expectations",
                    },
                    {
                        "label": "Home Tenure Expectations (Demographics)",
                        "value": "home_tenure_expectations_demo",
                    },
                    {
                        "label": "Ease of Obtaining Mortgage",
                        "value": "ease_of_obtaining_mortgage",
                    },
                    {
                        "label": "Ease of Obtaining Mortgage (Demographics)",
                        "value": "ease_of_obtaining_mortgage_demo",
                    },
                    {
                        "label": "Preference for Owning",
                        "value": "preference_for_owning",
                    },
                    {
                        "label": "Preference for Owning (Demographics)",
                        "value": "preference_for_owning_demo",
                    },
                    {
                        "label": "Renters Prob of Buying",
                        "value": "renters_prob_of_buying",
                    },
                    {
                        "label": "Renters Prob of Buying (Demographics)",
                        "value": "renters_prob_of_buying_demo",
                    },
                ]
            }
        }
    }

    topic: Literal[_TOPIC_KEYS] = Field(  # ty: ignore[invalid-type-form]
        default="home_price_expectations",
        description="The housing survey topic sheet. Topics ending in '_demo' break"
        " the series down by respondent demographics; '_distr' topics give the"
        " distribution of responses.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkConsumerHousingData(Data):
    """New York Fed SCE Housing Survey Data.

    One row per survey month, with one column per series within the topic. The
    series are pivoted to wide, so the columns vary with the selected topic sheet.
    """

    date: dateType = Field(description="The survey month.")


class FederalReserveNewYorkConsumerHousingFetcher(
    Fetcher[
        FederalReserveNewYorkConsumerHousingQueryParams,
        list[FederalReserveNewYorkConsumerHousingData],
    ]
):
    """New York Fed SCE Housing Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkConsumerHousingQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkConsumerHousingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkConsumerHousingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the SCE Housing workbook from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw SCE Housing workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "new_york_sce_housing",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkConsumerHousingQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkConsumerHousingData]:
        """Pivot the requested housing topic sheet to wide ``date`` + per-series."""
        from openbb_federal_reserve.utils.sce import parse_sce
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_sce(
            data[0]["_raw"],
            _TOPICS[query.topic],
            start_date=query.start_date,
            end_date=query.end_date,
            header_row=_HEADER_ROW,
        )
        return [
            FederalReserveNewYorkConsumerHousingData.model_validate(record)
            for record in pivot_wide(
                records, index="date", column="series", value="value"
            )
        ]
