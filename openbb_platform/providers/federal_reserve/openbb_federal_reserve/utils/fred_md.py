"""FRED-MD / FRED-QD series descriptions from the McCracken-Ng appendix."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "fred_md" / "descriptions.json"
)

_MEDIA = "https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md"
MD_APPENDIX_URL = (
    f"{_MEDIA}/fred-md_appendix0324.zip"
    "?sc_lang=en&hash=C8B84CF979313F21D9034FE68134E8EF"
)
QD_APPENDIX_URL = (
    f"{_MEDIA}/fred-qd_appendix0324.zip"
    "?sc_lang=en&hash=B237B1AB6F9AC21A5686190C60DE22AA"
)
_MD_MEMBER = "FRED-MD Appendix/FRED-MD_updated_appendix.csv"
_QD_MEMBER = "FRED-QD Appendix/FRED-QD_updated_appendix.csv"


@lru_cache(maxsize=1)
def load_descriptions() -> dict[str, dict[str, str]]:
    """Return the committed ``{frequency: {mnemonic: description}}`` mapping."""
    return json.loads(ASSET_PATH.read_text(encoding="utf-8"))


def _frequency(frequency: str) -> dict[str, str]:
    """Return the mnemonic-to-description map for a panel frequency."""
    return load_descriptions()[frequency]


def series_options(frequency: str) -> list[dict[str, str]]:
    """Return multiSelect options mapping each description to its series mnemonic."""
    return [
        {"label": description, "value": mnemonic}
        for mnemonic, description in _frequency(frequency).items()
    ]


def columns_defs(frequency: str) -> list[dict[str, Any]]:
    """Return table column definitions carrying a descriptive header per series."""
    defs: list[dict[str, Any]] = [
        {
            "field": "date",
            "headerName": "Date",
            "cellDataType": "date",
            "pinned": "left",
            "sort": "desc",
        }
    ]
    for mnemonic, description in _frequency(frequency).items():
        defs.append(
            {
                "field": mnemonic,
                "headerName": description,
                "headerTooltip": mnemonic,
                "cellDataType": "number",
            }
        )
    return defs


def _appendix_map(
    zip_bytes: bytes, member: str, mnemonic_col: str, description_col: str
) -> dict[str, str]:
    """Parse an appendix CSV from its zip into a lower-cased mnemonic map."""
    import csv
    import io
    import re
    import zipfile

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        text = archive.read(member).decode("cp1252")
    result: dict[str, str] = {}
    for row in csv.DictReader(io.StringIO(text)):
        mnemonic = (row.get(mnemonic_col) or "").strip()
        description = re.sub(r"\s+", " ", (row.get(description_col) or "").strip())
        if mnemonic:
            result[mnemonic.lower()] = description
    return result


def _align(header_line: str, appendix: dict[str, str]) -> dict[str, str]:
    """Map each panel column to its appendix description, keeping the panel casing."""
    columns = [c.strip() for c in header_line.split(",")[1:] if c.strip()]
    return {column: appendix.get(column.lower(), column) for column in columns}


def generate(
    md_bytes: bytes | None = None,
    qd_bytes: bytes | None = None,
    monthly_csv: str | None = None,
    quarterly_csv: str | None = None,
) -> dict[str, dict[str, str]]:
    """Build the descriptions mapping from the appendix zips and panel headers.

    Parameters
    ----------
    md_bytes, qd_bytes : bytes | None
        The FRED-MD and FRED-QD appendix zip contents; fetched when omitted.
    monthly_csv, quarterly_csv : str | None
        The panel CSV text whose header names the live columns; fetched when omitted.

    Returns
    -------
    dict[str, dict[str, str]]
        The ``{frequency: {mnemonic: description}}`` mapping aligned to the panels.
    """
    from openbb_federal_reserve.utils.st_louis import fetch_bytes, fetch_fred_panel

    md_bytes = md_bytes if md_bytes is not None else fetch_bytes(MD_APPENDIX_URL)
    qd_bytes = qd_bytes if qd_bytes is not None else fetch_bytes(QD_APPENDIX_URL)
    monthly = monthly_csv if monthly_csv is not None else fetch_fred_panel("monthly")
    quarterly = (
        quarterly_csv if quarterly_csv is not None else fetch_fred_panel("quarterly")
    )
    return {
        "monthly": _align(
            monthly.splitlines()[0],
            _appendix_map(md_bytes, _MD_MEMBER, "fred", "description"),
        ),
        "quarterly": _align(
            quarterly.splitlines()[0],
            _appendix_map(qd_bytes, _QD_MEMBER, "FRED MNEMONIC", "DESCRIPTION"),
        ),
    }


def write_asset(**kwargs: Any) -> Path:
    """Write the descriptions mapping to the committed asset path."""
    payload = generate(**kwargs)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    load_descriptions.cache_clear()
    return ASSET_PATH


def _main() -> None:
    """Regenerate the asset and print the series counts."""
    path = write_asset()
    data = load_descriptions()
    print(  # noqa: T201
        f"wrote {path}: monthly={len(data['monthly'])} "
        f"quarterly={len(data['quarterly'])}"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
