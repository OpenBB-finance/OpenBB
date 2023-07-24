"""Company Overview Data Model."""


from datetime import date
from typing import Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol


class CompanyOverviewQueryParams(QueryParams, BaseSymbol):
    """Company overview query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class CompanyOverviewData(Data):
    """Company Overview data.

    Returns
    -------
    symbol : str
        The symbol of the company.
    price : float
        The price of the company.
    beta : float
        The beta of the company.
    vol_avg : int
        The volume average of the company.
    mkt_cap : int
        The market capitalization of the company.
    last_div : float
        The last dividend of the company.
    range : str
        The range of the company.
    changes : float
        The changes of the company.
    company_name : str
        The company name of the company.
    currency : str
        The currency of the company.
    cik : Optional[str]
        The CIK of the company.
    isin : Optional[str]
        The ISIN of the company.
    cusip : Optional[str]
        The CUSIP of the company.
    exchange : str
        The exchange of the company.
    exchange_short_name : str
        The exchange short name of the company.
    industry : str
        The industry of the company.
    website : str
        The website of the company.
    description : str
        The description of the company.
    ceo : str
        The CEO of the company.
    sector : str
        The sector of the company.
    country : str
        The country of the company.
    full_time_employees : str
        The full time employees of the company.
    phone : str
        The phone of the company.
    address : str
        The address of the company.
    city : str
        The city of the company.
    state : str
        The state of the company.
    zip : str
        The zip of the company.
    dcf_diff : float
        The discounted cash flow difference of the company.
    dcf : float
        The discounted cash flow of the company.
    image : str
        The image of the company.
    ipo_date : date
        The IPO date of the company.
    default_image : bool
        If the image is the default image.
    is_etf : bool
        If the company is an ETF.
    is_actively_trading : bool
        If the company is actively trading.
    is_adr : bool
        If the company is an ADR.
    is_fund : bool
        If the company is a fund.
    """

    symbol: str
    price: float
    beta: float
    vol_avg: int
    mkt_cap: int
    last_div: float
    range: str
    changes: float
    company_name: str
    currency: str
    cik: Optional[str]
    isin: Optional[str]
    cusip: Optional[str]
    exchange: str
    exchange_short_name: str
    industry: str
    website: str
    description: str
    ceo: str
    sector: str
    country: str
    full_time_employees: str
    phone: str
    address: str
    city: str
    state: str
    zip: str
    dcf_diff: float
    dcf: float
    image: str
    ipo_date: date
    default_image: bool
    is_etf: bool
    is_actively_trading: bool
    is_adr: bool
    is_fund: bool
