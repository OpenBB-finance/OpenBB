"""Choice feeds built from what the exchange lists right now."""


def _choices(values, labels: dict | None = None) -> list[dict[str, str]]:
    """Pair each value with a label for a widget parameter."""
    named = labels or {}

    return [{"label": named.get(value, value), "value": value} for value in values]


async def currency_choices() -> list[dict[str, str]]:
    """Return every currency the exchange lists."""
    from openbb_deribit.utils.helpers import get_currencies

    currencies = await get_currencies()

    return _choices(
        sorted(str(d["currency"]) for d in currencies),
        {
            str(d["currency"]): str(d.get("currency_long") or d["currency"])
            for d in currencies
        },
    )


async def index_choices(extended: bool = False) -> list[dict[str, str]]:
    """Return the name of every published index."""
    from openbb_deribit.utils.helpers import get_index_names

    names = await get_index_names(extended)

    return _choices(
        sorted(
            str(name["name"]) if isinstance(name, dict) else str(name) for name in names
        )
    )


async def instrument_choices(
    kind: str | None = None,
    currency: str = "any",
    expired: bool = False,
) -> list[dict[str, str]]:
    """Return every instrument of one kind, labelled by its name."""
    from openbb_deribit.utils.helpers import get_instruments

    instruments = await get_instruments(currency, kind, expired)

    return _choices(sorted(str(d["instrument_name"]) for d in instruments))


async def perpetual_choices() -> list[dict[str, str]]:
    """Return every perpetual, labelled by its instrument name."""
    from openbb_deribit.utils.helpers import get_perpetual_symbols

    perpetuals = await get_perpetual_symbols()

    return [{"label": name, "value": name} for name in sorted(perpetuals.values())]


async def options_root_choices() -> list[dict[str, str]]:
    """Return every underlying with listed options."""
    from openbb_deribit.utils.helpers import get_options_roots

    return _choices(await get_options_roots())


async def futures_root_choices() -> list[dict[str, str]]:
    """Return every underlying with a listed futures curve."""
    from openbb_deribit.utils.helpers import get_futures_roots

    return _choices(await get_futures_roots())


async def mark_price_choices() -> list[dict[str, str]]:
    """Return the options whose mark price the exchange keeps a history of.

    The exchange keeps that history only for the contracts its volatility
    indexes are built from, which are the two expirations bracketing thirty
    days on BTC and ETH. Every other instrument returns an empty series, so
    offering the whole option universe here would be offering mostly dead ends.

    Returns
    -------
    list[dict[str, str]]
        Each contract, labelled by its instrument name.
    """
    import asyncio

    from openbb_deribit.utils.helpers import get_volatility_index_options

    listings = await asyncio.gather(
        *(get_volatility_index_options(currency) for currency in ("BTC", "ETH")),
        return_exceptions=True,
    )

    return _choices(
        sorted(
            str(contract["instrument_name"])
            for listing in listings
            if isinstance(listing, list)
            for contract in listing
        )
    )


async def combo_choices(
    currency: str = "BTC", state: str | None = None
) -> list[dict[str, str]]:
    """Return the identifier of every combo listed on one currency."""
    from openbb_deribit.utils.client import request
    from openbb_deribit.utils.helpers import normalize_currency

    combos = await request(
        "get_combo_ids", {"currency": normalize_currency(currency), "state": state}
    )

    return _choices(sorted(str(combo) for combo in combos))
