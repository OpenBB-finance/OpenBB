"""CFTC provider helpers."""

from typing import Any

_COT_CHOICES: list[dict] = []


async def socrata_json(response: Any, _: Any) -> Any:
    """Decode a CFTC public-reporting response, raising a clear error on an outage."""
    from openbb_core.app.model.abstract.error import OpenBBError

    content_type = response.headers.get("Content-Type", "")

    if response.status != 200 or "json" not in content_type:
        raise OpenBBError(
            f"The CFTC public reporting API returned HTTP {response.status}"
            f" ({content_type or 'no content type'}). The portal is likely undergoing"
            " maintenance or is temporarily unavailable - try again shortly."
        )

    return await response.json()


async def get_cot_choices() -> list[dict]:
    """Return the COT contract choices for Workspace, fetched once per process."""
    from openbb_cftc.models.cot_search import CftcCotSearchData, CftcCotSearchFetcher

    global _COT_CHOICES  # noqa: PLW0603

    if _COT_CHOICES:
        return _COT_CHOICES

    contracts = await CftcCotSearchFetcher.fetch_data({}, {})
    choices: list[dict] = []

    for contract in contracts:
        if not isinstance(contract, CftcCotSearchData):
            continue

        code = (contract.code or "").strip()
        name = (contract.name or "").strip()
        subcategory = (contract.subcategory or "").strip()

        if not code:
            continue

        choices.append(
            {
                "label": name,
                "value": code,
                "extraInfo": {
                    "description": f"{subcategory}  | {code}",
                    "rightOfDescription": "",
                },
            }
        )

    _COT_CHOICES = choices

    return _COT_CHOICES


async def get_ppd_date_choices(asset_class: str) -> list[dict]:
    """Return the report dates published for an asset class."""
    from openbb_cftc.utils.dtcc import get_available_dates

    dates = await get_available_dates(asset_class)

    return [{"label": d, "value": d} for d in reversed(dates)]


def reset_cot_choices() -> None:
    """Clear the cached COT choices."""
    global _COT_CHOICES  # noqa: PLW0603

    _COT_CHOICES = []
