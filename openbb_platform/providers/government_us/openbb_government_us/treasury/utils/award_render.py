"""Render a USAspending award detail record as an OpenBB Workspace HTML widget."""

from html import escape
from pathlib import Path
from typing import Any

TEMPLATE = Path(__file__).parent.parent / "assets" / "award_info.html"

LABELS: dict[str, str] = {
    "award_id": "Award ID",
    "piid": "PIID",
    "fain": "FAIN",
    "uri": "URI",
    "award_type": "Type Code",
    "award_type_description": "Type",
    "category": "Category",
    "record_type": "Record Type",
    "parent_award_id": "Parent Award ID",
    "parent_piid": "Parent PIID",
    "internal_id": "Internal ID",
    "total_obligation": "Total Obligation",
    "base_exercised_options": "Base + Exercised Options",
    "base_and_all_options": "Base + All Options",
    "total_outlay": "Total Outlay",
    "total_account_obligation": "Account Obligation",
    "total_account_outlay": "Account Outlay",
    "total_subaward_amount": "Total Subaward Amount",
    "subaward_count": "Subaward Count",
    "total_subsidy_cost": "Total Subsidy Cost",
    "total_loan_value": "Total Loan Value",
    "non_federal_funding": "Non-Federal Funding",
    "total_funding": "Total Funding",
    "date_signed": "Date Signed",
    "period_start": "Start Date",
    "period_end": "Current End Date",
    "period_potential_end": "Potential End Date",
    "last_modified": "Last Modified",
    "recipient_name": "Recipient",
    "recipient_uei": "Recipient UEI",
    "parent_recipient_name": "Parent Recipient",
    "parent_recipient_uei": "Parent UEI",
    "recipient_city": "City",
    "recipient_state": "State",
    "recipient_zip": "ZIP",
    "recipient_country": "Country",
    "recipient_congressional_district": "Congressional District",
    "place_of_performance_city": "City",
    "place_of_performance_state": "State",
    "place_of_performance_country": "Country",
    "place_of_performance_congressional_district": "Congressional District",
    "awarding_agency": "Awarding Agency",
    "awarding_subagency": "Awarding Sub-Agency",
    "awarding_office": "Awarding Office",
    "funding_agency": "Funding Agency",
    "funding_subagency": "Funding Sub-Agency",
    "funding_office": "Funding Office",
    "funding_agency_abbreviation": "Funding Agency Abbreviation",
    "naics": "NAICS",
    "naics_description": "NAICS Description",
    "psc": "PSC",
    "psc_description": "PSC Description",
    "cfda_number": "Assistance Listing",
    "cfda_title": "Assistance Listing Title",
    "subaward_number": "Subaward Number",
    "subaward_id": "Subaward ID",
    "action_date": "Action Date",
    "amount": "Amount",
    "description": "Description",
}

SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Award",
        (
            "award_id",
            "piid",
            "fain",
            "uri",
            "award_type_description",
            "award_type",
            "category",
            "record_type",
            "parent_award_id",
            "parent_piid",
            "internal_id",
        ),
    ),
    (
        "Amounts",
        (
            "total_obligation",
            "base_exercised_options",
            "base_and_all_options",
            "total_outlay",
            "total_account_obligation",
            "total_account_outlay",
            "total_subaward_amount",
            "subaward_count",
            "total_subsidy_cost",
            "total_loan_value",
            "non_federal_funding",
            "total_funding",
        ),
    ),
    (
        "Period of Performance",
        (
            "date_signed",
            "period_start",
            "period_end",
            "period_potential_end",
            "last_modified",
        ),
    ),
    (
        "Recipient",
        (
            "recipient_name",
            "recipient_uei",
            "parent_recipient_name",
            "parent_recipient_uei",
            "recipient_city",
            "recipient_state",
            "recipient_zip",
            "recipient_country",
            "recipient_congressional_district",
        ),
    ),
    (
        "Place of Performance",
        (
            "place_of_performance_city",
            "place_of_performance_state",
            "place_of_performance_country",
            "place_of_performance_congressional_district",
        ),
    ),
    (
        "Agencies",
        (
            "awarding_agency",
            "awarding_subagency",
            "awarding_office",
            "funding_agency",
            "funding_subagency",
            "funding_office",
            "funding_agency_abbreviation",
        ),
    ),
    (
        "Classification",
        (
            "naics",
            "naics_description",
            "psc",
            "psc_description",
            "cfda_number",
            "cfda_title",
        ),
    ),
)

SUBAWARD_FIELDS = (
    "subaward_number",
    "action_date",
    "amount",
    "description",
    "subaward_id",
)

USD_FIELDS = frozenset(
    {
        "total_obligation",
        "base_exercised_options",
        "base_and_all_options",
        "total_outlay",
        "total_account_obligation",
        "total_account_outlay",
        "total_subaward_amount",
        "total_subsidy_cost",
        "total_loan_value",
        "non_federal_funding",
        "total_funding",
        "amount",
    }
)

GROUPED_FIELDS = frozenset({"subaward_count"})

KPI_FIELDS = (
    "total_obligation",
    "base_and_all_options",
    "total_outlay",
    "total_subaward_amount",
)

BADGE_FIELDS = ("category", "award_type_description", "awarding_agency", "piid")


def _value_cell(field: str, value: Any) -> str:
    """Render one value cell, tagging numerics for display-only grouping."""
    text = escape(str(value))

    if field in USD_FIELDS or field in GROUPED_FIELDS:
        prefix = ' data-prefix="usd"' if field in USD_FIELDS else ""
        return f'<dd class="num" data-value="{text}"{prefix}>{text}</dd>'

    return f"<dd>{text}</dd>"


def _section_html(title: str, fields: tuple[str, ...], record: dict) -> str:
    """Render one titled section, omitting every absent field."""
    rows = [
        f"<dt>{escape(LABELS.get(field, field))}</dt>"
        + _value_cell(field, record[field])
        for field in fields
        if record.get(field) is not None
    ]

    if not rows:
        return ""

    return (
        f'<div class="section"><h2>{escape(title)}</h2><dl>'
        + "".join(rows)
        + "</dl></div>"
    )


def _kpis_html(record: dict) -> str:
    """Render the headline amount cards for the amounts the award reports."""
    cards = [
        f'<div class="kpi"><div class="kpi-label">{escape(LABELS[field])}</div>'
        f'<div class="kpi-value" data-value="{escape(str(record[field]))}"'
        f' data-prefix="usd">{escape(str(record[field]))}</div></div>'
        for field in KPI_FIELDS
        if record.get(field) is not None
    ]

    return "".join(cards)


def _badges_html(record: dict) -> str:
    """Render the identifying badges shown under the title."""
    return "".join(
        f'<span class="badge">{escape(str(record[field]))}</span>'
        for field in BADGE_FIELDS
        if record.get(field) is not None
    )


def _subaward_card(subaward: dict) -> str:
    """Render one subaward as a collapsible card."""
    name = escape(str(subaward.get("recipient_name") or "Unnamed subrecipient"))
    date = escape(str(subaward.get("action_date") or ""))
    amount = subaward.get("amount")
    amount_html = (
        f'<span class="sub-amount" data-value="{escape(str(amount))}"'
        f' data-prefix="usd">{escape(str(amount))}</span>'
        if amount is not None
        else ""
    )
    rows = [
        f"<dt>{escape(LABELS.get(field, field))}</dt>"
        + _value_cell(field, subaward[field])
        for field in SUBAWARD_FIELDS
        if subaward.get(field) is not None
    ]

    return (
        '<details class="sub"><summary>'
        f'<span class="sub-name">{name}</span>'
        f'<span class="sub-date">{date}</span>{amount_html}'
        "</summary>"
        f'<div class="sub-body"><dl>{"".join(rows)}</dl></div>'
        "</details>"
    )


def _subawards_html(subawards: list[dict], total: int | None) -> str:
    """Render the subaward cards, disclosing any rows beyond the render cap."""
    if not subawards:
        return ""

    shown = len(subawards)
    heading = f"Subawards ({total if total is not None else shown})"
    note = (
        f'<p class="note">Showing the first {shown} of {total}.</p>'
        if total is not None and total > shown
        else ""
    )

    return (
        f'<details class="subawards"><summary>{escape(heading)}</summary>'
        + "".join(_subaward_card(subaward) for subaward in subawards)
        + note
        + "</details>"
    )


def render_award_info(
    record: dict,
    subawards: list[dict] | None = None,
    subaward_total: int | None = None,
) -> str:
    """Render an award detail record as a standalone HTML page.

    Parameters
    ----------
    record : dict
        A single ``section='detail'`` award record, with absent fields omitted.
    subawards : list[dict] | None
        The award's ``section='subawards'`` records, rendered as collapsible cards.
    subaward_total : int | None
        Total subawards the award reports, used to disclose a truncated render.

    Returns
    -------
    str
        The rendered HTML document.
    """
    import re

    template = TEMPLATE.read_text(encoding="utf-8")
    title = record.get("recipient_name") or record.get("award_id") or "Award"
    description = record.get("description")
    body = (
        "".join(_section_html(name, fields, record) for name, fields in SECTIONS)
        or '<p class="empty">No award detail was returned.</p>'
    )
    tokens = {
        "__TITLE__": escape(str(title)),
        "__SUBTITLE__": escape(str(record.get("award_id") or "")),
        "__BADGES__": _badges_html(record),
        "__DESCRIPTION__": (
            f'<div class="desc">{escape(str(description))}</div>' if description else ""
        ),
        "__KPIS__": _kpis_html(record),
        "__BODY__": body,
        "__SUBAWARDS__": _subawards_html(subawards or [], subaward_total),
    }

    return re.sub(
        "|".join(tokens),
        lambda match: tokens[match.group(0)],
        template,
    )
