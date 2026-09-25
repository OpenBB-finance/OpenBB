"""Render a USAspending recipient profile as an OpenBB Workspace HTML widget."""

from html import escape
from pathlib import Path
from typing import Any

TEMPLATE = Path(__file__).parent.parent / "assets" / "recipient_info.html"

LEVEL_LABELS: dict[str, str] = {
    "P": "Parent Recipient",
    "C": "Child Recipient",
    "R": "Recipient",
}

LABELS: dict[str, str] = {
    "name": "Name",
    "recipient_id": "Recipient ID",
    "recipient_level": "Level",
    "uei": "UEI",
    "duns": "Legacy DUNS",
    "parent_name": "Parent Recipient",
    "parent_uei": "Parent UEI",
    "parent_duns": "Parent DUNS",
    "parent_id": "Parent ID",
    "address_line1": "Address",
    "address_line2": "Address 2",
    "address_line3": "Address 3",
    "city_name": "City",
    "county_name": "County",
    "state_code": "State",
    "zip": "ZIP",
    "zip4": "ZIP+4",
    "congressional_code": "Congressional District",
    "country_name": "Country",
    "country_code": "Country Code",
    "foreign_province": "Foreign Province",
    "foreign_postal_code": "Foreign Postal Code",
    "total_transaction_amount": "Transaction Amount",
    "total_transactions": "Transactions",
    "total_face_value_loan_amount": "Face Value of Loans",
    "total_face_value_loan_transactions": "Loan Transactions",
    "amount": "Amount",
    "state_province": "State",
}

IDENTITY_FIELDS = (
    "name",
    "recipient_level",
    "uei",
    "duns",
    "recipient_id",
    "parent_name",
    "parent_uei",
    "parent_duns",
    "parent_id",
)

LOCATION_FIELDS = (
    "address_line1",
    "address_line2",
    "address_line3",
    "city_name",
    "county_name",
    "state_code",
    "zip",
    "zip4",
    "congressional_code",
    "country_name",
    "foreign_province",
    "foreign_postal_code",
)

CHILD_FIELDS = ("recipient_id", "uei", "duns", "state_province", "amount")

USD_FIELDS = frozenset(
    {"total_transaction_amount", "total_face_value_loan_amount", "amount"}
)

COUNT_FIELDS = frozenset({"total_transactions", "total_face_value_loan_transactions"})

KPI_FIELDS = (
    "total_transaction_amount",
    "total_transactions",
    "total_face_value_loan_amount",
    "total_face_value_loan_transactions",
)


def _number_cell(field: str, value: Any, tag: str = "dd") -> str:
    """Render a value cell, tagging numerics for display-only formatting."""
    text = escape(str(value))

    if field in USD_FIELDS:
        return f'<{tag} data-value="{text}" data-prefix="usd">{text}</{tag}>'

    if field in COUNT_FIELDS:
        return f'<{tag} data-value="{text}">{text}</{tag}>'

    return f"<{tag}>{text}</{tag}>"


def _rows_html(fields: tuple[str, ...], record: dict) -> str:
    """Render definition rows for the populated fields of a record."""
    return "".join(
        f"<dt>{escape(LABELS.get(field, field))}</dt>"
        + _number_cell(field, record[field])
        for field in fields
        if record.get(field) not in (None, "")
    )


def _section_html(title: str, body: str) -> str:
    """Wrap rendered rows in a titled section, dropping an empty one."""
    if not body:
        return ""

    return f'<div class="section"><h2>{escape(title)}</h2><dl>{body}</dl></div>'


def _kpis_html(profile: dict) -> str:
    """Render the headline totals the recipient reports."""
    return "".join(
        f'<div class="kpi"><div class="kpi-label">{escape(LABELS[field])}</div>'
        + _number_cell(field, profile[field], tag="div").replace(
            "<div ", '<div class="kpi-value" ', 1
        )
        + "</div>"
        for field in KPI_FIELDS
        if profile.get(field) is not None
    )


def _badges_html(profile: dict) -> str:
    """Render the identifying badges shown under the title."""
    location = profile.get("location") or {}
    values = [
        LEVEL_LABELS.get(profile.get("recipient_level") or ""),
        profile.get("uei"),
        profile.get("duns"),
        location.get("state_code"),
        *(profile.get("business_types") or []),
    ]

    return "".join(
        f'<span class="badge">{escape(str(value).replace("_", " "))}</span>'
        for value in values
        if value
    )


def _top_table(title: str, rows: list[dict], denominator: float | None) -> str:
    """Render one top-category table, deriving each row's share of the total."""
    if not rows:
        return ""

    cells = []

    for row in rows:
        amount = row.get("amount")
        share = (
            f'<td class="num pct" data-value="{amount / denominator * 100}"'
            f' data-prefix="pct">{amount / denominator * 100}</td>'
            if amount is not None and denominator
            else '<td class="num pct"></td>'
        )
        cells.append(
            f"<tr><td>{escape(str(row.get('name') or ''))}</td>"
            + (
                f'<td class="num" data-value="{escape(str(amount))}"'
                f' data-prefix="usd">{escape(str(amount))}</td>'
                if amount is not None
                else '<td class="num"></td>'
            )
            + share
            + "</tr>"
        )

    return (
        f'<div class="top-card"><h3>{escape(title)}</h3><table>'
        '<tr><th>Name</th><th class="num">Obligations</th>'
        '<th class="num">% of Total</th></tr>' + "".join(cells) + "</table></div>"
    )


def _tops_html(tops: dict[str, list[dict]], denominator: float | None) -> str:
    """Render the top-category tables inside a collapsible container."""
    from openbb_government_us.treasury.utils.recipient import TOP_CATEGORIES

    cards = "".join(
        _top_table(TOP_CATEGORIES[category], rows, denominator)
        for category, rows in tops.items()
        if category in TOP_CATEGORIES
    )

    if not cards:
        return ""

    return (
        '<details class="tops"><summary>Top Categories</summary>'
        f'<div class="top-grid">{cards}</div></details>'
    )


def _child_card(child: dict) -> str:
    """Render one child recipient as a collapsible card."""
    name = escape(str(child.get("name") or "Unnamed recipient"))
    state = escape(str(child.get("state_province") or ""))
    amount = child.get("amount")
    amount_html = (
        f'<span class="child-amount" data-value="{escape(str(amount))}"'
        f' data-prefix="usd">{escape(str(amount))}</span>'
        if amount is not None
        else ""
    )

    return (
        '<details class="child"><summary>'
        f'<span class="child-name">{name}</span>'
        f'<span class="child-state">{state}</span>{amount_html}'
        "</summary>"
        f'<div class="child-body"><dl>{_rows_html(CHILD_FIELDS, child)}</dl></div>'
        "</details>"
    )


def _children_html(children: list[dict], shown: int | None = None) -> str:
    """Render the child recipients inside a collapsible container."""
    if not children:
        return ""

    total = shown if shown is not None else len(children)
    note = (
        f'<p class="note">Showing the first {len(children)} of {total}.</p>'
        if total > len(children)
        else ""
    )

    return (
        f'<details class="children"><summary>Child Recipients ({total})</summary>'
        + "".join(_child_card(child) for child in children)
        + note
        + "</details>"
    )


def render_recipient_info(
    profile: dict,
    tops: dict[str, list[dict]] | None = None,
    children: list[dict] | None = None,
    denominator: float | None = None,
    child_total: int | None = None,
) -> str:
    """Render a recipient profile as a standalone HTML page.

    Parameters
    ----------
    profile : dict
        The recipient profile payload.
    tops : dict[str, list[dict]] | None
        Top-category rows keyed by category name.
    children : list[dict] | None
        Child recipient rows, rendered as collapsible cards.
    denominator : float | None
        Total obligations over the same window, used to derive each category
        row's share. Shares are omitted when it is absent or zero.
    child_total : int | None
        Total child recipients, used to disclose a truncated render.

    Returns
    -------
    str
        The rendered HTML document.
    """
    import re

    template = TEMPLATE.read_text(encoding="utf-8")
    location = profile.get("location") or {}
    body = (
        _section_html("Identity", _rows_html(IDENTITY_FIELDS, profile))
        + _section_html("Location", _rows_html(LOCATION_FIELDS, location))
    ) or '<p class="empty">No recipient detail was returned.</p>'
    tokens = {
        "__TITLE__": escape(str(profile.get("name") or "Recipient")),
        "__SUBTITLE__": escape(str(profile.get("recipient_id") or "")),
        "__BADGES__": _badges_html(profile),
        "__KPIS__": _kpis_html(profile),
        "__BODY__": body,
        "__TOPS__": _tops_html(tops or {}, denominator),
        "__CHILDREN__": _children_html(children or [], child_total),
    }

    return re.sub("|".join(tokens), lambda match: tokens[match.group(0)], template)


def recipient_rows(
    profile: dict,
    tops: dict[str, list[dict]] | None = None,
    children: list[dict] | None = None,
    denominator: float | None = None,
) -> list[dict]:
    """Flatten a recipient profile into tabular records.

    Parameters
    ----------
    profile : dict
        The recipient profile payload.
    tops : dict[str, list[dict]] | None
        Top-category rows keyed by category name.
    children : list[dict] | None
        Child recipient rows.
    denominator : float | None
        Total obligations, used to derive each category row's share.

    Returns
    -------
    list[dict]
        One record per fact, sharing a single column set so the raw view
        renders as a table.
    """
    from openbb_government_us.treasury.utils.recipient import TOP_CATEGORIES

    location = profile.get("location") or {}
    rows: list[dict] = []

    def add(section: str, name: str, **values) -> None:
        """Append one record with the shared column set."""
        rows.append(
            {
                "section": section,
                "name": name,
                "value": values.get("value"),
                "amount": values.get("amount"),
                "percent_of_total": values.get("percent_of_total"),
                "code": values.get("code"),
                "uei": values.get("uei"),
                "state": values.get("state"),
                "recipient_id": values.get("recipient_id"),
            }
        )

    for field in IDENTITY_FIELDS:
        if profile.get(field) not in (None, ""):
            add("Identity", LABELS.get(field, field), value=str(profile[field]))

    for field in LOCATION_FIELDS:
        if location.get(field) not in (None, ""):
            add("Location", LABELS.get(field, field), value=str(location[field]))

    for name in profile.get("alternate_names") or []:
        add("Alternate Names", str(name))

    for slug in profile.get("business_types") or []:
        add("Business Types", str(slug).replace("_", " "))

    for field in KPI_FIELDS:
        if profile.get(field) is not None:
            add("Totals", LABELS[field], amount=profile[field])

    for category, entries in (tops or {}).items():
        label = TOP_CATEGORIES.get(category, category)

        for entry in entries:
            amount = entry.get("amount")
            add(
                label,
                str(entry.get("name") or ""),
                amount=amount,
                percent_of_total=(
                    amount / denominator * 100
                    if amount is not None and denominator
                    else None
                ),
                code=entry.get("code"),
            )

    for child in children or []:
        add(
            "Child Recipients",
            str(child.get("name") or ""),
            amount=child.get("amount"),
            uei=child.get("uei"),
            state=child.get("state_province"),
            recipient_id=child.get("recipient_id"),
        )

    return rows
