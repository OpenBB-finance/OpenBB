"""Income Statement Data Model."""


from datetime import date as dateType
from typing import Optional

from openbb_provider.abstract.data import Data
from openbb_provider.models.base import FinancialStatementQueryParams


class IncomeStatementQueryParams(FinancialStatementQueryParams):
    """Income statement query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period : Literal["annually", "quarterly"]
        The period of the income statement.
    """


class IncomeStatementData(Data):
    """Income Statement Data.

    Returns
    -------
    date : date
        The date of the income statement.
    symbol : str
        The symbol of the company.
    currency : Optional[str]
        The currency of the income statement.
    cik : Optional[int]
        The Central Index Key (CIK) of the company.
    filing_date : date
        The filing date of the income statement.
    accepted_date : Optional[date]
        The accepted date of the income statement.
    period : Optional[str]
        The period of the income statement.
    revenue : Optional[int]
        The revenue of the income statement.
    cost_of_revenue : Optional[int]
        The cost of revenue of the income statement.
    gross_profit : Optional[int]
        The gross profit of the income statement.
    research_and_development_expenses : Optional[int]
        The research and development expenses of the income statement.
    general_and_administrative_expenses : Optional[int]
        The general and administrative expenses of the income statement.
    selling_and_marketing_expenses : Optional[float]
        The selling and marketing expenses of the income statement.
    selling_general_and_administrative_expenses : Optional[int]
        The selling, general and administrative expenses of the income statement.
    other_expenses : Optional[int]
        The other expenses of the income statement.
    operating_expenses : Optional[int]
        The operating expenses of the income statement.
    depreciation_and_amortization : Optional[int]
        The depreciation and amortization of the income statement.
    ebitda : Optional[int]
        The earnings before interest, taxes, depreciation and amortization of the income statement.
    operating_income : Optional[int]
        The operating income of the income statement.
    interest_income : Optional[int]
        The interest income of the income statement.
    interest_expense : Optional[int]
        The interest expense of the income statement.
    total_other_income_expenses_net : Optional[int]
        The total other income expenses net of the income statement.
    income_before_tax : Optional[int]
        The income before tax of the income statement.
    income_tax_expense : Optional[int]
        The income tax expense of the income statement.
    net_income : Optional[int]
        The net income of the income statement.
    eps : Optional[float]
        The earnings per share of the income statement.
    eps_diluted : Optional[float]
        The diluted earnings per share of the income statement.
    weighted_average_shares_outstanding : Optional[int]
        The weighted average shares outstanding of the income statement.
    weighted_average_shares_outstanding_dil : Optional[int]
        The weighted average shares outstanding diluted of the income statement.
    """

    date: dateType
    currency: Optional[str] = None
    filing_date: Optional[dateType] = None
    accepted_date: Optional[dateType] = None
    period: Optional[str]

    revenue: Optional[int]
    cost_of_revenue: Optional[int]
    gross_profit: Optional[int]

    research_and_development_expenses: Optional[int] = None
    general_and_administrative_expenses: Optional[int] = None
    selling_and_marketing_expenses: Optional[float] = None
    selling_general_and_administrative_expenses: Optional[int] = None
    other_expenses: Optional[int] = None
    operating_expenses: Optional[int]

    depreciation_and_amortization: Optional[int] = None
    ebitda: Optional[int] = None
    operating_income: Optional[int] = None

    interest_income: Optional[int] = None
    interest_expense: Optional[int] = None
    total_other_income_expenses_net: Optional[int] = None
    income_before_tax: Optional[int]
    income_tax_expense: Optional[int]

    net_income: Optional[int]
    eps: Optional[float]
    eps_diluted: Optional[float]
    weighted_average_shares_outstanding: Optional[int] = None
    weighted_average_shares_outstanding_dil: Optional[int] = None
