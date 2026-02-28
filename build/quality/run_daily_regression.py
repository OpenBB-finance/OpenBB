#!/usr/bin/env python3
"""Run daily OpenBB API regression checks for real business queries."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REQUIRED_META_KEYS = {
    "route",
    "provider_requested",
    "provider_used",
    "provider_candidates",
    "fallback_trace",
    "confidence",
    "selection_reason",
}


@dataclass
class CaseResult:
    """Normalized case execution result."""

    case_id: str
    ok: bool
    status_code: int | None
    provider_used: str | None
    result_size: int
    error: str | None
    checks: dict[str, bool]


def _load_cases(cases_file: Path) -> list[dict[str, Any]]:
    payload = json.loads(cases_file.read_text(encoding="utf-8"))
    return payload.get("cases", [])


def _result_size(results: Any) -> int:
    if isinstance(results, list):
        return len(results)
    if isinstance(results, dict):
        return len(results)
    if results is None:
        return 0
    return 1


def _http_get(url: str, timeout: int) -> tuple[int, dict[str, Any]]:
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:  # nosec B310
        return int(resp.status), json.loads(resp.read().decode("utf-8"))


def _run_case(base_url: str, case: dict[str, Any], timeout: int) -> CaseResult:
    params = case.get("params", {})
    expect = case.get("expect", {})
    query = urlencode(params)
    path = case["path"]
    url = f"{base_url.rstrip('/')}{path}?{query}" if query else f"{base_url.rstrip('/')}{path}"

    checks: dict[str, bool] = {
        "http_200": False,
        "non_empty_results": False,
        "meta_present": False,
        "meta_keys_complete": False,
        "provider_requested_match": False,
        "provider_used_match": False,
        "provider_used_in_candidates": False,
        "fallback_trace_valid": False,
        "fallback_trace_consistent": False,
        "confidence_valid": False,
        "selection_reason_present": False,
        "selection_mode_match": False,
    }

    try:
        status, payload = _http_get(url, timeout=timeout)
        checks["http_200"] = status == 200

        result_size = _result_size(payload.get("results"))
        checks["non_empty_results"] = result_size >= int(expect.get("min_results", 1))

        provider_used = payload.get("provider")
        meta = (payload.get("extra") or {}).get("meta")
        checks["meta_present"] = isinstance(meta, dict)

        if isinstance(meta, dict):
            checks["meta_keys_complete"] = REQUIRED_META_KEYS.issubset(meta.keys())
            provider_used = meta.get("provider_used") or provider_used
            expected_provider_requested = expect.get("expected_provider_requested")
            if expected_provider_requested:
                checks["provider_requested_match"] = (
                    str(meta.get("provider_requested")) == str(expected_provider_requested)
                )
            else:
                checks["provider_requested_match"] = True

            expected_provider_used = expect.get("expected_provider_used")
            if expected_provider_used:
                checks["provider_used_match"] = (
                    str(provider_used) == str(expected_provider_used)
                )
            else:
                checks["provider_used_match"] = True

            provider_candidates = meta.get("provider_candidates")
            checks["provider_used_in_candidates"] = (
                isinstance(provider_candidates, list)
                and len(provider_candidates) > 0
                and provider_used in provider_candidates
            )

            fallback_trace = meta.get("fallback_trace")
            checks["fallback_trace_valid"] = isinstance(fallback_trace, list) and len(fallback_trace) > 0
            if checks["fallback_trace_valid"]:
                last_step = fallback_trace[-1]
                checks["fallback_trace_consistent"] = (
                    isinstance(last_step, dict)
                    and last_step.get("status") == "success"
                    and last_step.get("provider") == provider_used
                )

            confidence = meta.get("confidence")
            checks["confidence_valid"] = isinstance(confidence, (int, float)) and 0 <= confidence <= 1

            selection_reason = meta.get("selection_reason")
            checks["selection_reason_present"] = isinstance(selection_reason, dict) and len(selection_reason) > 0
            expected_selection_mode = expect.get("expected_selection_mode")
            if expected_selection_mode:
                checks["selection_mode_match"] = (
                    checks["selection_reason_present"]
                    and str(selection_reason.get("mode")) == str(expected_selection_mode)
                )
            else:
                checks["selection_mode_match"] = checks["selection_reason_present"]

        ok = all(checks.values())
        return CaseResult(
            case_id=case["id"],
            ok=ok,
            status_code=status,
            provider_used=provider_used,
            result_size=result_size,
            error=None if ok else "One or more checks failed",
            checks=checks,
        )

    except HTTPError as exc:
        return CaseResult(
            case_id=case["id"],
            ok=False,
            status_code=exc.code,
            provider_used=None,
            result_size=0,
            error=f"HTTPError: {exc}",
            checks=checks,
        )
    except URLError as exc:
        return CaseResult(
            case_id=case["id"],
            ok=False,
            status_code=None,
            provider_used=None,
            result_size=0,
            error=f"URLError: {exc}",
            checks=checks,
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return CaseResult(
            case_id=case["id"],
            ok=False,
            status_code=None,
            provider_used=None,
            result_size=0,
            error=f"Unhandled: {exc}",
            checks=checks,
        )


def _write_report(
    output_dir: Path,
    base_url: str,
    cases: list[dict[str, Any]],
    results: list[CaseResult],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"daily_regression_{stamp}.md"

    passed = sum(1 for r in results if r.ok)
    total = len(results)

    lines: list[str] = []
    lines.append("# OpenBB Daily Regression Report")
    lines.append("")
    lines.append(f"- Time (UTC): {now.isoformat()}")
    lines.append(f"- Base URL: `{base_url}`")
    lines.append(f"- Passed: `{passed}/{total}`")
    lines.append("")
    lines.append("## Case Results")
    lines.append("")
    lines.append("| Case ID | Status | HTTP | Provider Used | Result Size | Error |")
    lines.append("|---|---|---:|---|---:|---|")

    for item in results:
        status = "PASS" if item.ok else "FAIL"
        http = "-" if item.status_code is None else str(item.status_code)
        provider = item.provider_used or "-"
        err = (item.error or "").replace("|", "/")
        lines.append(
            f"| `{item.case_id}` | `{status}` | {http} | `{provider}` | {item.result_size} | {err} |"
        )

    lines.append("")
    lines.append("## Check Matrix")
    lines.append("")
    for item in results:
        lines.append(f"### `{item.case_id}`")
        for check_name, check_ok in item.checks.items():
            marker = "PASS" if check_ok else "FAIL"
            lines.append(f"- `{check_name}`: `{marker}`")
        lines.append("")

    lines.append("## Case Questions")
    lines.append("")
    for case in cases:
        lines.append(f"- `{case['id']}`: {case.get('question_zh', '')} / {case.get('question_en', '')}")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OpenBB daily regression benchmark.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:6900",
        help="OpenBB API base URL, default: http://127.0.0.1:6900",
    )
    parser.add_argument(
        "--cases",
        default="build/quality/daily_regression_cases.json",
        help="Path to cases json file.",
    )
    parser.add_argument(
        "--output-dir",
        default="build/quality/reports",
        help="Directory for markdown reports.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout seconds per case.",
    )
    args = parser.parse_args()

    cases = _load_cases(Path(args.cases))
    if not cases:
        print("No cases found.", file=sys.stderr)
        return 2

    results = [_run_case(args.base_url, case, args.timeout) for case in cases]
    report_path = _write_report(Path(args.output_dir), args.base_url, cases, results)

    passed = sum(1 for r in results if r.ok)
    total = len(results)
    print(f"Daily regression finished: {passed}/{total} passed")
    print(f"Report: {report_path}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
