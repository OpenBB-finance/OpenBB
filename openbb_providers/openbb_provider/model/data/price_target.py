"""Price target data model."""

# IMPORT STANDARD
from datetime import datetime
from typing import Optional

# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class PriceTargetQueryParams(QueryParams, BaseSymbol):
    """Price Target query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "PriceTargetQueryParams"


class PriceTargetData(Data, BaseSymbol):
    """Price target data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    published_date : datetime
        The published date of the price target.
    news_url : str
        The news URL of the price target.
    news_title : str
        The news title of the price target.
    analyst_name : str
        The analyst name of the price target.
    price_target : float
        The price target of the price target.
    adj_price_target : float
        The adjusted price target of the price target.
    price_when_posted : float
        The price when posted of the price target.
    news_publisher : str
        The news publisher of the price target.
    news_base_url : str
        The news base URL of the price target.
    analyst_company : str
        The analyst company of the price target.
    """

    symbol: str
    published_date: datetime
    news_url: str
    news_title: Optional[str]
    analyst_name: Optional[str]
    price_target: float
    adj_price_target: float
    price_when_posted: float
    news_publisher: str
    news_base_url: str
    analyst_company: str
