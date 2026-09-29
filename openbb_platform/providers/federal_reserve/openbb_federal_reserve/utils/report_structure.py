"""Shared Appendix A field-specification parsing for FFIEC report structures."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

MDRM = re.compile(r"\b[A-Z]{4}[A-Z0-9]{4}\b")

# both accepted.
LINE_REF = re.compile(
    r"^(?:(?:M|[A-Z])\.)?\d+(?:\.[a-z])*(?:\.\(\d+\))*(?:\([a-z]\))*\.?(?:;)?"
    r"|^[a-z]\."
)


def norm(line: str) -> str:
    """Lower-case and collapse whitespace for noise/banner comparison."""
    return re.sub(r"\s+", " ", line).strip().lower()


def level_from_reference(reference: str) -> int:
    """Derive the indent level from a line reference's nesting depth."""
    body = reference
    if re.fullmatch(r"[a-z]", body.rstrip(".")):
        return 2
    if body.startswith("M.") or re.match(r"^[A-Z]\.\d", body):
        body = body[2:]
    depth = 1
    depth += len(re.findall(r"\.[a-z](?![a-z])", body))
    depth += len(re.findall(r"\(\d+\)", body))
    depth += len(re.findall(r"\([a-z]\)", body))
    return depth


def level_from_caption(caption: str) -> int:
    """Infer an indent level for an unreferenced section header from its bullet."""
    token = caption.split(" ", 1)[0]
    if re.match(r"^\([a-z]\)", token):
        return 4
    if re.match(r"^\(\d+\)", token):
        return 3
    if re.match(r"^[a-z]\.", token):
        return 2
    return 1


def split_reference(line: str) -> tuple[str | None, str]:
    """Split a logical row into its line reference and caption text."""
    match = LINE_REF.match(line)
    if not match or not match.group(0).rstrip(".;"):
        return None, line
    reference = match.group(0).rstrip(";").rstrip(".")
    caption = line[match.end() :].strip()
    return reference, caption


_DOUBLED_REF = re.compile(
    r"^((?:M|[A-Z])\.\S+|\d+(?:\.[a-z])*(?:\.\(\d+\))*(?:\([a-z]\))*\.?)\s+\1\s"
)

_STRAY_LEADER = re.compile(r"^[a-z](M\.\d)")


def collapse_doubled(line: str) -> str:
    """Collapse a doubled leading line reference and strip a stray ref leader."""
    line = _STRAY_LEADER.sub(r"\1", line)
    match = _DOUBLED_REF.match(line)
    if not match:
        return line
    return f"{match.group(1)} {line[match.end() :]}".strip()


def starts_new_row(line: str) -> bool:
    """Return ``True`` when a line opens a new numbered report row."""
    match = LINE_REF.match(collapse_doubled(line))
    if not match or not match.group(0).rstrip(".;"):
        return False
    return line[match.end() : match.end() + 1] in {"", " "}


def is_not_applicable(line: str) -> bool:
    """Return ``True`` for a ``"Not applicable"`` placeholder line."""
    _, caption = split_reference(line)
    return clean_caption(caption).lower() == "not applicable" or (
        clean_caption(line).lower() == "not applicable"
    )


@dataclass
class ReportConfig:
    """The per-report knobs that drive the shared Appendix A parser.

    Parameters
    ----------
    appendix_banner : str
        The normalized (lower-cased, whitespace-collapsed) "Detailed Field
        Specifications" banner that opens the field-specification listing.
    schedule_header : re.Pattern[str]
        Matches a schedule banner line, capturing the schedule code (group 1)
        and its name (group 2).
    noise : set[str]
        Normalized page running heads and column banners dropped entirely.
    appendix_end : str | None
        The normalized banner of the table that follows the form (e.g. FR Y-9C
        Appendix B); extraction stops there. ``None`` reads to end of document.
    first_schedule : tuple[str, str] | None
        The ``(code, name)`` of an implicit opening schedule used until the
        first banner. ``None`` starts unscheduled (every schedule is bannered).
    cover_schedule : tuple[str, str]
        The ``(code, name)`` placeholder schedule active before any banner.
    is_note_prose : Callable[[str], bool] | None
        Returns ``True`` for an instructional-prose line/block to drop rather
        than emit as a spurious section header.
    """

    appendix_banner: str
    schedule_header: re.Pattern[str]
    noise: set[str] = field(default_factory=set)
    appendix_end: str | None = None
    first_schedule: tuple[str, str] | None = None
    cover_schedule: tuple[str, str] = ("COVER", "Cover Page")
    is_note_prose: Callable[[str], bool] | None = None


def read_pdf_pages(pdf_bytes: bytes) -> list[str]:
    """Return each PDF page's extracted text, using the shared pdfplumber reader."""
    import io

    import pdfplumber

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def pdf_lines(pdf_bytes: bytes, config: ReportConfig) -> list[str]:
    """Extract the appendix text as a flat list of stripped, non-empty lines."""
    lines: list[str] = []
    in_appendix = False
    for text in read_pdf_pages(pdf_bytes):
        normalized = "".join(char for char in text if char != "­")
        for raw in normalized.splitlines():
            stripped = raw.strip()
            if not stripped:
                continue
            if not in_appendix:
                if norm(stripped) == config.appendix_banner:
                    in_appendix = True
                continue
            if (
                config.appendix_end is not None
                and norm(stripped) == config.appendix_end
            ):
                return lines
            lines.append(stripped)
    return lines


def is_noise(line: str, config: ReportConfig) -> bool:
    """Return ``True`` for page running heads, banners, and bare page numbers."""
    lowered = norm(line)
    if lowered in config.noise:
        return True
    if re.fullmatch(r"\d+", line.strip()):
        return True
    if lowered.startswith("8-character"):
        return True
    return line.strip() == "-"


def clean_caption(caption: str) -> str:
    """Collapse whitespace and strip data-type prefixes and filler dashes."""
    caption = re.sub(r"\s+", " ", caption).strip()
    caption = re.sub(r"^(?:TEXT|INTEGER|PERCENT|DATE|NUMBER)\s+", "", caption)
    caption = caption.rstrip(" -").strip()
    return caption


def is_codes_only(line: str) -> bool:
    """Return ``True`` when a line is solely MDRM codes (a detached column row)."""
    if not MDRM.search(line):
        return False
    return not MDRM.sub("", line).strip()


def is_header_line(line: str) -> bool:
    """Return ``True`` when a code-less line is a space-dash continuation header."""
    return bool(re.search(r"\s-$", line)) and not MDRM.search(line)


def opens_wrapped_item(line: str) -> bool:
    """Return ``True`` when a code-less line is the first line of a wrapped item."""
    reference, _ = split_reference(line)
    body = line.rstrip().rstrip("*").rstrip()
    return reference is not None and not body.endswith(":")


def _flush_row(  # noqa: PLR0913
    schedule: str,
    schedule_name: str,
    reference: str | None,
    caption: str,
    codes: list[str],
    items: list[dict[str, Any]],
) -> None:
    """Append one parsed logical row to ``items``."""
    caption = clean_caption(caption)
    if not caption:
        return
    if (
        codes
        and all(code.startswith("TEXT") for code in codes)
        and re.search(r"\bDescription\b", caption)
    ):
        return
    is_header = not codes
    if reference is not None:
        level = level_from_reference(reference)
    else:
        level = level_from_caption(caption)
    items.append(
        {
            "schedule": schedule,
            "schedule_name": schedule_name,
            "line": reference,
            "caption": caption,
            "mdrm": codes[0] if codes else None,
            "columns": codes or None,
            "level": level,
            "is_header": is_header,
        }
    )


def parse_structure(pdf_bytes: bytes, config: ReportConfig) -> list[dict[str, Any]]:
    """Parse an Appendix A field-specification listing into ordered report items.

    Parameters
    ----------
    pdf_bytes : bytes
        The raw Reporting Central user guide PDF.
    config : ReportConfig
        The per-report banners, noise, schedule pattern and prose filter.

    Returns
    -------
    list[dict[str, Any]]
        One record per logical report line in form order, each with the keys
        ``schedule``, ``schedule_name``, ``line``, ``caption``, ``mdrm``,
        ``columns``, ``level`` and ``is_header``. Itemization free-text
        ``TEXTxxxx`` descriptions and instructional prose are dropped.
    """
    lines = pdf_lines(pdf_bytes, config)
    items: list[dict[str, Any]] = []
    schedule, schedule_name = config.cover_schedule
    seen_first_schedule = config.first_schedule is None
    pending: list[str] = []

    def flush_pending() -> None:
        """Resolve the buffered physical lines into one logical row."""
        nonlocal pending
        if not pending:
            return
        joined = " ".join(pending)
        codes = MDRM.findall(joined)
        if not codes and config.is_note_prose and config.is_note_prose(joined):
            pending = []
            return
        reference, caption = split_reference(MDRM.sub("", joined).strip())
        _flush_row(schedule, schedule_name, reference, caption, codes, items)
        pending = []

    def opens_row(line: str) -> bool:
        """Return ``True`` when ``line`` opens a new row, not a wrapped fragment."""
        if not starts_new_row(line):
            return False
        buffered = " ".join(pending)
        return buffered.count("(") <= buffered.count(")")

    for raw_line in lines:
        line = collapse_doubled(re.sub(r"\s+", " ", raw_line).strip())
        if not line or is_noise(line, config):
            flush_pending()
            continue

        header_match = config.schedule_header.match(line)
        if header_match and not MDRM.search(line):
            flush_pending()
            schedule = header_match.group(1)
            name = clean_caption(header_match.group(2)).lstrip("- ").strip()
            schedule_name = name or schedule
            seen_first_schedule = True
            continue

        if (
            not seen_first_schedule
            and config.first_schedule is not None
            and not re.match(r"^(?:TEXT|INTEGER|PERCENT|DATE|NUMBER)\b", line)
        ):
            flush_pending()
            schedule, schedule_name = config.first_schedule
            seen_first_schedule = True

        if re.match(r"^(?:(?:M|[A-Z])\.\S+\s+)?TEXT\b", line) and not re.search(
            r"\b(?:BH|RSSD)", line
        ):
            flush_pending()
            continue

        if not MDRM.search(line) and is_not_applicable(line):
            flush_pending()
            continue

        if MDRM.search(line):
            if pending and opens_row(line):
                flush_pending()
            pending.append(line)
            flush_pending()
            continue

        if is_header_line(line):
            flush_pending()
            reference, caption = split_reference(line)
            _flush_row(schedule, schedule_name, reference, caption, [], items)
            continue

        if pending and not opens_row(line):
            pending.append(line)
            continue
        if pending:
            flush_pending()
        if opens_wrapped_item(line) or (
            config.is_note_prose and config.is_note_prose(line)
        ):
            pending.append(line)
        else:
            pending.append(line)
            flush_pending()

    flush_pending()
    return items


def summarize(items: list[dict[str, Any]], source: str) -> dict[str, Any]:
    """Wrap parsed items with the schedule summary for the committed asset."""
    schedules: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        code = item["schedule"]
        if code not in seen:
            seen.add(code)
            schedules.append({"schedule": code, "name": item["schedule_name"]})
    return {
        "source": source,
        "schedule_count": len(schedules),
        "item_count": len(items),
        "schedules": schedules,
        "items": items,
    }
