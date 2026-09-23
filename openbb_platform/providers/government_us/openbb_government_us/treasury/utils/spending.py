"""USAspending Spending Explorer helpers."""

EARLIEST_FISCAL_YEAR = 2017

PERIOD_LABELS: dict[str, str] = {
    "2": "Through November",
    "3": "Through December (Q1)",
    "4": "Through January",
    "5": "Through February",
    "6": "Through March (Q2)",
    "7": "Through April",
    "8": "Through May",
    "9": "Through June (Q3)",
    "10": "Through July",
    "11": "Through August",
    "12": "Through September (Q4)",
}

STANDALONE_TYPES = (
    "object_class",
    "budget_function",
    "budget_subfunction",
    "agency",
    "federal_account",
)

SCOPE_ONLY_TYPES = ("program_activity", "recipient", "award", "award_category")

TYPE_LABELS: dict[str, str] = {
    "object_class": "Object Class",
    "budget_function": "Budget Function",
    "budget_subfunction": "Budget Subfunction",
    "agency": "Agency",
    "federal_account": "Federal Account",
    "program_activity": "Program Activity",
    "recipient": "Recipient",
    "award": "Award",
    "award_category": "Award Category",
}

SCOPE_DIMENSIONS = (
    "budget_function",
    "budget_subfunction",
    "agency",
    "federal_account",
    "program_activity",
    "object_class",
    "recipient",
)


def period_options() -> list[dict[str, str]]:
    """Build the reporting-period options, latest first."""
    return [
        {"label": "Latest available", "value": "latest"},
        *({"label": label, "value": value} for value, label in PERIOD_LABELS.items()),
    ]


async def latest_submission(fiscal_year: int | None = None) -> tuple[int, str]:
    """Resolve the most recent published fiscal year and period.

    Parameters
    ----------
    fiscal_year : int | None
        Fiscal year to resolve within. When None, the latest published year
        is used.

    Returns
    -------
    tuple[int, str]
        The fiscal year and the period, as the source expects it.

    Raises
    ------
    OpenBBError
        If the source publishes no submission period for the fiscal year.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
    from openbb_government_us.treasury.utils.usaspending import get_usaspending

    response = await get_usaspending(
        "references/submission_periods/", timeout=REQUEST_TIMEOUT
    )
    periods = [
        row
        for row in response.get("available_periods") or []
        if row.get("submission_fiscal_month")
        and (fiscal_year is None or row.get("submission_fiscal_year") == fiscal_year)
    ]

    if not periods:
        raise OpenBBError(
            f"No published submission period was found for FY{fiscal_year}."
            f" Data begins in FY{EARLIEST_FISCAL_YEAR} Q2 and the most recent"
            " year is only published as its periods close."
        )

    latest = max(
        periods,
        key=lambda row: (
            row["submission_fiscal_year"],
            row["submission_fiscal_month"],
        ),
    )

    return latest["submission_fiscal_year"], str(latest["submission_fiscal_month"])


def parse_scope(scope: str | None) -> tuple[str, str] | None:
    """Split a '<dimension>:<id>' drill token into its parts.

    Parameters
    ----------
    scope : str | None
        A token emitted by a breakdown row, e.g. 'agency:1173'.

    Returns
    -------
    tuple[str, str] | None
        The dimension and id, or None when no token was given.

    Raises
    ------
    OpenBBError
        If the token is malformed or names an unknown dimension.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    value = (scope or "").strip()

    if not value:
        return None

    dimension, separator, identifier = value.partition(":")

    if not separator or not identifier.strip():
        raise OpenBBError(
            f"Invalid scope: '{scope}'. It must read '<dimension>:<id>', e.g."
            " 'agency:1173', as emitted by a breakdown row."
        )

    dimension = dimension.strip()

    if dimension not in SCOPE_DIMENSIONS:
        raise OpenBBError(
            f"Invalid scope dimension: '{dimension}'. Valid dimensions are: "
            + ", ".join(SCOPE_DIMENSIONS)
        )

    return dimension, identifier.strip()


DIMENSION_OPTIONS = (
    "object_class",
    "budget_function",
    "budget_subfunction",
    "agency",
    "federal_account",
)


async def dimension_options(
    dimension: str, agency: str | None = None
) -> list[dict[str, str]]:
    """List the selectable entries of one spending dimension.

    Parameters
    ----------
    dimension : str
        One of DIMENSION_OPTIONS.
    agency : str | None
        Narrow the entries to one agency. Federal accounts number ~1,900
        government-wide but only ~160 within an agency, so the list is only
        practical once scoped.

    Returns
    -------
    list[dict[str, str]]
        Widget options pairing each entry's name with its id, by name.
    """
    from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
    from openbb_government_us.treasury.utils.usaspending import post_usaspending

    if dimension not in DIMENSION_OPTIONS:
        return []

    fiscal_year, period = await latest_submission()
    filters: dict[str, str] = {"fy": str(fiscal_year), "period": period}

    if agency:
        filters["agency"] = agency

    response = await post_usaspending(
        "spending/",
        {"type": dimension, "filters": filters},
        timeout=REQUEST_TIMEOUT,
    )
    options = [
        {"label": str(row["name"]), "value": str(row["id"])}
        for row in response.get("results") or []
        if row.get("id") is not None and row.get("name")
    ]

    return sorted(options, key=lambda option: option["label"])


async def awarding_agency_options() -> list[dict[str, str]]:
    """List the top-tier awarding agencies, by name."""
    from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
    from openbb_government_us.treasury.utils.usaspending import get_usaspending

    response = await get_usaspending(
        "references/toptier_agencies/", timeout=REQUEST_TIMEOUT
    )
    options = [
        {"label": str(row["agency_name"]), "value": str(row["agency_name"])}
        for row in response.get("results") or []
        if row.get("agency_name")
    ]

    return sorted(options, key=lambda option: option["label"])


def explorer_type_options(scoped: bool) -> list[dict[str, str]]:
    """List the breakdowns that work for the current scope.

    Parameters
    ----------
    scoped : bool
        Whether any scoping filter is set.

    Returns
    -------
    list[dict[str, str]]
        The offered breakdowns. The four that are too large to enumerate
        government-wide are offered only once a scope narrows them, so the
        control never presents a choice that would fail.
    """
    offered = STANDALONE_TYPES + (SCOPE_ONLY_TYPES if scoped else ())

    return [{"label": TYPE_LABELS[name], "value": name} for name in offered]
