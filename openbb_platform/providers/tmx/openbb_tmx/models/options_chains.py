"""TMX Options Chains Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class TmxOptionsChainsQueryParams(OptionsChainsQueryParams):
    """TMX Options Chains Query."""

    date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("date", ""),
        default=None,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxOptionsChainsData(OptionsChainsData):
    """TMX Options Chains Data."""

    __doc__ = OptionsChainsData.__doc__

    transactions: list[int | None] = Field(
        default_factory=list, description="Number of transactions for the contract."
    )
    total_value: list[float | None] = Field(
        default_factory=list,
        description="Total value of the transactions.",
    )
    settlement_price: list[float | None] = Field(
        default_factory=list,
        description="Settlement price on that date.",
    )

    @field_validator("expiration", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return the datetime object from the date string."""
        return [
            datetime.strptime(d, "%Y-%m-%d") if isinstance(d, str) else d for d in v
        ]


TICK_MAP = {1: "up", -1: "down", 0: "unchanged"}


def _flatten_chain(results: dict, symbol: str) -> dict:
    """Flatten a QuoteMedia option chain into columnar lists.

    Parameters
    ----------
    results : dict
        The chain results as QuoteMedia returns them.
    symbol : str
        The underlying symbol.

    Returns
    -------
    dict
        One list per field, aligned across contracts.
    """
    from math import isnan

    from pandas import DataFrame
    from pytz import timezone

    rows: list[dict] = []

    for group in results.get("expiryGroup", []):
        for pair in group.get("callputgroup", []):
            for quote in pair.get("quote", []):
                contract = quote.get("contract", {})
                price = quote.get("pricedata", {})
                greeks = quote.get("greeks", {})
                key = quote.get("key", {}).get("symbol", [])
                expiration = contract.get("expirydate")

                if not expiration:
                    continue

                rows.append(
                    {
                        "underlying_symbol": f"{symbol}:CA",
                        "contract_symbol": (
                            key[0] if key else quote.get("symbolstring")
                        ),
                        "expiration": expiration,
                        "strike": contract.get("strike"),
                        "option_type": str(contract.get("callput", "")).lower(),
                        "contract_type": contract.get("type"),
                        "open_interest": contract.get("openinterest"),
                        "contract_high": contract.get("contracthigh"),
                        "contract_low": contract.get("contractlow"),
                        "volume": price.get("contractvolume"),
                        "last_trade_price": price.get("last"),
                        "last_trade_time": price.get("lasttradedatetime"),
                        "last_quote_time": price.get("lastquotedatetime"),
                        "prev_close": price.get("prevclose"),
                        "change": price.get("change"),
                        "change_percent": price.get("changepercent"),
                        "open": price.get("open"),
                        "high": price.get("high"),
                        "low": price.get("low"),
                        "bid": price.get("bid"),
                        "bid_size": price.get("bidsize"),
                        "ask": price.get("ask"),
                        "ask_size": price.get("asksize"),
                        "tick": TICK_MAP.get(price.get("tick")),
                        "implied_volatility": greeks.get("impvol"),
                        "delta": greeks.get("delta"),
                        "gamma": greeks.get("gamma"),
                        "theta": greeks.get("theta"),
                        "vega": greeks.get("vega"),
                        "rho": greeks.get("rho"),
                    }
                )

    if not rows:
        return {}

    from pandas import to_datetime

    frame = DataFrame(rows).sort_values(["expiration", "strike", "option_type"])
    today = to_datetime(datetime.now(tz=timezone("America/New_York")).date())
    frame["dte"] = (to_datetime(frame["expiration"]) - today).dt.days
    flattened = frame.reset_index(drop=True).to_dict(orient="list")

    return {
        field: [None if isinstance(v, float) and isnan(v) else v for v in values]
        for field, values in flattened.items()
    }


class TmxOptionsChainsFetcher(
    Fetcher[
        TmxOptionsChainsQueryParams,
        TmxOptionsChainsData,
    ]
):
    """TMX Options Chains Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxOptionsChainsQueryParams:
        """Transform the query."""
        return TmxOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxOptionsChainsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the data."""
        from openbb_tmx.models.equity_quote import TmxEquityQuoteFetcher
        from openbb_tmx.utils.helpers import download_eod_chains, normalize_symbol
        from openbb_tmx.utils.quotemedia import get_option_chain

        symbol = normalize_symbol(query.symbol)

        if query.date is not None:
            chains = await download_eod_chains(
                symbol=query.symbol, date=query.date, use_cache=query.use_cache
            )

            return chains.to_dict(orient="list") if not chains.empty else {}

        results = await get_option_chain(symbol, use_cache=query.use_cache)
        flattened = _flatten_chain(results, symbol)

        if not flattened:
            return {}

        underlying_quote = await TmxEquityQuoteFetcher.fetch_data(
            {"symbol": query.symbol}, credentials
        )
        quotes = list(underlying_quote or [])
        underlying_price = getattr(quotes[0], "last_price", None) if quotes else None

        if underlying_price is not None:
            count = len(flattened["contract_symbol"])
            flattened["underlying_price"] = [underlying_price] * count

        return flattened

    @staticmethod
    def transform_data(
        query: TmxOptionsChainsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> TmxOptionsChainsData:
        """Transform the data and validate the model."""
        return TmxOptionsChainsData.model_validate(data)
