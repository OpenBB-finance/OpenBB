"""Code lists and validation for the USAspending award search filters."""

from typing import Any

CONTRACT_PRICING: dict[str, str] = {
    "A": "Fixed Price Redetermination",
    "B": "Fixed Price Level of Effort",
    "J": "Firm Fixed Price",
    "K": "Fixed Price with Economic Price Adjustment",
    "L": "Fixed Price Incentive",
    "M": "Fixed Price Award Fee",
    "R": "Cost Plus Award Fee",
    "S": "Cost No Fee",
    "T": "Cost Sharing",
    "U": "Cost Plus Fixed Fee",
    "V": "Cost Plus Incentive Fee",
    "Y": "Time and Materials",
    "Z": "Labor Hours",
    "1": "Order Dependent",
    "2": "Combination",
    "3": "Other",
}

SET_ASIDE: dict[str, str] = {
    "8A": "8(a) Competed",
    "8AN": "8(a) Sole Source",
    "8ACCiv": "SDB Set Aside 8(a)",
    "HS3": "8(a) with HUBZone Preference",
    "HS2Civ": "Combination HUBZone and 8(a)",
    "HZC": "HUBZone Set Aside",
    "HZS": "HUBZone Sole Source",
    "HMP": "HBCU or MI Set Aside - Partial",
    "HMT": "HBCU or MI Set Aside - Total",
    "BI": "Buy Indian",
    "ISEE": "Indian Economic Enterprise",
    "ISBEE": "Indian Small Business Economic Enterprise",
    "EDWOSB": "Economically-Disadvantaged Women-Owned Small Business",
    "EDWOSBSS": "Economically Disadvantaged Women Owned Small Business Sole Source",
    "WOSB": "Women-Owned Small Business",
    "WOSBSS": "Women Owned Small Business Sole Source",
    "SDVOSBC": "Service-Disabled Veteran-Owned Small Business Set Aside",
    "SDVOSBS": "SDVOSB Sole Source",
    "VSA": "Veteran Set Aside",
    "VSS": "Veteran Sole Source",
    "SBA": "Small Business Set Aside - Total",
    "SBP": "Small Business Set Aside - Partial",
    "ESB": "Emerging Small Business Set Aside",
    "RSBCiv": "Reserved for Small Business $2,501 to $100K",
    "VSBCiv": "Very Small Business Set Aside",
    "NONE": "No Set Aside Used",
}

EXTENT_COMPETED: dict[str, str] = {
    "A": "Full and Open Competition",
    "D": "Full and Open Competition after exclusion of sources",
    "F": "Competed under SAP",
    "CDOCiv": "Competitive Delivery Order",
    "E Civ": "Follow On to Competed Action",
    "B": "Not Available for Competition",
    "C": "Not Competed",
    "G": "Not Competed under SAP",
    "NDOCiv": "Non-Competitive Delivery Order",
}

CODE_LISTS: dict[str, dict[str, str]] = {
    "contract_pricing": CONTRACT_PRICING,
    "set_aside": SET_ASIDE,
    "extent_competed": EXTENT_COMPETED,
}

AUTOCOMPLETE: dict[str, tuple[str, str]] = {
    "naics": ("autocomplete/naics/", "naics"),
    "psc": ("autocomplete/psc/", "product_or_service_code"),
    "assistance_listing": ("autocomplete/cfda/", "program_number"),
}


def split_codes(value: str | None) -> list[str]:
    """Split a comma-separated code list into stripped, non-empty entries."""
    if not value:
        return []

    return [part.strip() for part in str(value).split(",") if part.strip()]


def validate_codes(field: str, value: str | None) -> list[str]:
    """Validate codes against a fixed code list.

    Parameters
    ----------
    field : str
        Key of CODE_LISTS to validate against.
    value : str | None
        Comma-separated codes.

    Returns
    -------
    list[str]
        The validated codes.

    Raises
    ------
    OpenBBError
        If any code is not in the list, because the source silently returns no
        rows for an unrecognized code rather than reporting an error.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    codes = split_codes(value)
    allowed = CODE_LISTS[field]
    unknown = [code for code in codes if code not in allowed]

    if unknown:
        raise OpenBBError(
            f"Invalid {field} code(s): {', '.join(unknown)}. Valid codes are: "
            + ", ".join(f"{code} ({label})" for code, label in allowed.items())
        )

    return codes


async def validate_reference_codes(field: str, value: str | None) -> list[str]:
    """Validate codes against the source's autocomplete reference.

    Parameters
    ----------
    field : str
        Key of AUTOCOMPLETE to validate against.
    value : str | None
        Comma-separated codes.

    Returns
    -------
    list[str]
        The validated codes.

    Raises
    ------
    OpenBBError
        If a code matches nothing, because the source silently returns no rows
        for an unrecognized code rather than reporting an error.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
    from openbb_government_us.treasury.utils.usaspending import post_usaspending

    codes = split_codes(value)

    if not codes:
        return []

    path, key = AUTOCOMPLETE[field]

    for code in codes:
        response = await post_usaspending(
            path, {"search_text": code, "limit": 100}, timeout=REQUEST_TIMEOUT
        )
        matches = {
            str(row.get(key)) for row in response.get("results") or [] if row.get(key)
        }

        if code not in matches:
            raise OpenBBError(
                f"Unknown {field} code: '{code}'."
                + (
                    f" Did you mean one of: {', '.join(sorted(matches)[:8])}?"
                    if matches
                    else " It matched nothing in the source's reference list."
                )
            )

    return codes


async def def_code_options() -> list[dict[str, str]]:
    """List the Disaster Emergency Fund Codes as widget options."""
    from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
    from openbb_government_us.treasury.utils.usaspending import get_usaspending

    response = await get_usaspending("references/def_codes/", timeout=REQUEST_TIMEOUT)
    options: list[dict[str, str]] = []

    for row in response.get("codes") or []:
        code = row.get("code")

        if not code:
            continue

        title = row.get("title") or row.get("public_law") or ""
        options.append({"label": f"{code} - {title}" if title else code, "value": code})

    return options


def code_options(field: str) -> list[dict[str, str]]:
    """Build the widget options for a fixed code list."""
    return [
        {"label": f"{label} ({code})", "value": code}
        for code, label in CODE_LISTS[field].items()
    ]


def apply_filters(query: Any, filters: dict[str, Any]) -> dict[str, Any]:
    """Add the validated code filters to an award search filter object."""
    mapping = {
        "contract_pricing": "contract_pricing_type_codes",
        "set_aside": "set_aside_type_codes",
        "extent_competed": "extent_competed_type_codes",
    }

    for field, target in mapping.items():
        codes = validate_codes(field, getattr(query, field, None))

        if codes:
            filters[target] = codes

    return filters
