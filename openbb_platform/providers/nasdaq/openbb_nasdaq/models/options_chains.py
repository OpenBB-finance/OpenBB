"""Nasdaq Options Chains Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT

EXCHANGES = Literal[
    "composite",
    "cbo",
    "aoe",
    "nyo",
    "pho",
    "moe",
    "box",
    "ise",
    "bto",
    "nso",
    "c2o",
    "bxo",
    "mio",
    "mpe",
    "edo",
    "gem",
    "mcry",
    "mxop",
]

# Nasdaq serves contract detail one strike at a time. Measured against the live
# API: 64 simultaneous requests sustain ~22 strikes/second with no refusals,
# ~128 has roughly half refused, and beyond that the caller is blocked outright.
# Failed strikes are retried with backoff so throughput never costs completeness.
_MAX_CONCURRENCY = 64
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF = 0.5

EXCHANGE_MAP = {
    "composite": "oprac",
    "cbo": "cbo",
    "aoe": "aoe",
    "nyo": "nyo",
    "pho": "pho",
    "moe": "moe",
    "box": "box",
    "ise": "ise",
    "bto": "bto",
    "nso": "nso",
    "c2o": "c2o",
    "bxo": "bxo",
    "mio": "mio",
    "mpe": "mpe",
    "edo": "edo",
    "gem": "gem",
    "mcry": "mcry",
    "mxop": "mxop",
}


class NasdaqOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Nasdaq Options Chains Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
        "exchange": {"choices": list(EXCHANGE_MAP)},
        "expiration": {"multiple_items_allowed": True},
    }

    exchange: EXCHANGES = Field(
        default="composite",
        description="The options exchange. 'composite' is the consolidated chain.",
    )
    expiration: str | None = Field(
        default=None,
        description="Restrict the chain to one or more comma-separated expiration"
        + " dates. Every expiration is returned when unset.",
    )


class NasdaqOptionsChainsData(OptionsChainsData):
    """Nasdaq Options Chains Data."""

    __doc__ = OptionsChainsData.__doc__


class NasdaqOptionsChainsFetcher(
    Fetcher[
        NasdaqOptionsChainsQueryParams,
        NasdaqOptionsChainsData,
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqOptionsChainsQueryParams:
        """Transform the query."""
        return NasdaqOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqOptionsChainsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Nasdaq endpoint.

        The chain endpoint carries last/change/bid/ask/volume/open-interest for
        every contract in range, in one request. Nasdaq has no bulk endpoint for
        anything else: full quote detail - open, high, low, previous close,
        sizes, contract high/low, tick, and market - costs one request per
        contract, and the greeks cost one request per expiration (Nasdaq's own
        greeks endpoint accepts a single ``date``). Both are therefore fanned
        out only for the requested expirations, or the nearest one when none is
        requested, rather than for the whole chain.

        Raises
        ------
        EmptyDataError
            If Nasdaq publishes no chain for the symbol.
        """
        import asyncio
        from datetime import date, timedelta

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import (
            get_contract_detail,
            get_nasdaq_data,
            resolve_asset_class,
            to_date,
        )

        symbol = query.symbol.upper()
        asset_class = await resolve_asset_class(symbol)
        excode = EXCHANGE_MAP[query.exchange]
        today = date.today()
        requested = {
            d
            for d in (
                to_date(part) for part in (query.expiration or "").split(",") if part
            )
            if d is not None
        }
        chain_path = (
            f"quote/{symbol}/option-chain?assetclass={asset_class}"
            f"&fromdate={min(requested) if requested else today}"
            f"&todate={max(requested) if requested else today + timedelta(days=1095)}"
            f"&limit=20000&excode={excode}&callput=callput&money=all&type=all"
        )
        chain = await get_nasdaq_data(chain_path)

        if not chain:
            raise EmptyDataError(f"No options chain was found for {symbol}.")

        front = _front_expiration(chain)
        fanout = requested or ({front} if front is not None else set())
        detail: dict = {}
        semaphore = asyncio.Semaphore(_MAX_CONCURRENCY)

        async def get_one(expiration, strike) -> None:
            """Collect one strike's full detail, retrying on a refused request."""
            async with semaphore:
                for attempt in range(_MAX_ATTEMPTS):
                    try:
                        sides = await get_contract_detail(
                            symbol, expiration, strike, asset_class
                        )
                    except Exception:  # noqa: BLE001
                        await asyncio.sleep(_RETRY_BACKOFF * (attempt + 1))
                        continue

                    for side, fields in sides.items():
                        detail[(expiration, strike, side)] = fields

                    return

        async def get_greeks(expiration) -> Any:
            """Fetch one expiration's greeks table, tolerating a refusal."""
            try:
                return await get_nasdaq_data(
                    f"quote/{symbol}/option-chain/greeks?assetclass={asset_class}"
                    f"&date={expiration}"
                )
            except Exception:  # noqa: BLE001
                return {}

        detail_pairs = _strikes_for(chain, fanout) if fanout else []
        _, greeks_payloads = await asyncio.gather(
            asyncio.gather(
                *[get_one(expiration, strike) for expiration, strike in detail_pairs]
            ),
            asyncio.gather(*[get_greeks(expiration) for expiration in sorted(fanout)]),
        )
        greeks: dict = {}

        for payload in greeks_payloads:
            greeks.update(_greeks_by_contract(payload or {}))

        return {
            "symbol": symbol,
            "chain": chain,
            "greeks": greeks,
            "detail": detail,
            "expirations": requested,
        }

    @staticmethod
    def transform_data(
        query: NasdaqOptionsChainsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[NasdaqOptionsChainsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the chain carried no priced contracts.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_number

        chain = data["chain"] or {}
        symbol = data["symbol"]
        last_trade = chain.get("lastTrade") or ""
        underlying_price = _underlying_price(last_trade)
        greeks = data.get("greeks") or {}
        detail = data.get("detail") or {}
        wanted = data.get("expirations") or set()
        contracts: list[dict] = []

        for row in (chain.get("table") or {}).get("rows") or []:
            strike = to_number(row.get("strike"))

            if strike is None:
                continue

            for side, prefix in (("call", "c_"), ("put", "p_")):
                contract = _contract_symbol(row.get("drillDownURL"), side)
                expiration = _expiration(contract)

                if expiration is None or (wanted and expiration not in wanted):
                    continue

                record = {
                    "underlying_symbol": symbol,
                    "underlying_price": underlying_price,
                    "contract_symbol": contract,
                    "expiration": expiration,
                    "strike": strike,
                    "option_type": side,
                    "last_trade_price": to_number(row.get(f"{prefix}Last")),
                    "change": to_number(row.get(f"{prefix}Change")),
                    "bid": to_number(row.get(f"{prefix}Bid")),
                    "ask": to_number(row.get(f"{prefix}Ask")),
                    "volume": to_number(row.get(f"{prefix}Volume")),
                    "open_interest": to_number(row.get(f"{prefix}Openinterest")),
                }
                record.update(greeks.get((expiration, strike, side), {}))
                record.update(detail.get((expiration, strike, side), {}))
                contracts.append(record)

        if not contracts:
            raise EmptyDataError(f"No option contracts were returned for {symbol}.")

        contracts.sort(key=lambda c: (c["expiration"], c["strike"], c["option_type"]))
        frame: dict[str, list] = {}

        for contract in contracts:
            for key in (
                "underlying_symbol",
                "underlying_price",
                "contract_symbol",
                "expiration",
                "strike",
                "option_type",
                "last_trade_price",
                "change",
                "bid",
                "ask",
                "bid_size",
                "ask_size",
                "volume",
                "open_interest",
                "open",
                "high",
                "low",
                "prev_close",
                "contract_high",
                "contract_low",
                "tick",
                "exchange",
                "implied_volatility",
                "delta",
                "gamma",
                "theta",
                "vega",
                "rho",
            ):
                frame.setdefault(key, []).append(contract.get(key))

        return AnnotatedResult(
            result=NasdaqOptionsChainsData.model_validate(frame),
            metadata={"symbol": symbol, "underlying_price": underlying_price},
        )


def _underlying_price(last_trade: str) -> float | None:
    """Pull the underlying price out of the chain's lastTrade banner.

    Parameters
    ----------
    last_trade : str
        The banner text - i.e., "AAPL $333.02 +11.36 ...".

    Returns
    -------
    float | None
        The underlying price, when present.
    """
    import re

    match = re.search(r"\$([\d,]+\.?\d*)", last_trade or "")

    return float(match.group(1).replace(",", "")) if match else None


def _contract_symbol(url: Any, side: str) -> str | None:
    """Build the OCC contract symbol from a Nasdaq drill-down URL.

    Parameters
    ----------
    url : Any
        The ``drillDownURL`` value - i.e., '.../aapl--260727c00205000'.
    side : str
        Either 'call' or 'put'.

    Returns
    -------
    str | None
        The upper-cased contract symbol for the requested side.
    """
    if not isinstance(url, str) or "--" not in url:
        return None

    tail = url.rsplit("--", 1)[-1]
    root = url.rsplit("/", 1)[-1].split("--", 1)[0]

    if len(tail) < 15:
        return None

    return f"{root}{tail[:6]}{'C' if side == 'call' else 'P'}{tail[7:]}".upper()


def _expiration(contract: str | None):
    """Parse the expiration date out of an OCC contract symbol.

    Parameters
    ----------
    contract : str | None
        The OCC contract symbol.

    Returns
    -------
    date | None
        The expiration date, when parseable.
    """
    from datetime import datetime

    if not contract or len(contract) < 15:
        return None

    digits = "".join(c for c in contract if c.isdigit())

    if len(digits) < 6:
        return None

    try:
        return datetime.strptime(digits[:6], "%y%m%d").date()
    except ValueError:
        return None


def _front_expiration(chain: dict):
    """Return the nearest expiration present in a chain payload.

    Parameters
    ----------
    chain : dict
        The Nasdaq chain payload.

    Returns
    -------
    date | None
        The nearest expiration, or None when the chain has no parseable rows.
    """
    expirations = {
        _expiration(_contract_symbol(row.get("drillDownURL"), "call"))
        for row in (chain.get("table") or {}).get("rows") or []
    }
    parsed = {expiration for expiration in expirations if expiration is not None}

    return min(parsed) if parsed else None


def _greeks_by_contract(greeks: dict) -> dict:
    """Index the greeks table by expiration, strike, and side.

    Parameters
    ----------
    greeks : dict
        The Nasdaq greeks payload.

    Returns
    -------
    dict
        Mapping of (expiration, strike, side) to the greek fields.
    """
    from openbb_nasdaq.utils.helpers import to_number

    indexed: dict = {}

    for row in (greeks.get("table") or {}).get("rows") or []:
        strike = to_number(row.get("strike") or row.get("Strike"))

        if strike is None:
            continue

        for side, prefix in (("call", "c"), ("put", "p")):
            contract = _contract_symbol(row.get("url"), side)
            expiration = _expiration(contract)

            if expiration is None:
                continue

            indexed[(expiration, strike, side)] = {
                "delta": to_number(row.get(f"{prefix}Delta")),
                "gamma": to_number(row.get(f"{prefix}Gamma")),
                "theta": to_number(row.get(f"{prefix}Theta")),
                "vega": to_number(row.get(f"{prefix}Vega")),
                "rho": to_number(row.get(f"{prefix}Rho")),
                "implied_volatility": to_number(row.get(f"{prefix}IV")),
            }

    return indexed


def _strikes_for(chain: dict, expirations: set) -> list[tuple]:
    """List the (expiration, strike) pairs present in a chain.

    Parameters
    ----------
    chain : dict
        The Nasdaq chain payload.
    expirations : set
        The expiration dates to keep. Every expiration is kept when empty.

    Returns
    -------
    list[tuple]
        Unique (expiration, strike) pairs.
    """
    from openbb_nasdaq.utils.helpers import to_number

    pairs: set = set()

    for row in (chain.get("table") or {}).get("rows") or []:
        strike = to_number(row.get("strike"))

        if strike is None:
            continue

        expiration = _expiration(_contract_symbol(row.get("drillDownURL"), "call"))

        if expiration is not None and (not expirations or expiration in expirations):
            pairs.add((expiration, strike))

    return sorted(pairs)
