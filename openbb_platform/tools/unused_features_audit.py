"""Generate an audit report for currently unused OpenBB features.

This script focuses on three drift vectors:
1) installed entry points vs `reference.json`
2) installed entry points vs `__extensions__.py`
3) desktop `quantApi.ts` / `macroApi.ts` exports vs actual route/component usage
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

ENTRY_POINT_GROUPS = (
    "openbb_core_extension",
    "openbb_provider_extension",
    "openbb_obbject_extension",
)


@dataclass(frozen=True)
class ExtensionDiff:
    """Diff summary for one extension source."""

    missing: list[str]
    stale: list[str]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _load_entry_points() -> dict[str, list[str]]:
    """Load installed entry points as `name@version` per group."""
    out: dict[str, list[str]] = {}
    for group in ENTRY_POINT_GROUPS:
        try:
            eps = importlib_metadata.entry_points(group=group)
        except TypeError:
            eps_all = importlib_metadata.entry_points()
            eps = eps_all.get(group, [])  # type: ignore[attr-defined]
        formatted: list[str] = []
        for ep in eps:
            version = ""
            try:
                dist = getattr(ep, "dist", None)
                version = getattr(dist, "version", "") if dist else ""
            except Exception:  # pragma: no cover - defensive
                version = ""
            formatted.append(f"{ep.name}@{version}")
        out[group] = sorted(set(formatted))
    return out


def _load_reference_extensions(reference_path: Path) -> dict[str, list[str]]:
    payload = _read_json(reference_path)
    ext_map = payload.get("info", {}).get("extensions", {})
    if not isinstance(ext_map, dict):
        return {group: [] for group in ENTRY_POINT_GROUPS}

    out: dict[str, list[str]] = {}
    for group in ENTRY_POINT_GROUPS:
        values = ext_map.get(group, [])
        if not isinstance(values, list):
            out[group] = []
            continue
        out[group] = sorted({str(item).strip() for item in values if str(item).strip()})
    return out


def _diff_lists(installed: list[str], declared: list[str]) -> ExtensionDiff:
    installed_set = set(installed)
    declared_set = set(declared)
    missing = sorted(installed_set - declared_set)
    stale = sorted(declared_set - installed_set)
    return ExtensionDiff(missing=missing, stale=stale)


def _parse_extensions_py_declared_names(extensions_py_path: Path) -> list[str]:
    """Extract declared extension names from `__extensions__.py` docstring list."""
    if not extensions_py_path.exists():
        return []
    text = extensions_py_path.read_text(encoding="utf-8")
    names = re.findall(r"-\s+([A-Za-z0-9_\-]+)@", text)
    return sorted(set(names))


def _entry_point_union_names(
    entry_points_by_group: dict[str, list[str]],
    groups: tuple[str, ...] = ("openbb_core_extension", "openbb_provider_extension"),
) -> list[str]:
    names: set[str] = set()
    for group in groups:
        values = entry_points_by_group.get(group, [])
        for item in values:
            names.add(item.split("@", 1)[0])
    return sorted(names)


def _extract_ts_export_functions(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"^\s*export function\s+([A-Za-z0-9_]+)\s*\(", text, flags=re.MULTILINE)))


def _find_ts_symbol_usages(symbol: str, source_root: Path, exclude: Path) -> list[str]:
    used_in: list[str] = []
    pattern = re.compile(rf"\b{re.escape(symbol)}\b")
    for path in source_root.rglob("*"):
        if not path.is_file():
            continue
        if path == exclude:
            continue
        if path.suffix.lower() not in {".ts", ".tsx"}:
            continue
        rel = path.relative_to(source_root.parent)
        if "tests" in rel.parts:
            continue
        content = path.read_text(encoding="utf-8")
        if pattern.search(content):
            used_in.append(str(rel).replace("\\", "/"))
    return sorted(used_in)


def _build_api_usage_report(api_file: Path, desktop_src: Path) -> dict[str, Any]:
    exports = _extract_ts_export_functions(api_file)
    usage_rows: list[dict[str, Any]] = []
    unused: list[str] = []
    for name in exports:
        used_in = _find_ts_symbol_usages(name, desktop_src, api_file)
        if not used_in:
            unused.append(name)
        usage_rows.append(
            {
                "name": name,
                "used": bool(used_in),
                "used_in": used_in,
            }
        )
    return {
        "file": str(api_file).replace("\\", "/"),
        "exports_total": len(exports),
        "unused_total": len(unused),
        "unused_exports": unused,
        "items": usage_rows,
    }


def _imports_desktop_api(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return re.search(r'from\s+"(?:\.\./)+lib/(quantApi|macroApi)"', text) is not None


def _estimate_unused_route_count(desktop_src: Path) -> int:
    """Heuristic route utilization check including delegated page components."""
    checks: dict[str, list[Path]] = {
        "quant": [desktop_src / "routes" / "quant.tsx"],
        "macro": [
            desktop_src / "routes" / "macro.tsx",
            desktop_src / "components" / "macro" / "MacroPage.tsx",
        ],
        "execution": [desktop_src / "routes" / "execution.tsx"],
        "ops": [desktop_src / "routes" / "ops.tsx"],
    }
    unused = 0
    for candidates in checks.values():
        if not any(path.exists() for path in candidates):
            unused += 1
            continue
        if not any(_imports_desktop_api(path) for path in candidates):
            unused += 1
    return unused


def _build_markdown_report(report: dict[str, Any]) -> str:
    ep = report["entry_points_vs_reference"]
    extensions = report["extensions_py_vs_entry_points"]
    desktop = report["desktop_api_usage"]
    metrics = report["metrics"]
    lines: list[str] = []
    lines.append("# Unused Features Audit")
    lines.append("")
    lines.append(f"- generated_at: `{report['generated_at']}`")
    lines.append(f"- repo_root: `{report['repo_root']}`")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append(f"- reference_drift: `{metrics['reference_drift']}`")
    lines.append(f"- extensions_py_drift: `{metrics['extensions_py_drift']}`")
    lines.append(f"- unused_api_exports: `{metrics['unused_api_exports']}`")
    lines.append(f"- unused_route_count: `{metrics['unused_route_count']}`")
    lines.append("")
    lines.append("## Entry Points vs Reference")
    lines.append("")
    for group in ENTRY_POINT_GROUPS:
        item = ep[group]
        lines.append(f"### {group}")
        lines.append(f"- installed: `{len(item['installed'])}`")
        lines.append(f"- reference: `{len(item['reference'])}`")
        lines.append(f"- missing_in_reference: `{len(item['missing_in_reference'])}`")
        lines.append(f"- stale_in_reference: `{len(item['stale_in_reference'])}`")
        lines.append("")
    lines.append("## __extensions__.py vs Entry Points")
    lines.append("")
    lines.append(f"- declared_names: `{len(extensions['declared_names'])}`")
    lines.append(f"- installed_names: `{len(extensions['installed_names'])}`")
    lines.append(f"- missing_in_extensions_py: `{len(extensions['missing_in_extensions_py'])}`")
    lines.append(f"- stale_in_extensions_py: `{len(extensions['stale_in_extensions_py'])}`")
    lines.append("")
    lines.append("## Desktop API Usage")
    lines.append("")
    for key in ("quantApi", "macroApi"):
        item = desktop[key]
        lines.append(f"### {key}")
        lines.append(f"- exports_total: `{item['exports_total']}`")
        lines.append(f"- unused_total: `{item['unused_total']}`")
        lines.append(f"- unused_exports: `{', '.join(item['unused_exports']) if item['unused_exports'] else '-'}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def generate_audit(repo_root: Path) -> dict[str, Any]:
    reference_path = repo_root / "openbb_platform" / "core" / "openbb" / "assets" / "reference.json"
    extensions_py_path = repo_root / "openbb_platform" / "core" / "openbb" / "package" / "__extensions__.py"
    desktop_src = repo_root / "desktop" / "src"
    quant_api = desktop_src / "lib" / "quantApi.ts"
    macro_api = desktop_src / "lib" / "macroApi.ts"

    entry_points_by_group = _load_entry_points()
    reference_by_group = _load_reference_extensions(reference_path)

    ep_report: dict[str, Any] = {}
    ref_drift_total = 0
    for group in ENTRY_POINT_GROUPS:
        diff = _diff_lists(entry_points_by_group[group], reference_by_group[group])
        ref_drift_total += len(diff.missing) + len(diff.stale)
        ep_report[group] = {
            "installed": entry_points_by_group[group],
            "reference": reference_by_group[group],
            "missing_in_reference": diff.missing,
            "stale_in_reference": diff.stale,
        }

    declared_names = _parse_extensions_py_declared_names(extensions_py_path)
    installed_names = _entry_point_union_names(entry_points_by_group)
    extensions_diff = _diff_lists(installed_names, declared_names)

    quant_usage = _build_api_usage_report(quant_api, desktop_src)
    macro_usage = _build_api_usage_report(macro_api, desktop_src)
    unused_api_exports = int(quant_usage["unused_total"]) + int(macro_usage["unused_total"])
    unused_route_count = _estimate_unused_route_count(desktop_src)

    report = {
        "generated_at": _utc_now(),
        "repo_root": str(repo_root).replace("\\", "/"),
        "entry_points_vs_reference": ep_report,
        "extensions_py_vs_entry_points": {
            "declared_names": declared_names,
            "installed_names": installed_names,
            "missing_in_extensions_py": extensions_diff.missing,
            "stale_in_extensions_py": extensions_diff.stale,
        },
        "desktop_api_usage": {
            "quantApi": quant_usage,
            "macroApi": macro_usage,
        },
        "metrics": {
            "reference_drift": ref_drift_total,
            "extensions_py_drift": len(extensions_diff.missing) + len(extensions_diff.stale),
            "unused_api_exports": unused_api_exports,
            "unused_route_count": unused_route_count,
        },
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate unused-features audit report.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--markdown-out", default="docs/unused-features-audit.md")
    parser.add_argument("--json-out", default="docs/unused-features-audit.json")
    parser.add_argument("--fail-on-drift", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = generate_audit(repo_root)
    markdown = _build_markdown_report(report)

    markdown_path = (repo_root / args.markdown_out).resolve()
    json_path = (repo_root / args.json_out).resolve()
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    metrics = report["metrics"]
    print(  # noqa: T201
        "unused-features-audit: "
        f"reference_drift={metrics['reference_drift']} "
        f"extensions_py_drift={metrics['extensions_py_drift']} "
        f"unused_api_exports={metrics['unused_api_exports']} "
        f"unused_route_count={metrics['unused_route_count']}"
    )

    if args.fail_on_drift:
        gate_failed = any(
            int(metrics[key]) > 0
            for key in ("reference_drift", "extensions_py_drift", "unused_api_exports", "unused_route_count")
        )
        if gate_failed:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
