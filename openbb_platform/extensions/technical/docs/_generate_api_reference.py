"""Regenerate ``docs/api-reference.md`` from the live router catalog.

Run from the extension root:

    python docs/_generate_api_reference.py

The reference is auto-generated so that any new or modified endpoint is
reflected after a single command, without hand-editing the markdown.
"""

import pathlib
import re

from openbb import obb

_CLASS_PATTERN = re.compile(r"<class '([^']+)'>")

CATEGORY_ORDER: list[tuple[str, str, str]] = [
    (
        "overlay",
        "Overlays",
        "Price-smoothing and envelope indicators plotted on the same axis as price.",
    ),
    ("oscillator", "Oscillators", "Bounded momentum indicators."),
    ("trend", "Trend", "Direction and strength of the prevailing move."),
    ("volume", "Volume", "Volume-weighted indicators."),
    (
        "volatility",
        "Volatility",
        "Realised-volatility estimators and the ATR family.",
    ),
    ("structure", "Structure", "Price-action support/resistance levels."),
    ("stats", "Statistics", "Distributional and time-series diagnostics."),
    (
        "signal",
        "Signals",
        "Event detectors. Reachable under the `/signals/` URL prefix; in Python, via `obb.technical.signals.<name>`.",
    ),
    (
        "multi",
        "Multi-Symbol and Utility",
        "Cross-sectional, composition, and discovery endpoints.",
    ),
]


def type_str(t) -> str:
    """Render a Python type for the docs table."""
    if t is None:
        return ""
    s = str(t) if not isinstance(t, type) else t.__name__
    s = _CLASS_PATTERN.sub(lambda m: m.group(1).rsplit(".", 1)[-1], s)
    s = s.replace("typing.", "").replace("datetime.", "")
    return s.replace("|", "\\|")


def constraints_str(c: dict | None) -> str:
    if not c:
        return ""
    return ", ".join(f"`{k}={v}`" for k, v in c.items())


def cell(s: str | None) -> str:
    if not s:
        return ""
    return s.replace("|", "\\|").replace("\n", " ").strip()


def render() -> str:
    # ``obb.technical`` is generated at runtime by the static-package builder
    # and not visible to static type checkers.
    catalog = obb.technical.indicators(category="all").results  # ty: ignore[unresolved-attribute]
    entries = catalog.indicators
    by_cat: dict[str, list] = {}
    for entry in entries:
        by_cat.setdefault(entry.category, []).append(entry)

    out: list[str] = []
    out.append("# API Reference")
    out.append("")
    out.append(
        "Auto-generated from the registered router by "
        "`docs/_generate_api_reference.py`. Endpoint names match the Python "
        "interface (`obb.technical.<name>` or `obb.technical.signals.<name>`) "
        "and the HTTP path (`POST /api/v1/technical/<name>`)."
    )
    out.append("")
    out.append(f"**Total endpoints**: {len(entries)}")
    out.append("")
    out.append(
        "Each endpoint also takes `data` (the OHLC(V) price series) which is "
        "omitted from the parameter tables below. `requires_columns` lists "
        "the OHLC(V) columns the endpoint reads from `data`."
    )
    out.append("")
    out.append("---")
    out.append("")

    for cat_key, cat_title, cat_blurb in CATEGORY_ORDER:
        cat_entries = by_cat.get(cat_key, [])
        if not cat_entries:
            continue
        out.append(f"## {cat_title}")
        out.append("")
        out.append(cat_blurb)
        out.append("")
        for entry in sorted(cat_entries, key=lambda e: e.name):
            out.append(f"### `{entry.name}`")
            out.append("")
            first_line = (entry.description or "").strip().split("\n", 1)[
                0
            ] or "(no description)"
            out.append(f"_{first_line}_")
            out.append("")
            if entry.requires_columns:
                cols = ", ".join(f"`{c}`" for c in entry.requires_columns)
                out.append(f"**Required input columns**: {cols}")
                out.append("")

            if entry.params:
                out.append("**Parameters** (in addition to `data`):")
                out.append("")
                out.append("| Name | Type | Default | Constraints | Description |")
                out.append("|---|---|---|---|---|")
                for p in entry.params:
                    ptype = type_str(p.type)
                    if p.choices:
                        ptype = (
                            "Literal[" + ", ".join(f'"{c}"' for c in p.choices) + "]"
                        )
                    default = (
                        f"`{p.default}`" if p.default is not None else "*required*"
                    )
                    cons = constraints_str(p.constraints)
                    out.append(
                        f"| `{p.name}` | `{ptype}` | {default} | {cons} | "
                        f"{cell(p.description)} |"
                    )
                out.append("")

            if entry.output_columns:
                out.append(
                    "**Returns** — `OBBject` with `results` list of rows containing:"
                )
                out.append("")
                out.append("| Column | Type | Nullable | Description |")
                out.append("|---|---|---|---|")
                for o in entry.output_columns:
                    otype = type_str(o.type)
                    nullable = "yes" if o.nullable else "no"
                    out.append(
                        f"| `{o.name}` | `{otype}` | {nullable} | {cell(o.description)} |"
                    )
                out.append("")

    return "\n".join(out) + "\n"


def main() -> None:
    target = pathlib.Path(__file__).parent / "api-reference.md"
    target.write_text(render())


if __name__ == "__main__":
    main()
