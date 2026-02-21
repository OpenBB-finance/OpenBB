"""Collect overnight Quant ML artifacts and render final report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def _tail_lines(path: Path, limit: int = 80) -> list[str]:
    if not path.exists():
        return []
    raw = path.read_bytes()
    text = ""
    decode_attempts: list[str] = []
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "cp949"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            decode_attempts.append(encoding)
            continue
    if not text:
        text = raw.decode("utf-8", errors="replace")
        text = f"[decode_fallback used after failures: {','.join(decode_attempts)}]\n{text}"
    lines = text.splitlines()
    return lines[-max(1, int(limit)) :]


def _render_markdown(
    session_id: str,
    session_dir: Path,
    recovery: dict[str, Any],
    checks: dict[str, Any],
    extra: dict[str, Any],
) -> str:
    check_rows = checks.get("checks", []) if isinstance(checks, dict) else []
    pass_count = sum(1 for item in check_rows if str(item.get("status")) == "PASS")
    fail_count = sum(1 for item in check_rows if str(item.get("status")) == "FAIL")
    failure_category = checks.get("failure_category")
    heartbeat_gap_sec_max = checks.get("heartbeat_gap_sec_max")
    registry_conflict_retries = checks.get("registry_conflict_retries")

    lines: list[str] = []
    lines.append("# Quant ML Overnight Final Report")
    lines.append("")
    lines.append(f"- Session ID: `{session_id}`")
    lines.append(f"- Generated (UTC): `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- Session Dir: `{session_dir}`")
    lines.append(f"- Overall Status: `{checks.get('overall_status', 'UNKNOWN')}`")
    lines.append(f"- failure_category: `{failure_category}`")
    lines.append(f"- heartbeat_gap_sec_max: `{heartbeat_gap_sec_max}`")
    lines.append(f"- registry_conflict_retries: `{registry_conflict_retries}`")
    lines.append("")
    lines.append("## Recovery")
    lines.append("")
    lines.append(f"- lock_removed: `{recovery.get('lock_removed')}`")
    lines.append(f"- lock_reason: `{recovery.get('lock_reason')}`")
    lines.append(f"- stale_runs_updated_count: `{recovery.get('stale_runs_updated_count')}`")
    lines.append(f"- active_runs_after: `{recovery.get('active_runs_after')}`")
    lines.append(
        f"- walkforward_queue_depth: `{recovery.get('walkforward_queue_depth')}`"
    )
    lines.append("")
    lines.append("## Verification Summary")
    lines.append("")
    lines.append(f"- pass: `{pass_count}`")
    lines.append(f"- fail: `{fail_count}`")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|---|---|---|")
    for row in check_rows:
        lines.append(
            f"| `{row.get('name', '')}` | `{row.get('status', '')}` | `{row.get('detail', '')}` |"
        )
    lines.append("")
    lines.append("## Runtime Artifacts")
    lines.append("")
    lines.append(f"- latest_bootstrap_run: `{extra.get('latest_bootstrap_run')}`")
    lines.append(f"- latest_training_run: `{extra.get('latest_training_run')}`")
    lines.append(f"- promoted_run_id: `{extra.get('promoted_run_id')}`")
    lines.append(f"- promoted_ready: `{extra.get('promoted_ready')}`")
    lines.append("")
    lines.append("## Timeline Tail")
    lines.append("")
    timeline_tail = _tail_lines(session_dir / "timeline.log", limit=80)
    if timeline_tail:
        lines.append("```text")
        lines.extend(timeline_tail)
        lines.append("```")
    else:
        lines.append("- (no timeline entries)")
    lines.append("")
    return "\n".join(lines) + "\n"


def _latest_run_id(prefix: str) -> str | None:
    root = Path.home() / ".openbb_platform" / "quant_ml" / "runs"
    if not root.exists():
        return None
    candidates = [item for item in root.iterdir() if item.is_dir() and item.name.startswith(prefix)]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0].name


def _promoted_payload() -> dict[str, Any]:
    path = Path.home() / ".openbb_platform" / "quant_ml" / "runtime" / "promoted_model.json"
    return _load_json(path, default={})


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Quant ML overnight report.")
    parser.add_argument("--session-dir", required=True)
    args = parser.parse_args()

    session_dir = Path(args.session_dir).resolve()
    session_id = session_dir.name
    session_dir.mkdir(parents=True, exist_ok=True)

    recovery = _load_json(session_dir / "recovery.json", default={})
    checks = _load_json(session_dir / "checks.json", default={})
    promoted = _promoted_payload()

    extra = {
        "latest_bootstrap_run": _latest_run_id("bst-"),
        "latest_training_run": _latest_run_id("trn-"),
        "promoted_run_id": promoted.get("run_id"),
        "promoted_ready": promoted.get("ready"),
    }

    payload = {
        "session_id": session_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "recovery": recovery,
        "checks": checks,
        "failure_category": checks.get("failure_category"),
        "heartbeat_gap_sec_max": checks.get("heartbeat_gap_sec_max"),
        "registry_conflict_retries": checks.get("registry_conflict_retries"),
        "extra": extra,
    }

    json_path = session_dir / "final_report.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = session_dir / "final_report.md"
    md_path.write_text(
        _render_markdown(session_id, session_dir, recovery, checks, extra),
        encoding="utf-8",
    )

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
