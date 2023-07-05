"""Stock owner data model."""


from datetime import (
    date as dateType,
    datetime,
)

from pydantic import validator

from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


def most_recent_quarter(base: dateType = dateType.today()) -> dateType:
    """Get the most recent quarter date.

    Parameter
    ---------
    base : date
        The date to get the most recent quarter.

    Returns
    -------
    date : date
        The most recent quarter date.
    """

    base = min(base, dateType.today())  # This prevents dates from being in the future
    exacts = [(3, 31), (6, 30), (9, 30), (12, 31)]
    for exact in exacts:
        if base.month == exact[0] and base.day == exact[1]:
            return base
    if base.month < 4:
        return dateType(base.year - 1, 12, 31)
    if base.month < 7:
        return dateType(base.year, 3, 31)
    if base.month < 10:
        return dateType(base.year, 6, 30)
    return dateType(base.year, 9, 30)


class StockOwnershipQueryParams(QueryParams, BaseSymbol):
    """Stock ownership query.


    Parameter
    ---------
    symbol : string
        The symbol of the company.
    page : int
        The page number to get
    date : date
        The CIK of the company owner.
    """

    page: int = 0
    date: dateType = most_recent_quarter()

    @validator("date", pre=True)
    def time_validate(cls, v: str):  # pylint: disable=E0213
        base = datetime.strptime(v, "%Y-%m-%d").date()
        return most_recent_quarter(base)


class StockOwnershipData(Data):
    """Stock ownership data.

    Returns
    -------
    date : date
        The date of the stock ownership.
    cik : int
        The cik of the stock ownership.
    filingDate : date
        The filing date of the stock ownership.
    investorName : str
        The investor name of the stock ownership.
    symbol : str
        The symbol of the stock ownership.
    securityName : str
        The security name of the stock ownership.
    typeOfSecurity : str
        The type of security of the stock ownership.
    securityCusip : str
        The security cusip of the stock ownership.
    sharesType : str
        The shares type of the stock ownership.
    putCallShare : str
        The put call share of the stock ownership.
    investmentDiscretion : str
        The investment discretion of the stock ownership.
    industryTitle : str
        The industry title of the stock ownership.
    weight : float
        The weight of the stock ownership.
    lastWeight : float
        The last weight of the stock ownership.
    changeInWeight : float
        The change in weight of the stock ownership.
    changeInWeightPercentage : float
        The change in weight percentage of the stock ownership.
    marketValue : int
        The market value of the stock ownership.
    lastMarketValue : int
        The last market value of the stock ownership.
    changeInMarketValue : int
        The change in market value of the stock ownership.
    changeInMarketValuePercentage : float
        The change in market value percentage of the stock ownership.
    sharesNumber : int
        The shares number of the stock ownership.
    lastSharesNumber : int
        The last shares number of the stock ownership.
    changeInSharesNumber : float
        The change in shares number of the stock ownership.
    changeInSharesNumberPercentage : float
        The change in shares number percentage of the stock ownership.
    quarterEndPrice : float
        The quarter end price of the stock ownership.
    avgPricePaid : float
        The average price paid of the stock ownership.
    isNew : bool
        Is the stock ownership new.
    isSoldOut : bool
        Is the stock ownership sold out.
    ownership : float
        How much is the ownership.
    lastOwnership : float
        The last ownership amount.
    changeInOwnership : float
        The change in ownership amount.
    changeInOwnershipPercentage : float
        The change in ownership percentage.
    holdingPeriod : int
        The holding period of the stock ownership.
    firstAdded : date
        The first added date of the stock ownership.
    performance : float
        The performance of the stock ownership.
    performancePercentage : float
        The performance percentage of the stock ownership.
    lastPerformance : float
        The last performance of the stock ownership.
    changeInPerformance : float
        The change in performance of the stock ownership.
    isCountedForPerformance : bool
        Is the stock ownership counted for performance.
    """

    date: dateType
    cik: int
    filingDate: dateType
    investorName: str
    symbol: str
    securityName: str
    typeOfSecurity: str
    securityCusip: str
    sharesType: str
    putCallShare: str
    investmentDiscretion: str
    industryTitle: str
    weight: float
    lastWeight: float
    changeInWeight: float
    changeInWeightPercentage: float
    marketValue: int
    lastMarketValue: int
    changeInMarketValue: int
    changeInMarketValuePercentage: float
    sharesNumber: int
    lastSharesNumber: int
    changeInSharesNumber: float
    changeInSharesNumberPercentage: float
    quarterEndPrice: float
    avgPricePaid: float
    isNew: bool
    isSoldOut: bool
    ownership: float
    lastOwnership: float
    changeInOwnership: float
    changeInOwnershipPercentage: float
    holdingPeriod: int
    firstAdded: dateType
    performance: float
    performancePercentage: float
    lastPerformance: float
    changeInPerformance: float
    isCountedForPerformance: bool
