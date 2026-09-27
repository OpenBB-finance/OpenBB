"""As-filed statement grouping, tag precedence, and period selection."""

import re
from datetime import date

from openbb_core.app.model.abstract.error import OpenBBError


def is_consolidated(fact) -> bool:
    """Exclude segmented and co-registrant facts."""
    return fact["segments"] in (None, "") and fact["coreg"] in (None, "")


def build_records(
    facts_by_field: dict[str, list[dict]], field_tags: dict[str, list[str]]
) -> list[dict]:
    """Preserve each filing and use its first available preferred tag."""
    groups = {}
    for field, facts in facts_by_field.items():
        for fact in facts:
            if not is_consolidated(fact):
                continue
            key = (fact["accession_id"], fact["period_end"])
            if key not in groups:
                groups[key] = (fact, {})
            _, fields = groups[key]
            fields.setdefault(field, {}).setdefault(fact["tag"], fact["value"])

    records = []
    for fact, fields in groups.values():
        record = {
            "period_ending": date.fromisoformat(fact["period_end"]),
            "accession_id": fact["accession_id"],
            "form": fact["form"],
            "filed": date.fromisoformat(fact["filed"]),
            "source_url": fact["source_url"],
            "duration_quarters": int(fact["duration_quarters"]),
        }
        for field, tags in field_tags.items():
            values = fields.get(field, {})
            value = next((values[tag] for tag in tags if tag in values), None)
            record[field] = float(value) if value is not None else None
        records.append(record)
    return records


def order_and_limit(records, limit) -> list[dict]:
    """Limit distinct periods while retaining every filing for those periods."""
    ordered = sorted(
        records,
        key=lambda record: (
            record["period_ending"], record["filed"], record["accession_id"]
        ),
        reverse=True,
    )
    if limit is None:
        return ordered
    periods = list(dict.fromkeys(record["period_ending"] for record in ordered))
    selected = set(periods[:limit])
    return [record for record in ordered if record["period_ending"] in selected]


def validate_cik(symbol: str) -> int:
    """Require a SEC CIK instead of a ticker."""
    symbol = symbol.strip()
    if re.fullmatch(r"[0-9]{1,10}", symbol) is None:
        raise OpenBBError(
            "Arkleon /v1 is addressed by CIK: pass the company's SEC CIK "
            "(digits only) as symbol. Tickers are not served by /v1."
        )
    return int(symbol)
