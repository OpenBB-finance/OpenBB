"""Runtime access to the generated EIA dataset catalog."""

import json
import lzma
import re
from datetime import (
    date as dateType,
    datetime,
    timedelta,
    timezone,
)
from functools import lru_cache
from pathlib import Path
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

ASSET_PATH = Path(__file__).parent.parent / "assets" / "eia_catalog.json.xz"

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")

_SLUG_DROP_TOKENS = {"inc", "llc", "ltd"}


def snake_case(name: str) -> str:
    """Convert an API identifier to snake_case."""
    return _CAMEL_RE.sub("_", name.replace("-", "_")).lower()


def label_slug(
    label: str,
    max_length: int = 60,
    keep_parenthetical: bool = False,
) -> str:
    """Build a human-readable snake_case parameter value from a display label.

    Parameters
    ----------
    label : str
        The display label, e.g. 'Battery storage' or 'Spot Price FOB'.
    max_length : int
        Maximum slug length; longer slugs are cut at a word boundary.
    keep_parenthetical : bool
        Keep parenthetical text as words instead of dropping it. Used to
        disambiguate labels like 'Columbia (WI)' and 'Columbia (SC)'.

    Returns
    -------
    str
        The slug, e.g. 'battery_storage' or 'spot_price_fob'.
    """
    text = label.lower().replace("&", " and ")
    text = text.replace("u.s.", " us ").replace("f.o.b.", " fob ")
    if keep_parenthetical:
        text = text.replace("(", " ").replace(")", " ")
    else:
        text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"^table \d+\W*", "", text)
    text = re.sub(r"[^0-9a-z]+", "_", text).strip("_")
    tokens = [t for t in text.split("_") if t and t not in _SLUG_DROP_TOKENS]
    slug = "_".join(tokens)
    if not slug:
        return "value"
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("_", 1)[0] or slug[:max_length]
    return slug


def attach_params(choices: list[dict[str, str]]) -> list[dict[str, str]]:
    """Attach a readable ``param`` slug to each choice of one facet vocabulary.

    Parameters
    ----------
    choices : list[dict[str, str]]
        Choice records with 'value' and 'label' keys, deduplicated by value.

    Returns
    -------
    list[dict[str, str]]
        The records with a 'param' slug per choice.
    """
    labels = [choice.get("label") or choice["value"] for choice in choices]
    slugs = [label_slug(label) for label in labels]

    by_slug: dict[str, set[str]] = {}
    for slug, label in zip(slugs, labels):
        by_slug.setdefault(slug, set()).add(label)
    retry = {slug for slug, slug_labels in by_slug.items() if len(slug_labels) > 1}
    for index, slug in enumerate(slugs):
        if slug in retry:
            slugs[index] = label_slug(
                labels[index], max_length=250, keep_parenthetical=True
            )

    assigned: dict[str, str] = {}
    out: list[dict[str, str]] = []
    for index, choice in enumerate(choices):
        slug, label = slugs[index], labels[index]
        if slug in assigned and assigned[slug] != label:
            code = re.sub(r"[^0-9a-z]+", "_", choice["value"].lower()).strip("_")
            candidate = f"{slug}_{code}" if code else f"{slug}_{index}"
            slug = candidate if candidate not in assigned else f"{slug}_{index}"
        assigned[slug] = label
        out.append({**choice, "param": slug})
    return out


STANDARD_FIELDS = {
    "dataset",
    "release",
    "frequency",
    "data_type",
    "start_date",
    "end_date",
    "sort",
    "limit",
}

DATASET_GROUPS = (
    "coal",
    "petroleum",
    "natural_gas",
    "electricity",
    "electricity_grid",
    "state_electricity_profiles",
    "densified_biomass",
    "nuclear_outages",
)


def pascal_case(name: str) -> str:
    """Convert a snake_case identifier to PascalCase."""
    return "".join(part.capitalize() for part in name.split("_"))


def model_name(group: str, dataset: str) -> str:
    """Build the provider-interface model name for one dataset."""
    return f"Eia{pascal_case(group)}{pascal_case(dataset)}"


def dataset_summary(spec: dict[str, Any]) -> str:
    """Build the one-line command summary for a dataset."""
    name = (
        spec["name"]
        .replace("U.S.", "US")
        .replace("F.O.B.", "FOB")
        .replace("No. ", "No ")
        .replace("\\", "/")
        .rstrip(".")
    )
    description = spec.get("description") or ""
    return f"{name}." + (f" {description}" if description else "")


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    """Load the packaged EIA dataset catalog.

    Returns
    -------
    dict[str, Any]
        The full catalog document keyed by group name.
    """
    return json.loads(lzma.decompress(ASSET_PATH.read_bytes()).decode("utf-8"))[
        "groups"
    ]


def get_group(group: str) -> dict[str, Any]:
    """Get one catalog group.

    Parameters
    ----------
    group : str
        Catalog group name, e.g. 'coal'.

    Returns
    -------
    dict[str, Any]
        The group document with 'datasets' and 'choices' keys.
    """
    catalog = load_catalog()
    if group not in catalog:
        raise OpenBBError(
            ValueError(f"Unknown EIA group '{group}'. Choices: {', '.join(catalog)}")
        )
    return catalog[group]


def get_dataset(group: str, dataset: str) -> dict[str, Any]:
    """Get one dataset specification.

    Parameters
    ----------
    group : str
        Catalog group name.
    dataset : str
        Dataset slug within the group.

    Returns
    -------
    dict[str, Any]
        The dataset specification.
    """
    datasets = get_group(group)["datasets"]
    if dataset not in datasets:
        raise OpenBBError(
            ValueError(
                f"Unknown dataset '{dataset}' for EIA group '{group}'."
                f" Choices: {', '.join(datasets)}"
            )
        )
    return datasets[dataset]


def dataset_choices(group: str) -> list[str]:
    """List the dataset slugs of a group."""
    return list(get_group(group)["datasets"])


def facet_choices(group: str, facet: str) -> list[dict[str, str]]:
    """Embedded value choices for one canonical facet of a group.

    Parameters
    ----------
    group : str
        Catalog group name.
    facet : str
        Canonical facet parameter name.

    Returns
    -------
    list[dict[str, str]]
        Choices as {'value': ..., 'label': ...} records; empty when the facet's
        value set is too large to embed.
    """
    return get_group(group)["choices"].get(facet, [])


def facet_schema(group: str, facet: str) -> dict[str, Any]:
    """Build the ``__json_schema_extra__`` entry for a multi-value facet field.

    Parameters
    ----------
    group : str
        Catalog group name.
    facet : str
        Canonical facet parameter name.

    Returns
    -------
    dict[str, Any]
        Schema extra with ``multiple_items_allowed`` and embedded choices when
        the facet's value set is small enough.
    """
    schema: dict[str, Any] = {"multiple_items_allowed": True}
    choices = facet_choices(group, facet)
    if choices and len(choices) <= SCHEMA_CHOICES_LIMIT:
        schema["choices"] = [
            choice.get("param") or choice["value"] for choice in choices
        ]
    return schema


def facet_description(group: str, facet: str, multiple: bool = True) -> str:
    """Build a query field description for one canonical facet.

    Parameters
    ----------
    group : str
        Catalog group name.
    facet : str
        Canonical facet parameter name.
    multiple : bool
        Whether the field accepts a comma-separated list of codes.

    Returns
    -------
    str
        Description text listing the datasets the facet applies to.
    """
    datasets = get_group(group)["datasets"]
    applies = [slug for slug, spec in datasets.items() if facet in spec["facets"]]
    labels = {
        spec["facets"][facet]["description"]
        for spec in datasets.values()
        if facet in spec["facets"]
    }
    label = sorted(labels)[0] if labels else facet
    parts = [f"{label} filter."]
    if multiple:
        parts.append("Accepts a comma-separated list of codes.")
    choices = facet_choices(group, facet)
    if choices:
        parts.append(f"Choices: {choices_text(choices)}.")
    else:
        parts.append("Use the `facet_options` endpoint for the list of valid codes.")
    if len(applies) < len(datasets):
        parts.append(f"Applies to datasets: {', '.join(applies)}.")
    return " ".join(parts)


def resolve_frequency(spec: dict[str, Any], frequency: str | None) -> tuple[str, dict]:
    """Resolve and validate the frequency for a dataset.

    Parameters
    ----------
    spec : dict[str, Any]
        Dataset specification.
    frequency : str | None
        Requested frequency id; None selects the dataset default.

    Returns
    -------
    tuple[str, dict]
        The frequency id and its specification (format, path).
    """
    frequencies = spec["frequencies"]
    if frequency is None:
        frequency = spec.get("default_frequency") or next(iter(frequencies))
    if frequency not in frequencies:
        raise OpenBBError(
            ValueError(
                f"Frequency '{frequency}' is not available for '{spec['path']}'."
                f" Choices: {', '.join(frequencies)}"
            )
        )
    return frequency, frequencies[frequency]


def resolve_data_columns(spec: dict[str, Any], data_type: str | None) -> list[str]:
    """Resolve the API data column ids to request for a dataset.

    Parameters
    ----------
    spec : dict[str, Any]
        Dataset specification.
    data_type : str | None
        Comma-separated data column names; None selects all columns.

    Returns
    -------
    list[str]
        API data column ids.
    """
    columns = spec["data_columns"]
    if not data_type:
        return [detail["id"] for detail in columns.values()]
    requested = [snake_case(item.strip()) for item in data_type.split(",")]
    invalid = [item for item in requested if item and item not in columns]
    if invalid:
        raise OpenBBError(
            ValueError(
                f"Invalid data_type value(s) {', '.join(invalid)} for '{spec['path']}'."
                f" Choices: {', '.join(columns)}"
            )
        )
    return [columns[item]["id"] for item in requested if item]


SCHEMA_CHOICES_LIMIT = 100


def choices_text(choices: list[dict[str, str]], limit: int = 50) -> str:
    """Render facet or column choices as an inline readable list.

    Parameters
    ----------
    choices : list[dict[str, str]]
        Choice records with 'value', 'label', and optional 'param' keys.
    limit : int
        Maximum number of choices to render.

    Returns
    -------
    str
        Semicolon-separated readable values, capped at ``limit``.
    """
    parts = [choice.get("param") or choice["value"] for choice in choices[:limit]]
    text = "; ".join(parts)
    if len(choices) > limit:
        text += (
            f"; plus {len(choices) - limit} more -"
            " use the `facet_options` endpoint for the full list"
        )
    return text


def format_choice_list(
    vocabulary: dict[str, str],
    name: str,
    limit: int = 50,
) -> str:
    """Render a facet vocabulary as a readable choice list.

    Parameters
    ----------
    vocabulary : dict[str, str]
        Facet value codes mapped to their labels.
    name : str
        The filter parameter name, used in the overflow hint.
    limit : int
        Maximum number of choices to render.

    Returns
    -------
    str
        One indented ``code = label`` line per choice.
    """
    shown = sorted(vocabulary.items(), key=lambda item: item[1])[:limit]
    lines = [f"    {value} = {label}" for value, label in shown]
    if len(vocabulary) > limit:
        lines.append(
            f"    ... {len(vocabulary) - limit} more - use the `facet_options`"
            f" endpoint for the full '{name}' list."
        )
    return "\n".join(lines)


def resolve_facets(
    spec: dict[str, Any],
    frequency: str,
    values: dict[str, str | None],
    choices: dict[str, list[dict[str, str]]] | None = None,
) -> dict[str, list[str]]:
    """Map canonical facet parameters onto API facet ids for a dataset.

    Parameters
    ----------
    spec : dict[str, Any]
        Dataset specification.
    frequency : str
        Resolved frequency id, used for frequency-restricted facets.
    values : dict[str, str | None]
        Canonical facet parameter values as comma-separated strings.
    choices : dict[str, list[dict[str, str]]] | None
        The group's embedded facet choices. When present for a facet, values
        are validated against the vocabulary (case-insensitively, correcting
        the casing) and invalid values raise with the valid choices listed.

    Returns
    -------
    dict[str, list[str]]
        API facet id to list of filter values.
    """
    facets = spec["facets"]
    query: dict[str, list[str]] = {}
    for canonical, raw in values.items():
        if raw is None or raw == "":
            continue
        if canonical not in facets:
            applicable = ", ".join(facets) if facets else "none"
            raise OpenBBError(
                ValueError(
                    f"The '{canonical}' filter does not apply to '{spec['path']}'."
                    f" Applicable filters: {applicable}"
                )
            )
        restricted = facets[canonical].get("frequencies")
        if restricted and frequency not in restricted:
            raise OpenBBError(
                ValueError(
                    f"The '{canonical}' filter only applies to"
                    f" frequency: {', '.join(restricted)}"
                )
            )
        items = [item.strip() for item in str(raw).split(",") if item.strip()]
        embedded = facets[canonical].get("choices") or (choices or {}).get(canonical)
        if embedded:
            lookup: dict[str, list[str]] = {}
            for entry in embedded:
                lookup.setdefault(entry["value"].lower(), []).append(entry["value"])
                if entry.get("param"):
                    lookup.setdefault(entry["param"].lower(), []).append(entry["value"])
            corrected: list[str] = []
            invalid: list[str] = []
            for item in items:
                matches = lookup.get(item.lower())
                if matches is None:
                    invalid.append(item)
                else:
                    corrected.extend(code for code in matches if code not in corrected)
            if invalid:
                valid = sorted(
                    {entry.get("param") or entry["value"] for entry in embedded}
                )
                shown = ", ".join(valid[:50])
                if len(valid) > 50:
                    shown += (
                        f", plus {len(valid) - 50} more -"
                        " use the `facet_options` endpoint for the full list"
                    )
                raise OpenBBError(
                    ValueError(
                        f"Invalid {canonical} value(s): {', '.join(invalid)}."
                        f" Valid choices: {shown}"
                    )
                )
            items = corrected
        query[facets[canonical]["id"]] = items
    _apply_fixed_facets(facets, frequency, query, choices)
    return query


def _apply_fixed_facets(
    facets: dict[str, Any],
    frequency: str,
    query: dict[str, list[str]],
    choices: dict[str, list[dict[str, str]]] | None,
) -> None:
    """Filter on facets that have exactly one choice, which are never parameters.

    A facet with a single possible value is not a real filter, so the generated
    models do not expose it. The request must still carry it.
    """
    for canonical, detail in facets.items():
        if detail["id"] in query or not detail.get("filterable", True):
            continue
        restricted = detail.get("frequencies")
        if restricted and frequency not in restricted:
            continue
        fixed = detail.get("choices") or (choices or {}).get(canonical) or []
        if len(fixed) == 1:
            query[detail["id"]] = [fixed[0]["value"]]


def format_period(value: dateType, fmt: str, end: bool = False) -> str:
    """Format a date as an EIA period string.

    Parameters
    ----------
    value : datetime.date
        The date to convert.
    fmt : str
        EIA period format, e.g. 'YYYY-"Q"Q' or 'YYYY-MM-DD"T"HH24'.
    end : bool
        Unused placeholder kept for signature stability; period boundaries are
        inclusive on both ends in the EIA API.

    Returns
    -------
    str
        The period string, truncated to the dataset's granularity.
    """
    _ = end
    if fmt == "YYYY":
        return f"{value.year:04d}"
    if fmt == "YYYY-MM":
        return f"{value.year:04d}-{value.month:02d}"
    if fmt == 'YYYY-"Q"Q':
        return f"{value.year:04d}-Q{(value.month - 1) // 3 + 1}"
    if fmt == "YYYY-MM-DD":
        return value.strftime("%Y-%m-%d")
    if fmt.startswith('YYYY-MM-DD"T"HH24'):
        hour = value.hour if isinstance(value, datetime) else 0
        return f"{value.strftime('%Y-%m-%d')}T{hour:02d}"
    raise OpenBBError(ValueError(f"Unsupported EIA period format: {fmt}"))


def parse_period(value: str, fmt: str) -> dateType | datetime:
    """Parse an EIA period string into a date or datetime.

    Parameters
    ----------
    value : str
        The period string returned by the API.
    fmt : str
        EIA period format for the requested frequency.

    Returns
    -------
    datetime.date | datetime.datetime
        Period start as a date, or a datetime for hourly frequencies.
    """
    if fmt == "YYYY":
        return dateType(int(value), 1, 1)
    if fmt == "YYYY-MM":
        year, month = value.split("-")
        return dateType(int(year), int(month), 1)
    if fmt == 'YYYY-"Q"Q':
        year, quarter = value.split("-Q")
        return dateType(int(year), (int(quarter) - 1) * 3 + 1, 1)
    if fmt == "YYYY-MM-DD":
        return datetime.strptime(value, "%Y-%m-%d").date()
    if fmt.startswith('YYYY-MM-DD"T"HH24'):
        base = datetime.strptime(value[:13], "%Y-%m-%dT%H")
        offset = value[13:]
        if not offset:
            return base
        digits = offset[1:].replace(":", "")
        delta = timedelta(hours=int(digits[:2] or 0), minutes=int(digits[2:4] or 0))
        return base.replace(
            tzinfo=timezone(-delta if offset[0] == "-" else delta),
        )
    raise OpenBBError(ValueError(f"Unsupported EIA period format: {fmt}"))
