"""Nasdaq Financial Statement Parsing.

Nasdaq publishes each statement as a label-per-row table with one column per
fiscal period. These helpers pivot that layout into one record per period and
map the Nasdaq row labels onto the OpenBB standard statement fields.
"""

from __future__ import annotations

from typing import Any

INCOME_STATEMENT_MAP = {
    "Total Revenue": "revenue",
    "Cost of Revenue": "cost_of_revenue",
    "Gross Profit": "gross_profit",
    "Operating Expenses": "total_operating_expenses",
    "Research and Development": "research_and_development_expense",
    "Sales, General and Admin.": "selling_general_and_administrative_expense",
    "Non-Recurring Items": "non_recurring_items",
    "Other Operating Items": "other_operating_expenses",
    "Operating Income": "operating_income",
    "Add'l income/expense items": "additional_income_expense_items",
    "Earnings Before Interest and Tax": "ebit",
    "Interest Expense": "interest_expense",
    "Earnings Before Tax": "income_before_tax",
    "Income Tax": "income_tax_expense",
    "Minority Interest": "minority_interest",
    "Equity Earnings/Loss Unconsolidated Subsidiary": "equity_earnings",
    "Net Income-Cont. Operations": "net_income_from_continuing_operations",
    "Net Income": "consolidated_net_income",
    "Net Income Applicable to Common Shareholders": "net_income",
}

BALANCE_SHEET_MAP = {
    "Cash and Cash Equivalents": "cash_and_cash_equivalents",
    "Short-Term Investments": "short_term_investments",
    "Net Receivables": "net_receivables",
    "Inventory": "inventory",
    "Other Current Assets": "other_current_assets",
    "Total Current Assets": "total_current_assets",
    "Long-Term Investments": "long_term_investments",
    "Fixed Assets": "property_plant_equipment_net",
    "Goodwill": "goodwill",
    "Intangible Assets": "intangible_assets",
    "Other Assets": "other_non_current_assets",
    "Deferred Asset Charges": "deferred_asset_charges",
    "Total Assets": "total_assets",
    "Accounts Payable": "accounts_payable",
    "Short-Term Debt / Current Portion of Long-Term Debt": "short_term_debt",
    "Other Current Liabilities": "other_current_liabilities",
    "Total Current Liabilities": "total_current_liabilities",
    "Long-Term Debt": "long_term_debt",
    "Other Liabilities": "other_non_current_liabilities",
    "Deferred Liability Charges": "deferred_liability_charges",
    "Misc. Stocks": "misc_stocks",
    "Minority Interest": "minority_interest",
    "Total Liabilities": "total_liabilities",
    "Common Stocks": "common_stock",
    "Capital Surplus": "additional_paid_in_capital",
    "Retained Earnings": "retained_earnings",
    "Treasury Stock": "treasury_stock",
    "Other Equity": "other_shareholders_equity",
    "Total Equity": "total_shareholders_equity",
    "Total Liabilities & Equity": "total_liabilities_and_shareholders_equity",
}

CASH_FLOW_MAP = {
    "Net Income": "net_income",
    "Depreciation": "depreciation_and_amortization",
    "Net Income Adjustments": "other_non_cash_items",
    "Accounts Receivable": "change_in_receivables",
    "Changes in Inventories": "change_in_inventory",
    "Other Operating Activities": "other_operating_activities",
    "Liabilities": "change_in_payables",
    "Net Cash Flow-Operating": "net_cash_flow_from_operating_activities",
    "Capital Expenditures": "capital_expenditure",
    "Investments": "purchase_of_investments",
    "Other Investing Activities": "other_investing_activities",
    "Net Cash Flows-Investing": "net_cash_flow_from_investing_activities",
    "Sale and Purchase of Stock": "net_stock_issuance",
    "Net Borrowings": "net_debt_issuance",
    "Other Financing Activities": "other_financing_activities",
    "Net Cash Flows-Financing": "net_cash_flow_from_financing_activities",
    "Effect of Exchange Rate": "effect_of_exchange_rate_changes_on_cash",
    "Net Cash Flow": "net_change_in_cash_and_equivalents",
}

FINANCIAL_RATIOS_MAP = {
    "Current Ratio": "current_ratio",
    "Quick Ratio": "quick_ratio",
    "Cash Ratio": "cash_ratio",
    "Gross Margin": "gross_profit_margin",
    "Operating Margin": "operating_profit_margin",
    "Pre-Tax Margin": "pretax_profit_margin",
    "Profit Margin": "net_profit_margin",
    "Pre-Tax ROE": "pretax_return_on_equity",
    "After Tax ROE": "return_on_equity",
}

PERCENT_RATIOS = {
    "gross_profit_margin",
    "operating_profit_margin",
    "pretax_profit_margin",
    "net_profit_margin",
    "pretax_return_on_equity",
    "return_on_equity",
}

TABLE_KEYS = {
    "income": "incomeStatementTable",
    "balance": "balanceSheetTable",
    "cash": "cashFlowTable",
    "ratios": "financialRatiosTable",
}


async def get_financials(symbol: str, period: str) -> dict:
    """Get the four financial statement tables for a symbol.

    Parameters
    ----------
    symbol : str
        The ticker symbol.
    period : str
        Either 'annual' or 'quarter'.

    Returns
    -------
    dict
        The Nasdaq financials payload.
    """
    from openbb_nasdaq.utils.helpers import get_nasdaq_data

    frequency = 1 if period == "annual" else 2

    return await get_nasdaq_data(
        f"company/{symbol.upper()}/financials?frequency={frequency}"
    )


def parse_statement(
    payload: dict,
    table: str,
    field_map: dict[str, str],
    symbol: str,
    period: str,
) -> list[dict]:
    """Pivot one Nasdaq statement table into one record per fiscal period.

    Parameters
    ----------
    payload : dict
        The Nasdaq financials payload.
    table : str
        One of the keys in ``TABLE_KEYS``.
    field_map : dict[str, str]
        Nasdaq row label mapped to the OpenBB standard field name.
    symbol : str
        The ticker symbol.
    period : str
        Either 'annual' or 'quarter'.

    Returns
    -------
    list[dict]
        One record per period, newest first.
    """
    from openbb_nasdaq.utils.helpers import to_date, to_number

    statement = (payload or {}).get(TABLE_KEYS[table]) or {}
    headers = statement.get("headers") or {}
    rows = statement.get("rows") or []
    columns = [c for c in headers if c != "value1"]
    results: list[dict] = []

    for column in columns:
        period_ending = to_date(headers.get(column))

        if period_ending is None:
            continue

        record: dict[str, Any] = {
            "symbol": symbol.upper(),
            "period_ending": period_ending,
            "fiscal_period": period,
            "fiscal_year": period_ending.year,
        }

        for row in rows:
            field = field_map.get(str(row.get("value1", "")).strip())

            if field is None:
                continue

            value = to_number(row.get(column))

            if value is None:
                continue

            record[field] = value / 100 if field in PERCENT_RATIOS else value

        if len(record) > 4:
            results.append(record)

    return sorted(results, key=lambda r: r["period_ending"], reverse=True)
