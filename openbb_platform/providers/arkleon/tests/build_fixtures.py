"""Reshape the supplied SEC companyfacts recording into contract-shaped fixtures."""

import json
import sys
from datetime import date
from pathlib import Path

# Direct script execution puts tests/ on sys.path, so include the package root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openbb_arkleon.models.balance_sheet import BALANCE_SHEET_TAGS
from openbb_arkleon.models.cash_flow import CASH_FLOW_TAGS
from openbb_arkleon.models.income_statement import INCOME_STATEMENT_TAGS


def build_fixtures(source: Path) -> None:
    """Write fixtures for exactly the tags, durations, and units requested."""
    companyfacts = json.loads(source.read_text())["facts"]["us-gaap"]
    output = Path(__file__).resolve().parent / "fixtures"
    output.mkdir(parents=True, exist_ok=True)
    requests = set()
    for tag_map, durations in (
        (BALANCE_SHEET_TAGS, (0,)),
        (INCOME_STATEMENT_TAGS, (1, 4)),
        (CASH_FLOW_TAGS, (1, 4)),
    ):
        for field, tags in tag_map.items():
            unit = "USD/shares" if field in ("eps_basic", "eps_diluted") else "USD"
            for tag in tags:
                for duration in durations:
                    requests.add((tag, duration, unit))

    def write(name: str, rows: list[dict], cursor=None) -> None:
        (output / name).write_text(
            json.dumps({"data": rows, "next_cursor": cursor}, indent=2) + "\n"
        )

    for tag, duration, unit in sorted(requests):
        rows = []
        entries = companyfacts.get(tag, {}).get("units", {}).get(unit, [])
        for entry in entries:
            quarters = (
                round(
                    (date.fromisoformat(entry["end"]) - date.fromisoformat(entry["start"])).days
                    / 91.3
                )
                if "start" in entry else 0
            )
            if quarters != duration or not "2019-01-01" <= entry["filed"] <= "2021-12-31":
                continue
            accession = entry["accn"]
            rows.append({
                "accession_id": accession,
                "tag": tag,
                "taxonomy": "us-gaap",
                "period_end": entry["end"],
                "duration_quarters": quarters,
                "unit": unit,
                "segments": "",
                "coreg": "",
                "value": entry["val"],
                "form": entry["form"],
                "filed": entry["filed"],
                "cik": 320193,
                "source_url": (
                    "https://www.sec.gov/Archives/edgar/data/320193/"
                    + accession.replace("-", "") + "/" + accession + "-index.htm"
                ),
            })
        if tag == "Assets":
            # Synthetic non-consolidated row, solely for testing segment exclusion.
            rows.append({**rows[0], "segments": "fixture-segment"})
        stem = f"facts_{tag}_{duration}_{unit.replace('/', '_')}"
        write(f"{stem}.json", rows)
        if tag == "Assets":
            midpoint = len(rows) // 2
            write(f"{stem}_page1.json", rows[:midpoint], "fixture-cursor-2")
            write(f"{stem}_page2.json", rows[midpoint:])


if __name__ == "__main__":
    build_fixtures(Path(sys.argv[1]))
