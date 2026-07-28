"""BLS Helpers."""

from datetime import date as _dateType
from typing import Any


def apply_date_window(
    rows: list[dict[str, Any]],
    start_date: _dateType | None,
    end_date: _dateType | None,
    key: str = "date",
) -> list[dict[str, Any]]:
    """Filter rows to an inclusive ``[start_date, end_date]`` window.

    Applied uniformly to every row — a row whose ``key`` date is missing or
    outside the window is dropped whenever a bound is set.
    """
    if start_date is not None:
        rows = [r for r in rows if r.get(key) is not None and r[key] >= start_date]
    if end_date is not None:
        rows = [r for r in rows if r.get(key) is not None and r[key] <= end_date]
    return rows


async def get_bls_timeseries(  # noqa: PLR0912
    api_key: str | None,
    series_ids: str | list[str],
    start_year: int | None = None,
    end_year: int | None = None,
    calculations: bool = True,
    catalog: bool = True,
    annual_average: bool = True,
    aspects: bool = False,
) -> dict:
    """Get BLS timeseries data. Max 50 symbols per request, and a 20 year historical window.

    Parameters
    ----------
    api_key : str | None
        BLS API key; ``None`` issues an unregistered request (lower limits).
    series_ids : List[str]
        List of BLS series IDs. Max 50 symbols per request.
    start_year : Optional[int]
        Start year for the data. Max history per-request may span 20 years.
    end_year : Optional[int]
        End year for the data.  Max history per-request may span 20 years.
    calculations : bool
        Include calculations in the response, if available. Default is True.
    catalog : bool
        Include catalog information in the response. Default is True.
    annual_average : bool
        Include annual averages in the response, if available. Default is True.
    aspects : bool
        Include aspects in the response, if available. Default is False.

    Returns
    -------
    Dict
        Returns a dictionary with the following keys: data, metadata, messages.
    EmptyDataError
        If no data is found, an EmptyDataError is returned and not raised.
    """
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    from warnings import warn
    from openbb_core.provider.utils.errors import EmptyDataError
    from openbb_core.provider.utils.helpers import amake_request

    symbols = series_ids.split(",") if isinstance(series_ids, str) else series_ids
    if len(symbols) > 50:
        warn(
            "Max 50 symbols per request. Truncating to 50 symbols."
            "Break the request into multiple queries to get more data."
        )
        symbols = symbols[:50]

    headers = {"Content-type": "application/json"}
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = json.dumps(
        {
            k: v
            for k, v in {
                "seriesid": symbols,
                "startyear": start_year,
                "endyear": end_year,
                "catalog": catalog,
                "calculations": calculations,
                "annualaverage": annual_average,
                "aspects": aspects,
                "registrationkey": api_key,
            }.items()
            if v
        }
    )
    res = await amake_request(url=url, method="POST", headers=headers, data=payload)
    results = res.get("Results", {}).get("series", [])  # type: ignore
    messages = res.get("message", [])  # type: ignore
    if messages:
        messages = [
            (
                f"The key provided by the User is invalid. {m.split(' provided by the User is invalid.')[1].strip()}"
                if m.startswith("The key:")
                else m
            )
            for m in messages
            if m
        ]

    metadata: dict = {}
    data: list = []
    for result in results:
        seriesID = result.get("seriesID")
        if not seriesID:
            continue
        catalog = result.get("catalog")
        if catalog:
            metadata.update({seriesID: catalog})
        _data = result.get("data", [])
        for _d in _data:
            new_d: dict = {}
            year = _d.get("year", "")
            month = _d.get("period", "").replace("M", "")
            if month.startswith("A") or month in ("S01", "Q01"):
                _date = year + "-01-01"
            elif month == "S02":
                _date = year + "-07-01"
            elif month in ("S03", "Q05"):
                _date = year + "-12-31"
                month = "13"
            elif month == "Q02":
                _date = year + "-04-01"
            elif month == "Q03":
                _date = year + "-07-01"
            elif month == "Q04":
                _date = year + "-10-01"
            else:
                _date = year + "-12-31" if month == "13" else year + "-" + month + "-01"
            new_d["symbol"] = seriesID
            title = metadata[seriesID].get("series_title") if catalog else None
            title = (
                title + (" (Annual Average)" if month == "13" else "")
                if title
                else None
            )
            if title:
                new_d["title"] = title
            new_d["date"] = _date
            value = _d.get("value")
            if value and value != "-":
                new_d["value"] = float(value)
            else:
                new_d["value"] = None
            new_d["latest"] = _d.get("latest") == "true"
            footnotes = _d.get("footnotes")
            if footnotes:
                new_d["footnotes"] = "; ".join(
                    [
                        f.get("text") if isinstance(f, dict) else str(f)
                        for f in footnotes
                        if f
                    ]
                )
                if not new_d.get("footnotes"):
                    new_d.pop("footnotes")

            calcs = _d.get("calculations")
            if calcs:
                changes = calcs.get("net_changes")
                pct_changes = calcs.get("pct_changes")
                if changes:
                    new_d["change_1M"] = (
                        float(changes.get("1")) if changes.get("1") else None
                    )
                    new_d["change_3M"] = (
                        float(changes.get("3")) if changes.get("3") else None
                    )
                    new_d["change_6M"] = (
                        float(changes.get("6")) if changes.get("6") else None
                    )
                    new_d["change_12M"] = (
                        float(changes.get("12")) if changes.get("12") else None
                    )

                if pct_changes:
                    new_d["change_percent_1M"] = (
                        float(pct_changes.get("1")) / 100
                        if pct_changes.get("1")
                        else None
                    )
                    new_d["change_percent_3M"] = (
                        float(pct_changes.get("3")) / 100
                        if pct_changes.get("3")
                        else None
                    )
                    new_d["change_percent_6M"] = (
                        float(pct_changes.get("6")) / 100
                        if pct_changes.get("6")
                        else None
                    )
                    new_d["change_percent_12M"] = (
                        float(pct_changes.get("12")) / 100
                        if pct_changes.get("12")
                        else None
                    )
            if aspects is True:
                # If there are aspects returned, we want to separate them from the main data.
                # We will store the aspects in the metadata dictionary.
                _aspects = _d.get("aspects")
                if _aspects:
                    for aspect in _aspects:
                        aspect.update(
                            {
                                "date": _date,
                                "footnotes": " ".join(
                                    f.get("text", "") for f in (footnotes or [])
                                ).strip(),
                            }
                        )
                    new_aspects = [
                        d for d in _aspects if d.get("value") and d.get("value") != "-"
                    ]
                    if new_aspects:
                        metadata[seriesID]["aspects"] = new_aspects
                    else:
                        messages.append(f"No Aspect Available for Series {seriesID}")

            if new_d:
                data.append(new_d)

    if not data:
        # Return EmptyDataError if no data is found instead of raising.
        # If we raise here, the API key can be exposed in the traceback.
        return EmptyDataError(f"No data found -> {messages}")  # type: ignore

    return {"data": data, "metadata": metadata, "messages": messages}
