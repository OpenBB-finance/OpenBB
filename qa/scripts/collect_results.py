"""Collect verification artifacts and generate machine/human summaries."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


@dataclass
class JunitTotals:
    tests: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "tests": self.tests,
            "failures": self.failures,
            "errors": self.errors,
            "skipped": self.skipped,
        }


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _collect_junit_totals(run_dir: Path) -> JunitTotals:
    totals = JunitTotals()
    for xml_file in run_dir.rglob("*.xml"):
        try:
            root = ET.parse(xml_file).getroot()
        except ET.ParseError:
            continue

        suites = [root] if root.tag == "testsuite" else list(root.findall(".//testsuite"))
        for suite in suites:
            totals.tests += int(suite.attrib.get("tests", 0))
            totals.failures += int(suite.attrib.get("failures", 0))
            totals.errors += int(suite.attrib.get("errors", 0))
            totals.skipped += int(suite.attrib.get("skipped", 0))
    return totals


def _collect_quarantine(run_dir: Path) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    for report in run_dir.rglob("quarantine_report.json"):
        data = _load_json(report)
        if isinstance(data, dict):
            reports.append(data)

    core: set[str] = set()
    extended: set[str] = set()
    unknown_provider: set[str] = set()
    unknown_suite: set[str] = set()

    for report in reports:
        core.update(report.get("core_provider_failures", []))
        extended.update(report.get("extended_provider_failures", []))
        unknown_provider.update(report.get("unknown_provider_failures", []))
        unknown_suite.update(report.get("unknown_suite_failures", []))

    return {
        "report_count": len(reports),
        "core_provider_failures": sorted(core),
        "extended_provider_failures": sorted(extended),
        "unknown_provider_failures": sorted(unknown_provider),
        "unknown_suite_failures": sorted(unknown_suite),
    }


def _build_root_statuses(summary: dict[str, Any]) -> list[dict[str, Any]]:
    roots = summary.get("roots", [])
    rows: list[dict[str, Any]] = []
    for root in roots:
        gates = root.get("gates", [])
        counts = Counter(g.get("status", "UNKNOWN") for g in gates)
        rows.append(
            {
                "root_label": root.get("root_label", "unknown"),
                "root_path": root.get("root_path", ""),
                "overall_status": root.get("overall_status", "UNKNOWN"),
                "pass": counts.get("PASS", 0),
                "fail": counts.get("FAIL", 0),
                "warn": counts.get("WARN", 0),
                "skip": counts.get("SKIP", 0),
            }
        )
    return rows


def _render_markdown(summary: dict[str, Any], junit: JunitTotals, quarantine: dict[str, Any]) -> str:
    run_id = summary.get("run_id", "unknown")
    generated = summary.get("generated_at_utc", datetime.now(timezone.utc).isoformat())
    overall = summary.get("overall_status", "UNKNOWN")
    roots = _build_root_statuses(summary)

    lines: list[str] = []
    lines.append("# Full Verification Report")
    lines.append("")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append(f"- Generated (UTC): `{generated}`")
    lines.append(f"- Overall Status: `{overall}`")
    lines.append("")
    lines.append("## Root Gate Summary")
    lines.append("")
    lines.append("| Root | Path | Overall | PASS | FAIL | WARN | SKIP |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    for row in roots:
        lines.append(
            f"| `{row['root_label']}` | `{row['root_path']}` | `{row['overall_status']}` | "
            f"{row['pass']} | {row['fail']} | {row['warn']} | {row['skip']} |"
        )
    lines.append("")
    lines.append("## JUnit Totals")
    lines.append("")
    lines.append(f"- tests: `{junit.tests}`")
    lines.append(f"- failures: `{junit.failures}`")
    lines.append(f"- errors: `{junit.errors}`")
    lines.append(f"- skipped: `{junit.skipped}`")
    lines.append("")
    lines.append("## Quarantine Summary")
    lines.append("")
    lines.append(f"- reports: `{quarantine['report_count']}`")
    lines.append(f"- core provider failures: `{', '.join(quarantine['core_provider_failures']) or 'none'}`")
    lines.append(f"- extended provider failures: `{', '.join(quarantine['extended_provider_failures']) or 'none'}`")
    lines.append(f"- unknown provider failures: `{', '.join(quarantine['unknown_provider_failures']) or 'none'}`")
    lines.append(f"- unknown suite failures: `{', '.join(quarantine['unknown_suite_failures']) or 'none'}`")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `.` must satisfy required CI gates.")
    lines.append("- `OpenBB/` is validated locally and reported separately.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect verification results.")
    parser.add_argument("--run-dir", required=True, help="Run output directory, e.g. logs/verification/<run_id>")
    parser.add_argument("--output", required=True, help="Path to write JSON summary")
    parser.add_argument("--report", required=True, help="Path to write markdown report")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    summary_path = run_dir / "run_summary.json"
    summary = _load_json(summary_path)
    if not isinstance(summary, dict):
        raise FileNotFoundError(f"Missing run summary: {summary_path}")

    junit = _collect_junit_totals(run_dir)
    quarantine = _collect_quarantine(run_dir)
    root_rows = _build_root_statuses(summary)

    final = {
        "run_id": summary.get("run_id"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_status": summary.get("overall_status"),
        "run_summary_path": str(summary_path),
        "root_statuses": root_rows,
        "junit_totals": junit.as_dict(),
        "quarantine": quarantine,
    }

    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(final, indent=2), encoding="utf-8")

    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_markdown(summary, junit, quarantine), encoding="utf-8")

    print(f"Wrote JSON summary: {out_path}")
    print(f"Wrote markdown report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
