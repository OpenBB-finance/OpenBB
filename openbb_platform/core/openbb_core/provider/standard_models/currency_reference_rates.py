"""Currency Reference Rates Model."""

from datetime import (
    date as dateType,
)
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CurrencyReferenceRatesQueryParams(QueryParams):
    """Currency Reference Rates Query."""


class CurrencyReferenceRatesData(Data):
    """Currency Reference Rates Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    EUR: Optional[float] = Field(description="Euro.", default=None)
    USD: Optional[float] = Field(description="US Dollar.", default=None)
    JPY: Optional[float] = Field(description="Japanese Yen.", default=None)
    BGN: Optional[float] = Field(description="Bulgarian Lev.", default=None)
    CZK: Optional[float] = Field(description="Czech Koruna.", default=None)
    DKK: Optional[float] = Field(description="Danish Krone.", default=None)
    GBP: Optional[float] = Field(description="Pound Sterling.", default=None)
    HUF: Optional[float] = Field(description="Hungarian Forint.", default=None)
    PLN: Optional[float] = Field(description="Polish Zloty.", default=None)
    RON: Optional[float] = Field(description="Romanian Leu.", default=None)
    SEK: Optional[float] = Field(description="Swedish Krona.", default=None)
    CHF: Optional[float] = Field(description="Swiss Franc.", default=None)
    ISK: Optional[float] = Field(description="Icelandic Krona.", default=None)
    NOK: Optional[float] = Field(description="Norwegian Krone.", default=None)
    TRY: Optional[float] = Field(description="Turkish Lira.", default=None)
    AUD: Optional[float] = Field(description="Australian Dollar.", default=None)
    BRL: Optional[float] = Field(description="Brazilian Real.", default=None)
    CAD: Optional[float] = Field(description="Canadian Dollar.", default=None)
    CNY: Optional[float] = Field(description="Chinese Yuan.", default=None)
    HKD: Optional[float] = Field(description="Hong Kong Dollar.", default=None)
    IDR: Optional[float] = Field(description="Indonesian Rupiah.", default=None)
    ILS: Optional[float] = Field(description="Israeli Shekel.", default=None)
    INR: Optional[float] = Field(description="Indian Rupee.", default=None)
    KRW: Optional[float] = Field(description="South Korean Won.", default=None)
    MXN: Optional[float] = Field(description="Mexican Peso.", default=None)
    MYR: Optional[float] = Field(description="Malaysian Ringgit.", default=None)
    NZD: Optional[float] = Field(description="New Zealand Dollar.", default=None)
    PHP: Optional[float] = Field(description="Philippine Peso.", default=None)
    SGD: Optional[float] = Field(description="Singapore Dollar.", default=None)
    THB: Optional[float] = Field(description="Thai Baht.", default=None)
    ZAR: Optional[float] = Field(description="South African Rand.", default=None)
