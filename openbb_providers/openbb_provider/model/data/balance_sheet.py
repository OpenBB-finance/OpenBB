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
    assets : Optional[int]
        The assets of the balance sheet.
    current_assets : Optional[int]
        The current assets of the balance sheet.
    current_liabilities : Optional[int]
        The current liabilities of the balance sheet.
    equity : Optional[int]
        The equity of the balance sheet.
    equity_attributable_to_noncontrolling_interest : Optional[int]
        The equity attributable to noncontrolling interest of the balance sheet.
    equity_attributable_to_parent : Optional[int]
        The equity attributable to parent of the balance sheet.
    liabilities : Optional[int]
        The liabilities of the balance sheet.
    liabilities_and_equity : Optional[int]
        The liabilities and equity of the balance sheet.
    noncurrent_assets : Optional[int]
        The noncurrent assets of the balance sheet.
    noncurrent_liabilities : Optional[int]
        The noncurrent liabilities of the balance sheet.
    """

    date: dateType
    # currency: Optional[str]
    cik: Optional[int]
    # period: Optional[str]
    assets: Optional[int]
    current_assets: Optional[int]
    current_liabilities: Optional[int]
    equity: Optional[int]
    equity_attributable_to_noncontrolling_interest: Optional[int]
    equity_attributable_to_parent: Optional[int]
    liabilities: Optional[int]
    liabilities_and_equity: Optional[int]
    noncurrent_assets: Optional[int]
    noncurrent_liabilities: Optional[int]
