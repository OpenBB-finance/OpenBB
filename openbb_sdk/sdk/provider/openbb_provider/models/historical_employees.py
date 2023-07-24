"""Historical Employees data model."""


from datetime import date, datetime

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol


class HistoricalEmployeesQueryParams(QueryParams, BaseSymbol):
    """Historical Employees query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class HistoricalEmployeesData(Data):
    """Historical Employees data.

    Returns
    -------
    symbol : str
        The symbol of the company to retrieve the historical employees of.
    cik : int
        The CIK of the company to retrieve the historical employees of.
    acceptance_time : datetime
        The time of acceptance of the company employee.
    period_of_report : date
        The date of reporting of the company employee.
    company_name : str
        The registered name of the company to retrieve the historical employees of.
    form_type : float
        The form type of the company employee.
    filing_date : date
        The filing date of the company employee
    employee_count : int
        The count of employees of the company.
    source : str
        The source URL which retrieves this data for the company.
    """

    symbol: str
    cik: int
    acceptance_time: datetime
    period_of_report: date
    company_name: str
    form_type: str
    filing_date: date
    employee_count: int
    source: str
