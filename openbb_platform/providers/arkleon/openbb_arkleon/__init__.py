"""Arkleon provider extension for the OpenBB Platform."""

from openbb_arkleon.models.balance_sheet import ArkleonBalanceSheetFetcher
from openbb_arkleon.models.cash_flow import ArkleonCashFlowStatementFetcher
from openbb_arkleon.models.income_statement import ArkleonIncomeStatementFetcher
from openbb_core.provider.abstract.provider import Provider

arkleon_provider = Provider(
    name="arkleon",
    description=(
        "Point-in-time SEC fundamentals from Arkleon /v1: accounting values as filed, "
        "limited to filings filed on or before as_of."
    ),
    website="https://arkleon.com",
    credentials=["api_key"],
    fetcher_dict={
        "BalanceSheet": ArkleonBalanceSheetFetcher,
        "IncomeStatement": ArkleonIncomeStatementFetcher,
        "CashFlowStatement": ArkleonCashFlowStatementFetcher,
    },
    repr_name="Arkleon",
    instructions=(
        "Set the ARKLEON_API_KEY environment variable, or set obb.user.credentials.arkleon_api_key, "
        "to an issued Arkleon ak_ key."
    ),
)
