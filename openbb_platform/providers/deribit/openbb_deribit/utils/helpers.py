"""Deribit Helpers Module."""

from typing import Literal, Optional

from async_lru import alru_cache
from openbb_core.app.model.abstract.error import OpenBBError

DERIBIT_OPTIONS_SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "BNB", "PAXG"]
OptionsSymbols = Literal["BTC", "ETH", "SOL", "XRP", "BNB", "PAXG"]
CURRENCIES = ["BTC", "ETH", "USDC", "USDT", "EURR", "all"]
Currencies = Literal["BTC", "ETH", "USDC", "USDT", "EURR", "all"]
DERIVATIVE_TYPES = ["future", "option", "spot", "future_combo", "option_combo"]
DerivativeTypes = Literal["future", "option", "spot", "future_combo", "option_combo"]
BASE_URL = "https://www.deribit.com"


@alru_cache(maxsize=64)
async def get_instruments(
    currency: Currencies = "BTC",
    derivative_type: Optional[DerivativeTypes] = None,
) -> list[dict]:
    """
    Get Deribit instruments.

    Parameters
    ----------
    currency : Currencies
        The currency to get instruments for. Default is "BTC".
    derivative_type : Optional[DerivativeTypes]
        The type of derivative to get instruments for. Default is None, which gets all types.

    Returns
    -------
    list[dict]
        A list of instrument dictionaries.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    if currency != "all" and currency.upper() not in CURRENCIES:
        raise ValueError(
            f"Currency {currency} not supported. Supported currencies are: {', '.join(CURRENCIES)}"
        )
    if derivative_type and derivative_type not in DERIVATIVE_TYPES:
        raise ValueError(
            f"Kind {derivative_type} not supported. Supported kinds are: {', '.join(DERIVATIVE_TYPES)}"
        )

    url = f"{BASE_URL}/api/v2/public/get_instruments?currency={currency.upper() if currency != 'all' else 'any'}"

    if derivative_type is not None:
        url += f"&kind={derivative_type}"

    try:
        response = await amake_request(url)
        return response.get("result", [])  # type: ignore
    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(f"Failed to get instruments -> {e.__class__.__name__}: {e}")


async def get_options_symbols(symbol: OptionsSymbols = "BTC") -> dict[str, str]:
    """
    Get a dictionary of contract symbols by expiry.

    Parameters
    ----------
    symbol : OptionsSymbols
        The underlying symbol to get options for. Default is "BTC".

    Returns
    -------
    dict[str, str]
        A dictionary of contract symbols by expiry date.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import to_datetime

    if symbol.upper() not in DERIBIT_OPTIONS_SYMBOLS:
        raise ValueError(
            f"Invalid Deribit symbol. Supported symbols are: {', '.join(DERIBIT_OPTIONS_SYMBOLS)}",
        )

    currency = (
        "USDC" if symbol.upper() in ["BNB", "PAXG", "SOL", "XRP"] else symbol.upper()
    )
    instruments = await get_instruments(currency, "option")
    expirations: dict = {}
    all_options = list(
        set(
            [
                d.get("instrument_name")
                for d in instruments
                if d.get("instrument_name").startswith(symbol)
                and d.get("instrument_name").endswith(("-C", "-P"))
            ]
        )
    )
    for item in sorted(
        list(
            set(
                [
                    (
                        to_datetime(d.split("-")[1]).date().strftime("%Y-%m-%d"),
                        d.split("-")[1],
                    )
                    for d in all_options
                ]
            )
        )
    ):
        expirations[item[0]] = item[1]

    return {
        expiration: [str(d) for d in all_options if expirations[expiration] in d]
        for expiration in expirations
    }
