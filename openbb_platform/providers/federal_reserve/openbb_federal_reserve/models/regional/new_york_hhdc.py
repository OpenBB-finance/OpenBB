"""Federal Reserve Bank of New York Household Debt and Credit Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.ny_hhdc import TABLES

_TABLE_KEYS = tuple(TABLES)


class FederalReserveNewYorkHouseholdDebtQueryParams(QueryParams):
    """New York Fed Household Debt and Credit Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Total Debt Balance", "value": "total_debt_balance"},
                    {
                        "label": "Number of Accounts by Loan Type",
                        "value": "number_of_accounts_by_loan_type",
                    },
                    {
                        "label": "New and Closed Accounts and Inquiries",
                        "value": "new_and_closed_accounts_and_inquiries",
                    },
                    {
                        "label": "Mortgage Originations by Credit Score",
                        "value": "mortgage_originations_by_credit_score",
                    },
                    {
                        "label": "Credit Score at Origination Mortgages",
                        "value": "credit_score_at_origination_mortgages",
                    },
                    {
                        "label": "Auto Loan Originations by Credit Score",
                        "value": "auto_loan_originations_by_credit_score",
                    },
                    {
                        "label": "Credit Score at Origination Auto Loans",
                        "value": "credit_score_at_origination_auto_loans",
                    },
                    {
                        "label": "Credit Limit and Balance Cards and He Revolving",
                        "value": "credit_limit_and_balance_cards_and_he_revolving",
                    },
                    {
                        "label": "Total Balance by Delinquency Status",
                        "value": "total_balance_by_delinquency_status",
                    },
                    {
                        "label": "Percent of Balance 90 Days Delinquent by Loan Type",
                        "value": "percent_of_balance_90_days_delinquent_by_loan_type",
                    },
                    {
                        "label": "Flow Into Early Delinquency by Loan Type",
                        "value": "flow_into_early_delinquency_by_loan_type",
                    },
                    {
                        "label": "Flow Into Serious Delinquency by Loan Type",
                        "value": "flow_into_serious_delinquency_by_loan_type",
                    },
                    {
                        "label": "Transition Rates Current Mortgage Accounts",
                        "value": "transition_rates_current_mortgage_accounts",
                    },
                    {
                        "label": "Transition Rates 30 60 Day Late Mortgage Accounts",
                        "value": "transition_rates_30_60_day_late_mortgage_accounts",
                    },
                    {
                        "label": "New Foreclosures and Bankruptcies",
                        "value": "new_foreclosures_and_bankruptcies",
                    },
                    {
                        "label": "Third Party Collections",
                        "value": "third_party_collections",
                    },
                    {
                        "label": "Total Debt Balance by Age",
                        "value": "total_debt_balance_by_age",
                    },
                    {
                        "label": "Debt Share by Product Type and Age",
                        "value": "debt_share_by_product_type_and_age",
                    },
                    {
                        "label": "Auto Loan Originations by Age",
                        "value": "auto_loan_originations_by_age",
                    },
                    {
                        "label": "Mortgage Originations by Age",
                        "value": "mortgage_originations_by_age",
                    },
                    {
                        "label": "Transition Into Serious Delinquency by Age",
                        "value": "transition_into_serious_delinquency_by_age",
                    },
                    {
                        "label": "Transition Into Serious Delinquency Mortgages by Age",
                        "value": "transition_into_serious_delinquency_mortgages_by_age",
                    },
                    {
                        "label": "Transition Into Serious Delinquency Auto Loans by Age",
                        "value": "transition_into_serious_delinquency_auto_loans_by_age",
                    },
                    {
                        "label": "Transition Into Serious Delinquency Credit Cards by Age",
                        "value": "transition_into_serious_delinquency_credit_cards_by_age",
                    },
                    {
                        "label": "Transition Into Serious Delinquency Student Loans by Age",
                        "value": "transition_into_serious_delinquency_student_loans_by_age",
                    },
                    {
                        "label": "New Foreclosures by Age",
                        "value": "new_foreclosures_by_age",
                    },
                    {
                        "label": "New Bankruptcies by Age",
                        "value": "new_bankruptcies_by_age",
                    },
                    {
                        "label": "Composition of Debt Balance per Capita by State",
                        "value": "composition_of_debt_balance_per_capita_by_state",
                    },
                    {
                        "label": "Delinquency Status per Capita by State Recent",
                        "value": "delinquency_status_per_capita_by_state_recent",
                    },
                    {
                        "label": "Delinquency Status per Capita by State Prior",
                        "value": "delinquency_status_per_capita_by_state_prior",
                    },
                    {
                        "label": "Percent of Balance 90 Days Late by State",
                        "value": "percent_of_balance_90_days_late_by_state",
                    },
                    {
                        "label": "Percent of Mortgage Debt 90 Days Late by State",
                        "value": "percent_of_mortgage_debt_90_days_late_by_state",
                    },
                    {
                        "label": "Transition Rates Into 30 Days Late by State",
                        "value": "transition_rates_into_30_days_late_by_state",
                    },
                    {
                        "label": "Transition Rates Into 90 Days Late by State",
                        "value": "transition_rates_into_90_days_late_by_state",
                    },
                    {
                        "label": "Percent of Consumers With New Foreclosures by State",
                        "value": "percent_of_consumers_with_new_foreclosures_by_state",
                    },
                    {
                        "label": "Percent of Consumers With New Bankruptcies by State",
                        "value": "percent_of_consumers_with_new_bankruptcies_by_state",
                    },
                ]
            }
        }
    }

    table: Literal[_TABLE_KEYS] = Field(  # ty: ignore[invalid-type-form]
        default="total_debt_balance",
        description="The report table to retrieve. Each table corresponds to one"
        " chart in the Quarterly Report on Household Debt and Credit, including"
        " national, by-age, and by-state breakdowns.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkHouseholdDebtData(Data):
    """New York Fed Household Debt and Credit Data.

    One row per quarter, with one column per series within the requested table.
    The series are pivoted to wide, so the columns vary with the selected report
    table.
    """

    date: dateType = Field(description="The quarter, as the quarter-end date.")


class FederalReserveNewYorkHouseholdDebtFetcher(
    Fetcher[
        FederalReserveNewYorkHouseholdDebtQueryParams,
        list[FederalReserveNewYorkHouseholdDebtData],
    ]
):
    """New York Fed Household Debt and Credit Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkHouseholdDebtQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkHouseholdDebtQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkHouseholdDebtQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Discover the latest quarter and download the HHDC workbook."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.ny_hhdc import (
            XLSX_URL,
            latest_household_debt_quarter,
        )

        quarter = latest_household_debt_quarter()

        def _producer() -> bytes:
            """Fetch the raw HHDC workbook bytes for the latest quarter."""
            response = make_request(XLSX_URL.format(quarter))
            response.raise_for_status()
            return response.content

        content = cached(
            ("new_york_hhdc", quarter),
            lambda: seconds_until_next_release("quarterly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkHouseholdDebtQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkHouseholdDebtData]:
        """Pivot the requested table to wide ``date`` + per-series columns."""
        from openbb_federal_reserve.utils.ny_hhdc import TABLES, parse_hhdc_sheet
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_hhdc_sheet(
            data[0]["_raw"],
            TABLES[query.table],
            start_date=query.start_date,
            end_date=query.end_date,
        )
        return [
            FederalReserveNewYorkHouseholdDebtData.model_validate(record)
            for record in pivot_wide(
                records, index="date", column="series", value="value"
            )
        ]
