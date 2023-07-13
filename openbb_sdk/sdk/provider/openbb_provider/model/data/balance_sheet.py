"""Balance Sheet Data Model."""


from datetime import date as dateType
from typing import Optional

from openbb_provider.model.abstract.data import Data
from openbb_provider.model.data.base import FinancialStatementQueryParams

# IMPORT THIRD PARTY


class BalanceSheetQueryParams(FinancialStatementQueryParams):
    """Cash flow statement query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period : Literal["annually", "quarterly"]
        The period of the balance sheet.
    """


class BalanceSheetData(Data):
    """Return Balance Sheet Data.

    Returns
    -------
    date : date
        The date of the balance sheet.
    cik : Optional[int]
        The CIK of the balance sheet.
    cash_and_cash_equivalents : Optional[int]
        The cash and cash equivalents of the balance sheet.
    short_term_investments : Optional[int]
        The short term investments of the balance sheet.
    cash_and_short_term_investments : Optional[int]
        The cash and short term investments of the balance sheet.
    net_receivables : Optional[int]
        The net receivables of the balance sheet.
    inventory : Optional[int]
        The inventory of the balance sheet.
    other_current_assets : Optional[int]
        The other current assets of the balance sheet.
    current_assets : Optional[int]
        The current assets of the balance sheet.
    long_term_investments : Optional[int]
        The long term investments of the balance sheet.
    property_plant_equipment_net : Optional[int]
        The property plant equipment net of the balance sheet.
    other_non_current_assets : Optional[int]
        The other non current assets of the balance sheet.
    noncurrent_assets : Optional[int]
        The non current assets of the balance sheet.
    assets : Optional[int]
        The assets of the balance sheet.
    accounts_payable : Optional[int]
        The accounts payable of the balance sheet.
    other_current_liabilities : Optional[int]
        The other current liabilities of the balance sheet.
    deferred_revenue : Optional[int]
        The deferred revenue of the balance sheet.
    current_liabilities : Optional[int]
        The current liabilities of the balance sheet.
    long_term_debt : Optional[int]
        The long term debt of the balance sheet.
    other_non_current_liabilities : Optional[int]
        The other non current liabilities of the balance sheet.
    noncurrent_liabilities : Optional[int]
        The non current liabilities of the balance sheet.
    liabilities : Optional[int]
        The liabilities of the balance sheet.
    common_stock : Optional[int]
        The common stock of the balance sheet.
    retained_earnings : Optional[int]
        The retained earnings of the balance sheet.
    accumulated_other_comprehensive_income_loss : Optional[int]
        The accumulated other comprehensive income loss of the balance sheet.
    total_equity : Optional[int]
        The total equity of the balance sheet.
    total_liabilities_and_stockholders_equity : Optional[int]
        The total liabilities and stockholders equity of the balance sheet.
    """

    date: dateType
    cik: Optional[int]

    cash_and_cash_equivalents: Optional[int]
    short_term_investments: Optional[int]
    cash_and_short_term_investments: Optional[int]
    net_receivables: Optional[int]
    inventory: Optional[int]
    other_current_assets: Optional[int]
    current_assets: Optional[int]

    long_term_investments: Optional[int]
    property_plant_equipment_net: Optional[int]
    other_non_current_assets: Optional[int]
    noncurrent_assets: Optional[int]
    assets: Optional[int]

    account_payables: Optional[int]
    other_current_liabilities: Optional[int]
    deferred_revenue: Optional[int]
    current_liabilities: Optional[int]

    long_term_debt: Optional[int]
    other_non_current_liabilities: Optional[int]
    noncurrent_liabilities: Optional[int]
    liabilities: Optional[int]

    common_stock: Optional[int]
    retained_earnings: Optional[int]
    accumulated_other_comprehensive_income_loss: Optional[int]
    total_equity: Optional[int]
    total_liabilities_and_stockholders_equity: Optional[int]
