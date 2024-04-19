"""Tradier Equity Quote Model."""

# pylint: disable = unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from dateutil.parser import parse
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request, safe_fromtimestamp
from openbb_tradier.utils.constants import OPTIONS_EXCHANGES, STOCK_EXCHANGES
from pydantic import Field, field_validator, model_validator
from pytz import timezone


class TradierEquityQuoteQueryParams(EquityQuoteQueryParams):
    """Tradier Equity Quote Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class TradierEquityQuoteData(EquityQuoteData):
    """Tradier Equity Quote Data."""

    __alias_dict__ = {
        "name": "description",
        "exchange": "exch",
        "asset_type": "type",
        "bid_exchange": "bidexch",
        "bid_size": "bidsize",
        "ask_size": "asksize",
        "ask_exchange": "askexch",
        "last_price": "last",
        "last_timestamp": "trade_date",
        "prev_close": "prevclose",
        "year_high": "week_52_high",
        "year_low": "week_52_low",
        "volume_avg": "average_volume",
        "change_percent": "change_percentage",
        "root_symbol": "root_symbols",
        "orats_final_iv": "smv_vol",
        "greeks_timestamp": "updated_at",
        "bid_timestamp": "bid_date",
        "ask_timestamp": "ask_date",
    }

    last_volume: Optional[int] = Field(
        default=None,
        description="The last trade volume.",
    )
    volume_avg: Optional[int] = Field(
        default=None,
        description="The average daily trading volume.",
    )
    bid_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the bid price.",
    )
    ask_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the ask price.",
    )
    greeks_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the greeks data.",
    )
    underlying: Optional[str] = Field(
        default=None,
        description="The underlying symbol for the option.",
    )
    root_symbol: Optional[str] = Field(
        default=None,
        description="The root symbol for the option.",
    )
    option_type: Optional[Literal["call", "put"]] = Field(
        default=None,
        description="Type of option - call or put.",
    )
    contract_size: Optional[int] = Field(
        default=None,
        description="The number of shares in a standard contract.",
    )
    expiration_type: Optional[str] = Field(
        default=None,
        description="The expiration type of the option - i.e, standard, weekly, etc.",
    )
    expiration_date: Optional[dateType] = Field(
        default=None,
        description="The expiration date of the option.",
    )
    strike: Optional[float] = Field(
        default=None,
        description="The strike price of the option.",
    )
    open_interest: Optional[int] = Field(
        default=None,
        description="The number of open contracts for the option.",
    )
    bid_iv: Optional[float] = Field(
        default=None,
        description="Implied volatility of the bid price.",
    )
    ask_iv: Optional[float] = Field(
        default=None,
        description="Implied volatility of the ask price.",
    )
    mid_iv: Optional[float] = Field(
        default=None,
        description="Mid-point implied volatility of the option.",
    )
    orats_final_iv: Optional[float] = Field(
        default=None,
        description="ORATS final implied volatility of the option.",
    )
    delta: Optional[float] = Field(
        default=None,
        description="Delta of the option.",
    )
    gamma: Optional[float] = Field(
        default=None,
        description="Gamma of the option.",
    )
    theta: Optional[float] = Field(
        default=None,
        description="Theta of the option.",
    )
    vega: Optional[float] = Field(
        default=None,
        description="Vega of the option.",
    )
    rho: Optional[float] = Field(
        default=None,
        description="Rho of the option.",
    )
    phi: Optional[float] = Field(
        default=None,
        description="Phi of the option.",
    )

    @field_validator(
        "last_timestamp",
        "ask_timestamp",
        "bid_timestamp",
        "greeks_timestamp",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_dates(cls, v):
        """Validate the dates."""
        if v != 0 and v is not None and isinstance(v, int):
            v = int(v) / 1000  # milliseconds to seconds
            v = safe_fromtimestamp(v)
            v = v.replace(microsecond=0)
            v = v.astimezone(timezone("America/New_York"))
            return v
        if v is not None and isinstance(v, str):
            v = parse(v)
            v = v.replace(microsecond=0, tzinfo=timezone("UTC"))
            v = v.astimezone(timezone("America/New_York"))
            return v
        return None

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percentage."""
        return float(v) / 100 if v else None

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if (v == 0 or str(v) == "0") else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class TradierEquityQuoteFetcher(
    Fetcher[TradierEquityQuoteQueryParams, List[TradierEquityQuoteData]]
):
    """Tradier Equity Quote Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TradierEquityQuoteQueryParams:
        """Transform the query."""
        return TradierEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TradierEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tradier endpoint."""
        api_key = credentials.get("tradier_api_key") if credentials else ""
        sandbox = True

        if api_key and credentials.get("tradier_account_type") not in ["sandbox", "live"]:  # type: ignore
            raise ValueError(
                "Invalid account type for Tradier. Must be either 'sandbox' or 'live'."
            )

        if api_key:
            sandbox = (
                credentials.get("tradier_account_type") == "sandbox"
                if credentials
                else False
            )

        BASE_URL = (
            "https://api.tradier.com/"
            if sandbox is False
            else "https://sandbox.tradier.com/"
        )
        HEADERS = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        url = f"{BASE_URL}v1/markets/quotes?symbols={query.symbol}&greeks=true"

        response = await amake_request(url, headers=HEADERS)

        if response.get("quotes"):  # type: ignore
            data = response["quotes"].get("quote")  # type: ignore
            if len(data) > 0:
                return data if isinstance(data, list) else [data]

        raise EmptyDataError("No results found.")

    @staticmethod
    def transform_data(
        query: TradierEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TradierEquityQuoteData]:
        """Transform and validate the data."""
        results: List[TradierEquityQuoteData] = []

        for d in data:

            d["exch"] = (
                OPTIONS_EXCHANGES.get(d["exch"])
                if d.get("type") in ["option", "index"]
                else STOCK_EXCHANGES.get(d["exch"])
            )
            d["askexch"] = (
                OPTIONS_EXCHANGES.get(d["askexch"])
                if d.get("type") in ["option", "index"]
                else STOCK_EXCHANGES.get(d["askexch"])
            )
            d["bidexch"] = (
                OPTIONS_EXCHANGES.get(d["bidexch"])
                if d.get("type") in ["option", "index"]
                else STOCK_EXCHANGES.get(d["bidexch"])
            )

            if "greeks" in d:
                # Flatten the nested greeks dictionary
                greeks = d.pop("greeks")
                if greeks is not None:
                    d.update(**greeks)

            if (
                d.get("root_symbols") == d.get("symbol")
                and d.get("root_symbols") is not None
            ):
                _ = d.pop("root_symbols")

            if (
                d.get("root_symbol") == d.get("underlying")
                and d.get("root_symbol") is not None
            ):
                _ = d.pop("root_symbol")

            results.append(TradierEquityQuoteData.model_validate(d))

        return results
