"""Nasdaq Nordic Trading Hours and Holiday Schedule Parsing.

The session hours and the exchange holiday calendar are published only as
server-rendered tables on the trading-hours page, so they are read out of the
markup rather than from an API.
"""

from __future__ import annotations

import re

TRADING_HOURS_URL = "https://www.nasdaq.com/european-market-activity/trading-hours"

TABLE = re.compile(r"<table.*?</table>", re.S)

ROW = re.compile(r"<tr.*?</tr>", re.S)

CELL = re.compile(r"<t[dh].*?</t[dh]>", re.S)

HEADING = re.compile(r"<h[23][^>]*>(.*?)</h[23]>", re.S)

HOLIDAY_YEAR = re.compile(r"Exchange Holiday Schedule\s+(\d{4})")

CLOSED_DATE = re.compile(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})")


def clean(markup: str) -> str:
    """Strip markup and collapse whitespace to a single readable line.

    Parameters
    ----------
    markup : str
        A fragment of HTML.

    Returns
    -------
    str
        The visible text.
    """
    from html import unescape

    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", markup))).strip()


async def fetch_trading_hours() -> str:
    """Download the Nasdaq Nordic trading-hours page.

    Returns
    -------
    str
        The page markup.
    """
    from openbb_core.provider.utils.helpers import amake_request

    from openbb_nasdaq.utils.helpers import get_headers

    async def return_text(response, _):
        """Return the decoded response body."""
        return await response.text()

    markup = await amake_request(
        TRADING_HOURS_URL,
        headers=get_headers("text"),
        response_callback=return_text,
    )

    return markup if isinstance(markup, str) else ""


def _tables(markup: str) -> list[tuple[str, list[list[str]]]]:
    """Split the page into its tables, each with the heading above it.

    Parameters
    ----------
    markup : str
        The page markup.

    Returns
    -------
    list[tuple]
        One ``(heading, rows)`` pair per table, rows being lists of cells.
    """
    tables: list[tuple[str, list[list[str]]]] = []

    for match in TABLE.finditer(markup):
        headings = [clean(h) for h in HEADING.findall(markup[: match.start()])]
        rows = [
            [clean(cell) for cell in CELL.findall(row)]
            for row in ROW.findall(match.group(0))
        ]
        tables.append((headings[-1] if headings else "", rows))

    return tables


def parse_trading_hours(markup: str) -> list[dict]:
    """Read the session hours out of the trading-hours page.

    Each table heads its columns with the Nordic markets and its rows with the
    traded segment, so the grid is flattened into one record per segment and
    market.

    Parameters
    ----------
    markup : str
        The page markup.

    Returns
    -------
    list[dict]
        One record per segment, market, and session.
    """
    results: list[dict] = []

    for heading, rows in _tables(markup):
        if HOLIDAY_YEAR.search(heading) or len(rows) < 2:
            continue

        header = rows[0]
        section = clean(header[0]) or heading

        if not section:
            continue

        for row in rows[1:]:
            segment = row[0] if row else ""

            if not segment:
                continue

            for column, value in zip(header[1:], row[1:]):
                hours = value.replace("\xa0", " ").strip()

                if not hours or hours in {"-", "--", "---"}:
                    continue

                results.append(
                    {
                        "section": section,
                        "segment": segment,
                        "market": column.replace("\xa0", " ").strip(),
                        "hours": hours,
                    }
                )

    return results


def parse_holidays(markup: str) -> list[dict]:
    """Read the exchange holiday calendar out of the trading-hours page.

    Parameters
    ----------
    markup : str
        The page markup.

    Returns
    -------
    list[dict]
        One record per market, instrument group, and closed date.
    """
    from datetime import datetime

    results: list[dict] = []

    for heading, rows in _tables(markup):
        year = HOLIDAY_YEAR.search(heading)

        if not year or len(rows) < 2:
            continue

        header = rows[0]

        for row in rows[1:]:
            market = row[0] if row else ""

            if not market:
                continue

            for column, value in zip(header[1:], row[1:]):
                for month, day, closed_year in CLOSED_DATE.findall(
                    value.replace("\xa0", " ")
                ):
                    try:
                        closed = datetime.strptime(
                            f"{month} {day} {closed_year}", "%b %d %Y"
                        ).date()
                    except ValueError:
                        continue

                    results.append(
                        {
                            "market": market,
                            "instrument_group": column,
                            "date": closed,
                        }
                    )

    return results
