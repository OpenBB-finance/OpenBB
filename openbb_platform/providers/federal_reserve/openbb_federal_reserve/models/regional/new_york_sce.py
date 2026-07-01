"""Federal Reserve Bank of New York Survey of Consumer Expectations Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.sce import INFLATION_SHEETS, topic_map

URL = (
    "https://www.newyorkfed.org/medialibrary/interactives/sce/sce"
    "/downloads/data/frbny-sce-data.xlsx"
)

_TOPICS = topic_map(INFLATION_SHEETS)
_TOPIC_KEYS = tuple(_TOPICS)


class FederalReserveNewYorkConsumerExpectationsQueryParams(QueryParams):
    """New York Fed Survey of Consumer Expectations Query Parameters."""

    __json_schema_extra__ = {
        "topic": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Inflation Expectations",
                        "value": "inflation_expectations",
                    },
                    {
                        "label": "Inflation Expectations (Demographics)",
                        "value": "inflation_expectations_demo",
                    },
                    {
                        "label": "Inflation Uncertainty",
                        "value": "inflation_uncertainty",
                    },
                    {
                        "label": "Inflation Uncertainty (Demographics)",
                        "value": "inflation_uncertainty_demo",
                    },
                    {
                        "label": "Home Price Expectations",
                        "value": "home_price_expectations",
                    },
                    {
                        "label": "Home Price Expectations (Demographics)",
                        "value": "home_price_expectations_demo",
                    },
                    {
                        "label": "Home Price Uncertainty",
                        "value": "home_price_uncertainty",
                    },
                    {
                        "label": "Home Price Uncertainty (Demographics)",
                        "value": "home_price_uncertainty_demo",
                    },
                    {
                        "label": "Commodity Expectations",
                        "value": "commodity_expectations",
                    },
                    {"label": "Earnings Growth", "value": "earnings_growth"},
                    {
                        "label": "Earnings Growth (Demographics)",
                        "value": "earnings_growth_demo",
                    },
                    {"label": "Earnings Uncertainty", "value": "earnings_uncertainty"},
                    {
                        "label": "Earnings Uncertainty (Demographics)",
                        "value": "earnings_uncertainty_demo",
                    },
                    {
                        "label": "Job Separation Expectation",
                        "value": "job_separation_expectation",
                    },
                    {
                        "label": "Job Separation Expectation (Demographics)",
                        "value": "job_separation_expectation_demo",
                    },
                    {
                        "label": "Job Finding Expectations",
                        "value": "job_finding_expectations",
                    },
                    {
                        "label": "Job Finding Expectations (Demographics)",
                        "value": "job_finding_expectations_demo",
                    },
                    {"label": "Moving Expectations", "value": "moving_expectations"},
                    {
                        "label": "Moving Expectations (Demographics)",
                        "value": "moving_expectations_demo",
                    },
                    {
                        "label": "Unemployment Expectations",
                        "value": "unemployment_expectations",
                    },
                    {
                        "label": "Unemployment Expectations (Demographics)",
                        "value": "unemployment_expectations_demo",
                    },
                    {"label": "Hh Income Change", "value": "hh_income_change"},
                    {
                        "label": "Hh Income Change (Demographics)",
                        "value": "hh_income_change_demo",
                    },
                    {"label": "Hh Spending Change", "value": "hh_spending_change"},
                    {
                        "label": "Hh Spending Change (Demographics)",
                        "value": "hh_spending_change_demo",
                    },
                    {"label": "Taxes Change", "value": "taxes_change"},
                    {
                        "label": "Taxes Change (Demographics)",
                        "value": "taxes_change_demo",
                    },
                    {"label": "Credit Availability", "value": "credit_availability"},
                    {
                        "label": "Household Financial Situation",
                        "value": "household_financial_situation",
                    },
                    {
                        "label": "Delinquency Expectations",
                        "value": "delinquency_expectations",
                    },
                    {
                        "label": "Delinquency Expectations (Demographics)",
                        "value": "delinquency_expectations_demo",
                    },
                    {
                        "label": "Interest Rate Expectations",
                        "value": "interest_rate_expectations",
                    },
                    {
                        "label": "Interest Rate Expectations (Demographics)",
                        "value": "interest_rate_expectations_demo",
                    },
                    {"label": "Stock Prices", "value": "stock_prices"},
                    {
                        "label": "Stock Prices (Demographics)",
                        "value": "stock_prices_demo",
                    },
                    {"label": "Government Debt", "value": "government_debt"},
                    {
                        "label": "Government Debt (Demographics)",
                        "value": "government_debt_demo",
                    },
                    {
                        "label": "Inflation Expectations Distr",
                        "value": "inflation_expectations_distr",
                    },
                    {"label": "Prob of Infl Outcome", "value": "prob_of_infl_outcome"},
                    {
                        "label": "Prob of Infl Outcome (Demographics)",
                        "value": "prob_of_infl_outcome_demo",
                    },
                    {
                        "label": "Five Year Ahead Infl Exp",
                        "value": "five_year_ahead_infl_exp",
                    },
                    {
                        "label": "Five Year Ahead Infl Exp (Demographics)",
                        "value": "five_year_ahead_infl_exp_demo",
                    },
                ]
            }
        }
    }

    topic: Literal[_TOPIC_KEYS] = Field(  # ty: ignore[invalid-type-form]
        default="inflation_expectations",
        description="The survey topic sheet. Topics ending in '_demo' break the"
        " series down by respondent demographics; '_distr' topics give the"
        " distribution of responses.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkConsumerExpectationsData(Data):
    """New York Fed Survey of Consumer Expectations Data.

    One row per survey month, with one column per series within the topic. The
    series are pivoted to wide, so the columns vary with the selected topic sheet.
    """

    date: dateType = Field(description="The survey month.")


class FederalReserveNewYorkConsumerExpectationsFetcher(
    Fetcher[
        FederalReserveNewYorkConsumerExpectationsQueryParams,
        list[FederalReserveNewYorkConsumerExpectationsData],
    ]
):
    """New York Fed Survey of Consumer Expectations Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkConsumerExpectationsQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkConsumerExpectationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkConsumerExpectationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the SCE inflation workbook from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw SCE workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "new_york_sce", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkConsumerExpectationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkConsumerExpectationsData]:
        """Pivot the requested topic sheet to wide ``date`` + per-series columns."""
        from openbb_federal_reserve.utils.sce import parse_sce
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_sce(
            data[0]["_raw"],
            _TOPICS[query.topic],
            start_date=query.start_date,
            end_date=query.end_date,
        )
        return [
            FederalReserveNewYorkConsumerExpectationsData.model_validate(record)
            for record in pivot_wide(
                records, index="date", column="series", value="value"
            )
        ]
