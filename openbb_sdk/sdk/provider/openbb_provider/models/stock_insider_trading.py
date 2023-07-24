"""Stock insider trading data model."""


from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from openbb_provider.abstract.data import Data, QueryParams


class TransactionTypes(str, Enum):
    Award = "A-Award"
    Conversion = "C-Conversion"
    Return = "D-Return"
    ExpireShort = "E-ExpireShort"
    InKind = "F-InKind"
    Gift = "G-Gift"
    ExpireLong = "H-ExpireLong"
    Discretionary = "I-Discretionary"
    Other = "J-Other"
    Small = "L-Small"
    Exempt = "M-Exempt"
    OutOfTheMoney = "O-OutOfTheMoney"
    Purchase = "P-Purchase"
    Sale = "S-Sale"
    Tender = "U-Tender"
    Will = "W-Will"
    InTheMoney = "X-InTheMoney"
    Trust = "Z-Trust"


class StockInsiderTradingQueryParams(QueryParams):
    """Stock Insider Trading query.


    Parameter
    ---------
    transactionType : List[TransactionTypes]
        The type of the transaction. Possible values are:
        A-Award, C-Conversion, D-Return, E-ExpireShort, F-InKind, G-Gift, H-ExpireLong
        I-Discretionary, J-Other, L-Small, M-Exempt, O-OutOfTheMoneym P-Purchase
        S-Sale, U-Tender, W-Will, X-InTheMoney, Z-Trust
    symbol : str]
        The symbol of the company.
    reportingCik : int]
        The CIK of the reporting owner.
    companyCik : int]
        The CIK of the company owner.
    page: int
        The page number to get
    """

    transactionType: List[TransactionTypes] = []
    symbol: Optional[str]
    reportingCik: Optional[int]
    companyCik: Optional[int]
    page: int = 0


class StockInsiderTradingData(Data):
    """Stock insider trading data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    filingDate : datetime
        The filing date of the stock insider trading.
    transactionDate : date
        The transaction date of the stock insider trading.
    reportingCik : int
        The reporting CIK of the stock insider trading.
    transactionType : str
        The transaction type of the stock insider trading.
    securitiesOwned : int
        The securities owned of the stock insider trading.
    companyCik : int
        The company CIK of the stock insider trading.
    reportingName : str
        The reporting name of the stock insider trading.
    typeOfOwner : str
        The type of owner of the stock insider trading.
    acquistionOrDisposition : str
        The acquistion or disposition of the stock insider trading.
    formType : str
        The form type of the stock insider trading.
    securitiesTransacted : float
        The securities transacted of the stock insider trading.
    price : float
        The price of the stock insider trading.
    securityName : str
        The security name of the stock insider trading.
    link : str
        The link of the stock insider trading.
    """

    symbol: str
    filing_date: datetime
    transaction_date: date
    reporting_cik: int
    transaction_type: str
    securities_owned: int
    company_cik: int
    reporting_name: str
    type_of_owner: str
    acquistion_or_disposition: str
    form_type: str
    securities_transacted: float
    price: float
    security_name: str
    link: str
