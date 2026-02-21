[CmdletBinding()]
param(
  [string]$OutputDir = "",
  [string]$PythonExe = ".\\.venv\\Scripts\\python.exe",
  [int]$StaleMinutes = 30,
  [int]$LockTtlHours = 6,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

function Ensure-Directory([string]$PathValue) {
  if (-not (Test-Path -LiteralPath $PathValue)) {
    New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
  }
}

function Resolve-OutputDirectory([string]$PathValue) {
  if ([string]::IsNullOrWhiteSpace($PathValue)) {
    return Join-Path (Get-Location).Path "logs/overnight/manual"
  }
  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return [System.IO.Path]::GetFullPath($PathValue)
  }
  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $PathValue))
}

if ($null -eq (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
  throw "Python executable not found: $PythonExe"
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\\.."))
if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
  $env:PYTHONPATH = "openbb_platform/extensions/quant_ml"
}

$resolvedOutputDir = Resolve-OutputDirectory $OutputDir
Ensure-Directory $resolvedOutputDir
$recoveryPath = Join-Path $resolvedOutputDir "recovery.json"

$pyCode = @'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from openbb_quant_ml.service.run_index import rebuild_runs_index
from openbb_quant_ml.service.storage import write_registry
from openbb_quant_ml.jobs.lock import inspect_lock

try:
    from openbb_quant_ml.service.ops_status import get_ops_status_response
except Exception:
    get_ops_status_response = None


def pid_alive(pid):
    if pid is None or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def parse_iso(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def has_recent_progress(run_dir: Path, stale_minutes: int, now_utc: datetime):
    if not run_dir.exists():
        return False
    mtimes = []
    for path in run_dir.iterdir():
        if not path.is_file():
            continue
        name = path.name
        tracked = (
            (name.startswith("predictions") and name.endswith(".parquet"))
            or (name.startswith("metrics") and name.endswith(".json"))
            or (name.startswith("backtest") and name.endswith(".json"))
            or name.startswith("model_")
        )
        if tracked:
            mtimes.append(datetime.fromtimestamp(path.stat().st_mtime, timezone.utc))
    if not mtimes:
        return False
    last = max(mtimes)
    return ((now_utc - last).total_seconds() / 60.0) < float(stale_minutes)


def main():
    stale_minutes = int(sys.argv[1])
    lock_ttl_hours = int(sys.argv[2])
    dry_run = bool(int(sys.argv[3]))

    root = Path.home() / ".openbb_platform" / "quant_ml"
    reg_path = root / "registry.json"
    lock_path = root / ".locks" / "bootstrap.lock"
    now = datetime.now(timezone.utc)

    result = {
        "timestamp_utc": now.replace(microsecond=0).isoformat(),
        "dry_run": dry_run,
        "lock_path": str(lock_path),
        "lock_removed": False,
        "lock_reason": "",
        "target_job_lock_health": "missing",
        "lock_health_detail": {},
        "stale_runs_marked": [],
        "active_runs_after": 0,
        "walkforward_queue_depth": None,
    }

    lock_info = inspect_lock(lock_path, stale_ttl_sec=lock_ttl_hours * 3600)
    result["lock_health_detail"] = lock_info
    result["target_job_lock_health"] = str(lock_info.get("health", "missing"))

    if lock_path.exists():
        stale = bool(lock_info.get("stale", False))
        if stale:
            result["lock_reason"] = str(lock_info.get("reason") or "pid_dead_or_ttl_expired")
            if not dry_run:
                try:
                    lock_path.unlink(missing_ok=True)
                    result["lock_removed"] = True
                except PermissionError:
                    result["lock_removed"] = False
                    result["lock_reason"] = "lock_in_use_permission_denied"
                    result["target_job_lock_health"] = "in_use"
                except OSError as exc:
                    result["lock_removed"] = False
                    result["lock_reason"] = f"lock_remove_failed:{exc.__class__.__name__}"
            else:
                result["lock_removed"] = True
        else:
            result["lock_reason"] = "active_lock_kept"
            result["target_job_lock_health"] = "ok"
    else:
        result["lock_reason"] = "lock_missing"
        result["target_job_lock_health"] = "missing"

    payload = {"runs": {}}
    if reg_path.exists():
        payload = json.loads(reg_path.read_text(encoding="utf-8"))
    runs = payload.get("runs", {})
    if not isinstance(runs, dict):
        runs = {}

    updated = 0
    for run_id, row in list(runs.items()):
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).lower()
        if status not in {"queued", "running"}:
            continue
        ts = parse_iso(row.get("updated_at") or row.get("created_at"))
        age_min = ((now - ts).total_seconds() / 60.0) if ts is not None else 999999.0
        if age_min < float(stale_minutes):
            continue
        run_dir = root / "runs" / str(run_id)
        recent_progress = has_recent_progress(run_dir, stale_minutes=stale_minutes, now_utc=now)
        should_mark = (status == "queued") or (status == "running" and not recent_progress)
        if not should_mark:
            continue
        result["stale_runs_marked"].append(
            {
                "run_id": str(run_id),
                "previous_status": status,
                "age_minutes": round(age_min, 3),
                "had_recent_progress": recent_progress,
            }
        )
        if not dry_run:
            row["status"] = "failed"
            row["stage"] = "failed_stale"
            row["progress"] = 100
            row["error"] = "failed_stale_run_cleanup"
            row["updated_at"] = now.replace(microsecond=0).isoformat()
            logs = row.get("logs_tail", [])
            if not isinstance(logs, list):
                logs = []
            logs.append("Run was marked failed by overnight stale-run cleanup.")
            row["logs_tail"] = logs[-200:]
            runs[str(run_id)] = row
            updated += 1

    payload["runs"] = runs
    if not dry_run:
        write_registry(payload)
        rebuild_runs_index()

    active_after = 0
    for row in runs.values():
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).lower() in {"queued", "running"}:
            active_after += 1
    result["active_runs_after"] = active_after
    result["stale_runs_updated_count"] = updated if not dry_run else len(result["stale_runs_marked"])

    if get_ops_status_response is not None:
        try:
            ops = get_ops_status_response()
            result["walkforward_queue_depth"] = int(ops.walkforward_queue_depth)
        except Exception:
            result["walkforward_queue_depth"] = None

    # Final lock health snapshot after potential cleanup.
    final_lock = inspect_lock(lock_path, stale_ttl_sec=lock_ttl_hours * 3600)
    result["lock_health_detail"] = final_lock
    if not final_lock.get("exists", False):
        result["target_job_lock_health"] = "missing"
    elif str(final_lock.get("health", "")) == "ok":
        result["target_job_lock_health"] = "ok"
    elif result["lock_reason"] == "lock_in_use_permission_denied":
        result["target_job_lock_health"] = "in_use"
    else:
        result["target_job_lock_health"] = str(final_lock.get("health", "stale"))

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
'@

Push-Location $repoRoot
try {
  $oldErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    $jsonLine = $pyCode | & $PythonExe - "$StaleMinutes" "$LockTtlHours" "$([int]$DryRun.IsPresent)"
  } finally {
    $ErrorActionPreference = $oldErrorActionPreference
  }
  if ($LASTEXITCODE -ne 0) {
    throw "state recovery python helper failed with exit code $LASTEXITCODE"
  }
  $jsonText = ($jsonLine | Select-Object -Last 1)
  if ([string]::IsNullOrWhiteSpace($jsonText)) {
    throw "empty recovery result from python helper"
  }
  $obj = $jsonText | ConvertFrom-Json
  $obj | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $recoveryPath -Encoding UTF8
  Write-Host "Recovery report written: $recoveryPath"
  Write-Host "active_runs_after=$($obj.active_runs_after), lock_removed=$($obj.lock_removed), stale_runs_updated_count=$($obj.stale_runs_updated_count)"
} finally {
  Pop-Location
}
