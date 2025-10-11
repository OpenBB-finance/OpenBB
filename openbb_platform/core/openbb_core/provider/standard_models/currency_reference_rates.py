"""Currency Reference Rates Model."""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CurrencyReferenceRatesQueryParams(QueryParams):
    """Currency Reference Rates Query."""


class CurrencyReferenceRatesData(Data):
    """Currency Reference Rates Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    EUR: float | None = Field(description="Euro.", default=None)
    USD: float | None = Field(description="US Dollar.", default=None)
    JPY: float | None = Field(description="Japanese Yen.", default=None)
    BGN: float | None = Field(description="Bulgarian Lev.", default=None)
    CZK: float | None = Field(description="Czech Koruna.", default=None)
    DKK: float | None = Field(description="Danish Krone.", default=None)
    GBP: float | None = Field(description="Pound Sterling.", default=None)
    HUF: float | None = Field(description="Hungarian Forint.", default=None)
    PLN: float | None = Field(description="Polish Zloty.", default=None)
    RON: float | None = Field(description="Romanian Leu.", default=None)
    SEK: float | None = Field(description="Swedish Krona.", default=None)
    CHF: float | None = Field(description="Swiss Franc.", default=None)
    ISK: float | None = Field(description="Icelandic Krona.", default=None)
    NOK: float | None = Field(description="Norwegian Krone.", default=None)
    TRY: float | None = Field(description="Turkish Lira.", default=None)
    AUD: float | None = Field(description="Australian Dollar.", default=None)
    BRL: float | None = Field(description="Brazilian Real.", default=None)
    CAD: float | None = Field(description="Canadian Dollar.", default=None)
    CNY: float | None = Field(description="Chinese Yuan.", default=None)
    HKD: float | None = Field(description="Hong Kong Dollar.", default=None)
    IDR: float | None = Field(description="Indonesian Rupiah.", default=None)
    ILS: float | None = Field(description="Israeli Shekel.", default=None)
    INR: float | None = Field(description="Indian Rupee.", default=None)
    KRW: float | None = Field(description="South Korean Won.", default=None)
    MXN: float | None = Field(description="Mexican Peso.", default=None)
    MYR: float | None = Field(description="Malaysian Ringgit.", default=None)
    NZD: float | None = Field(description="New Zealand Dollar.", default=None)
    PHP: float | None = Field(description="Philippine Peso.", default=None)
    SGD: float | None = Field(description="Singapore Dollar.", default=None)
    THB: float | None = Field(description="Thai Baht.", default=None)
    ZAR: float | None = Field(description="South African Rand.", default=None)
