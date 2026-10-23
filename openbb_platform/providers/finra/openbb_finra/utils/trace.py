"""Query building for the public TRACE data service."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openbb_finra.utils.client import TraceSession


def is_cusip(value: str) -> bool:
    """Return whether a value is a CUSIP with a valid check digit.

    Parameters
    ----------
    value : str
        The candidate identifier.

    Returns
    -------
    bool
        True when the value is nine characters with a matching check digit.
    """
    text = value.strip().upper()

    if len(text) != 9 or not text.isalnum() or not text[8].isdigit():
        return False

    total = 0

    for position, character in enumerate(text[:8]):
        number = (
            int(character) if character.isdigit() else ord(character) - ord("A") + 10
        )

        if position % 2:
            number *= 2

        total += number // 10 + number % 10

    return (10 - total % 10) % 10 == int(text[8])


def match_filters(text: str, field: str) -> list[dict]:
    """Return the filters that match every word of a text within one field.

    Parameters
    ----------
    text : str
        The words to look for, in any order.
    field : str
        The TRACE field to search.

    Returns
    -------
    list[dict]
        One case-insensitive substring filter per word.
    """
    words = [
        word
        for word in text.replace("%", " ").replace("_", " ").split()
        if word.strip()
    ]

    return [
        {
            "searchValue": word,
            "fuzzy": False,
            "synonym": False,
            "fields": [{"name": field, "boost": 1}],
        }
        for word in words
    ]


async def resolve_bonds(trace: "TraceSession", identifiers: list[str]) -> list[dict]:
    """Return the TRACE bond-search record of each CUSIP or FINRA symbol.

    Parameters
    ----------
    trace : TraceSession
        The open TRACE session.
    identifiers : list[str]
        CUSIPs or FINRA bond symbols, upper-cased.

    Returns
    -------
    list[dict]
        The records found, with the cusip, symbol, issuer, and bond type.
    """
    import asyncio

    from openbb_finra.utils.constants import BOND_SEARCH_DATASET, BOND_SEARCH_FIELDS

    cusips = [value for value in identifiers if is_cusip(value)]
    symbols = [value for value in identifiers if not is_cusip(value)]
    queries = [
        trace.query(
            BOND_SEARCH_DATASET,
            {
                "fields": BOND_SEARCH_FIELDS,
                "domainFilters": [{"fieldName": field, "values": values}],
            },
        )
        for field, values in (("cusip", cusips), ("issueSymbolIdentifier", symbols))
        if values
    ]
    records: dict[str, dict] = {}

    for rows in await asyncio.gather(*queries):
        for row in rows:
            if row.get("cusip") and row.get("bondType"):
                records[str(row["cusip"])] = row

    return list(records.values())
