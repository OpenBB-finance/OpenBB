"""Parser for the Federal Reserve Data Download Program (DDP) SDMX-ML feed."""

from __future__ import annotations

import re
from typing import Any
from xml.etree.ElementTree import Element, ParseError

from defusedxml.ElementTree import fromstring

_PURE_SEASONAL = {"SA", "SAAR", "NSA"}


def _seasonal_flag(code: str) -> bool | None:
    """Map a dimension code to a seasonal-adjustment boolean, where it carries one."""
    if re.match(r"NSA($|_)", code):
        return False
    if re.match(r"SAAR$", code) or re.match(r"SA($|_)", code):
        return True
    return None


MISSING_VALUES = {"-9999", "-99999", "-9999.99", "-99999.99"}

_NON_DIMENSION_ATTRS = {"SERIES_NAME", "FREQ", "UNIT", "UNIT_MULT", "CURRENCY"}

_NO_SCALE_MULTIPLIERS = {"", "1", "1.0", "One", "Units", "Not Applicable"}


def _scale_word(unit_mult: str | None, labels: dict[str, str]) -> str | None:
    """Resolve a ``UNIT_MULT`` factor to its scale word (``Millions``), else ``None``."""
    if not unit_mult:
        return None
    key = unit_mult
    try:
        as_float = float(unit_mult)
        if as_float == int(as_float):
            key = str(int(as_float))
    except ValueError:
        key = unit_mult
    word = labels.get(key, labels.get(unit_mult, ""))
    if not word or word in _NO_SCALE_MULTIPLIERS:
        return None
    return word


_NON_SCALABLE_KEYWORDS = (
    "percent",
    "index",
    "rate",
    "ratio",
    "basis point",
)

_COUNT_LABELS = {"number", "count", "units", "unit"}

_BASE_YEAR_RE = re.compile(r"base\s*=?\s*(\d{4})", re.IGNORECASE)


def _currency_noun(currency_label: str | None) -> str | None:
    """Reduce a currency codelist label to its plural noun (``Dollars``), else ``None``."""
    if not currency_label or currency_label == "Not Applicable":
        return None
    name = currency_label.rsplit("/", 1)[-1].split("(")[0].strip()
    if not name:
        return None
    if name.endswith("Dollar"):
        return "Dollars"
    words = name.split()
    words[-1] = words[-1] if words[-1].endswith("s") else words[-1] + "s"
    return " ".join(words)


def _unit_label(
    unit: str | None,
    currency: str | None,
    scale: str | None,
    codelists: dict[str, dict[str, str]],
) -> str | None:
    """Build a human-readable unit label, e.g. ``"Millions of Dollars"``."""
    unit_labels = codelists.get("unit", {})
    currency_labels = codelists.get("currency", {})
    resolved = unit_labels.get(unit, unit) if unit else None
    if resolved and resolved.lower().startswith("currency"):
        noun = _currency_noun(currency_labels.get(currency, currency)) or "Dollars"
        base = _BASE_YEAR_RE.search(resolved)
        suffix = f" ({base.group(1)} base)" if base else ""
        label = f"{scale} of {noun}" if scale else noun
        return f"{label}{suffix}"
    if not resolved:
        return f"{scale}" if scale else None
    lowered = resolved.lower()
    if any(keyword in lowered for keyword in _NON_SCALABLE_KEYWORDS):
        return resolved
    if not scale:
        return resolved
    if lowered in _COUNT_LABELS:
        return scale
    return f"{scale} of {resolved}"


def _local(tag: str) -> str:
    """Strip the XML namespace from a tag name."""
    return tag.rsplit("}", 1)[-1]


def _annotations(series_el: Element) -> dict[str, str]:
    """Collect a series' annotations keyed by snake-cased annotation type."""
    out: dict[str, str] = {}
    for ann in series_el.iter():
        if _local(ann.tag) != "Annotation":
            continue
        a_type = a_text = ""
        for child in ann:
            name = _local(child.tag)
            if name == "AnnotationType":
                a_type = (child.text or "").strip()
            elif name == "AnnotationText":
                a_text = (child.text or "").strip()
        if a_type:
            out[a_type.lower().replace(" ", "_")] = a_text
    return out


def _observation(obs_el: Element) -> dict[str, Any]:
    """Parse one ``Obs`` element, mapping missing sentinels to ``None``."""
    attrib = obs_el.attrib
    raw = attrib.get("OBS_VALUE")
    status = attrib.get("OBS_STATUS", "")
    if raw is None or status == "ND" or raw in MISSING_VALUES:
        value: float | None = None
    else:
        try:
            value = float(raw)
        except ValueError:
            value = None
    return {
        "date": attrib.get("TIME_PERIOD"),
        "value": value,
        "status": status or None,
    }


def parse_series(xml_text: str) -> list[dict[str, Any]]:
    """Parse a DDP SDMX-ML document into series with metadata and observations.

    Parameters
    ----------
    xml_text : str
        The raw SDMX-ML payload returned by the DDP ``Output.aspx`` endpoint.

    Returns
    -------
    list[dict[str, Any]]
        One entry per series with ``series_id``, ``title``, ``description``,
        ``frequency``, ``unit``, ``unit_multiplier``, ``currency``,
        ``dimensions``, and ``observations``.
    """
    if not xml_text or not xml_text.strip():
        return []
    root = fromstring(xml_text)
    results: list[dict[str, Any]] = []

    for el in root.iter():
        if _local(el.tag) != "Series":
            continue
        attrib = dict(el.attrib)
        series_id = attrib.get("SERIES_NAME")
        if not series_id:
            continue
        freq = attrib.get("FREQ")
        annotations = _annotations(el)
        observations = [_observation(o) for o in el if _local(o.tag) == "Obs"]
        results.append(
            {
                "series_id": series_id,
                "title": annotations.get("short_description") or series_id,
                "description": (
                    annotations.get("long_description")
                    or annotations.get("short_description")
                    or ""
                ),
                "frequency": freq,
                "unit": attrib.get("UNIT"),
                "unit_multiplier": attrib.get("UNIT_MULT"),
                "currency": attrib.get("CURRENCY"),
                "dimensions": {
                    key.lower(): value
                    for key, value in attrib.items()
                    if key not in _NON_DIMENSION_ATTRS
                },
                "observations": observations,
            }
        )

    return results


def parse_structure(xml_text: str) -> dict[str, dict[str, str]]:
    """Parse a DDP structure file into each dimension's codelist labels."""
    if not xml_text or not xml_text.strip():
        return {}
    try:
        root = fromstring(xml_text.lstrip("﻿"))
    except ParseError:
        return {}

    codelists: dict[str, dict[str, str]] = {}
    for code_list in root.iter():
        if _local(code_list.tag) != "CodeList":
            continue
        codes: dict[str, str] = {}
        for code in code_list:
            if _local(code.tag) != "Code":
                continue
            value = code.get("value")
            description = next(
                (
                    (child.text or "").strip()
                    for child in code
                    if _local(child.tag) == "Description"
                ),
                "",
            )
            if value is not None:
                codes[value] = description
        identifier = code_list.get("id")
        if identifier:
            codelists[identifier] = codes

    concepts: dict[str, dict[str, str]] = {}
    for element in root.iter():
        if _local(element.tag) not in ("Dimension", "Attribute"):
            continue
        concept = element.get("concept")
        codelist = element.get("codelist")
        if concept and codelist in codelists:
            concepts[concept.lower()] = codelists[codelist]
    return concepts


def to_rows(
    series: list[dict[str, Any]],
    codelists: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """Flatten parsed series into long-format observation rows."""
    codelists = codelists or {}
    freq_labels = codelists.get("freq", {})
    unit_mult_labels = codelists.get("unit_mult", {})
    rows: list[dict[str, Any]] = []
    for entry in series:
        dimensions: dict[str, Any] = {}
        seasonally_adjusted: bool | None = None
        for dimension, code in entry["dimensions"].items():
            if seasonally_adjusted is None:
                seasonally_adjusted = _seasonal_flag(code)
            labels = codelists.get(dimension, {})
            if labels and set(labels).issubset(_PURE_SEASONAL):
                continue
            dimensions[dimension] = labels.get(code, code)
        dimensions["seasonally_adjusted"] = seasonally_adjusted
        scale = _scale_word(entry.get("unit_multiplier"), unit_mult_labels)
        unit = _unit_label(entry.get("unit"), entry.get("currency"), scale, codelists)
        for obs in entry["observations"]:
            rows.append(
                {
                    "date": obs["date"],
                    "series_id": entry["series_id"],
                    "value": obs["value"],
                    "title": entry["title"],
                    "frequency": freq_labels.get(
                        entry["frequency"], entry["frequency"]
                    ),
                    "unit": unit,
                    "unit_multiplier": scale,
                    **dimensions,
                }
            )
    return rows
