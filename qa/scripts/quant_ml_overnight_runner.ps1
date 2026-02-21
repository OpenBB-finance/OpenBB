[CmdletBinding()]
param(
  [string]$SessionId = "",
  [string]$OutputBaseDir = "logs/overnight",
  [string]$RepoRoot = ".",
  [string]$PythonExe = ".\\.venv\\Scripts\\python.exe",
  [string]$ConfigPath = "openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs_overnight.yaml",
  [string]$ApiBaseUrl = "http://127.0.0.1:6900",
  [int]$PollSeconds = 120,
  [int]$StallMinutes = 25,
  [switch]$EnablePush,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

function Resolve-Abs([string]$PathValue) {
  if ([string]::IsNullOrWhiteSpace($PathValue)) {
    return (Get-Location).Path
  }
  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return [System.IO.Path]::GetFullPath($PathValue)
  }
  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $PathValue))
}

function Ensure-Directory([string]$PathValue) {
  if (-not (Test-Path -LiteralPath $PathValue)) {
    New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
  }
}

function Write-Timeline([string]$Message) {
  $stamp = (Get-Date).ToUniversalTime().ToString("o")
  $line = "[$stamp] $Message"
  Add-Content -LiteralPath $timelinePath -Value $line -Encoding UTF8
  Write-Host $line
}

function Write-LogTailToTimeline(
  [string]$Label,
  [string]$PathValue,
  [int]$TailLines = 80
) {
  if ([string]::IsNullOrWhiteSpace($PathValue) -or -not (Test-Path -LiteralPath $PathValue)) {
    Write-Timeline "$Label tail unavailable: $PathValue"
    return
  }
  Write-Timeline "$Label tail begin ($PathValue)"
  Get-Content -LiteralPath $PathValue -Tail $TailLines | ForEach-Object {
    Write-Timeline "$Label> $_"
  }
  Write-Timeline "$Label tail end"
}

function Add-Phase(
  [System.Collections.Generic.List[object]]$List,
  [string]$Phase,
  [string]$Status,
  [string]$Detail
) {
  $List.Add([pscustomobject]@{
      timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
      phase = $Phase
      status = $Status
      detail = $Detail
    })
}

function Save-PhaseChecks(
  [System.Collections.Generic.List[object]]$List,
  [string]$OutputPath
) {
  $payload = [pscustomobject]@{
    session_id = $SessionId
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    checks = @($List.ToArray())
  }
  $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}

function Run-CommandWithLog(
  [string]$Name,
  [string]$Command,
  [scriptblock]$Action,
  [string]$LogPath,
  [switch]$ExecuteInDryRun
) {
  Ensure-Directory (Split-Path -Parent $LogPath)
  if ($DryRun -and -not $ExecuteInDryRun) {
    Set-Content -LiteralPath $LogPath -Value "DRY RUN: $Command"
    Write-Timeline "$Name PASS (dry-run)"
    return [pscustomobject]@{ success = $true; exit_code = 0; log = $LogPath }
  }
  $start = Get-Date
  $exit = 0
  $oldErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    & $Action
    $exit = [int]$LASTEXITCODE
  } catch {
    $_ | Out-String | Tee-Object -FilePath $LogPath -Append | Out-Null
    $exit = 1
  } finally {
    $ErrorActionPreference = $oldErrorActionPreference
  }
  $secs = ((Get-Date) - $start).TotalSeconds
  if ($exit -eq 0) {
    Write-Timeline "$Name PASS (${secs}s)"
    return [pscustomobject]@{ success = $true; exit_code = 0; log = $LogPath }
  }
  Write-Timeline "$Name FAIL (${secs}s, exit=$exit)"
  return [pscustomobject]@{ success = $false; exit_code = $exit; log = $LogPath }
}

function Invoke-PythonJson(
  [string]$PyCode,
  [string[]]$PyArgs
) {
  $oldErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    $lines = $PyCode | & $PythonExe - @PyArgs
  } finally {
    $ErrorActionPreference = $oldErrorActionPreference
  }
  if ($LASTEXITCODE -ne 0) {
    throw "Python helper failed with exit code $LASTEXITCODE"
  }
  $jsonText = ($lines | Select-Object -Last 1)
  if ([string]::IsNullOrWhiteSpace($jsonText)) {
    throw "Python helper returned empty output"
  }
  return ($jsonText | ConvertFrom-Json)
}

function Build-ProfileConfig(
  [string]$BaseConfig,
  [string]$ProfileName,
  [string]$OutputConfig
) {
  $pyCode = @'
import json
import sys
from pathlib import Path
import yaml

base = Path(sys.argv[1])
profile = sys.argv[2]
out = Path(sys.argv[3])
cfg = yaml.safe_load(base.read_text(encoding="utf-8")) or {}
profiles = cfg.get("overnight_profiles", {})
overrides = profiles.get(profile, {})
if not isinstance(overrides, dict):
    overrides = {}
for section, patch in overrides.items():
    if isinstance(patch, dict):
        current = cfg.get(section, {})
        if not isinstance(current, dict):
            current = {}
        current.update(patch)
        cfg[section] = current
    else:
        cfg[section] = patch
cfg.pop("overnight_profiles", None)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
print(json.dumps({"ok": True, "profile": profile, "output": str(out)}))
'@
  $null = Invoke-PythonJson $pyCode @($BaseConfig, $ProfileName, $OutputConfig)
}

function Get-TrainingRunIds() {
  $pyCode = @'
import json
from pathlib import Path
p = Path.home()/".openbb_platform"/"quant_ml"/"registry.json"
if not p.exists():
    print(json.dumps({"run_ids": []}))
    raise SystemExit(0)
obj = json.loads(p.read_text(encoding="utf-8"))
runs = obj.get("runs", {})
ids = sorted([k for k in runs.keys() if str(k).startswith("trn-")])
print(json.dumps({"run_ids": ids}))
'@
  $obj = Invoke-PythonJson $pyCode @()
  return @($obj.run_ids)
}

function Get-LatestActiveRunFingerprint() {
  $pyCode = @'
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home()/".openbb_platform"/"quant_ml"/"registry.json"
if not p.exists():
    print(json.dumps({
        "run_id": None,
        "status": None,
        "stage": None,
        "progress": None,
        "updated_at": None,
        "file_count": 0,
        "max_mtime": 0.0,
    }))
    raise SystemExit(0)
obj = json.loads(p.read_text(encoding="utf-8"))
runs = obj.get("runs", {})
rows = []
for rid, row in runs.items():
    if not isinstance(row, dict):
        continue
    st = str(row.get("status", "")).lower()
    if st not in {"queued", "running"}:
        continue
    ts = str(row.get("updated_at") or row.get("created_at") or "")
    rows.append((ts, str(rid), st, row))
if not rows:
    print(json.dumps({
        "run_id": None,
        "status": None,
        "stage": None,
        "progress": None,
        "updated_at": None,
        "file_count": 0,
        "max_mtime": 0.0,
    }))
    raise SystemExit(0)
rows.sort(key=lambda item: item[0], reverse=True)
ts, rid, st, row = rows[0]
run_dir = Path.home()/".openbb_platform"/"quant_ml"/"runs"/rid
files = [x for x in run_dir.iterdir() if x.is_file()] if run_dir.exists() else []
max_mtime = max((f.stat().st_mtime for f in files), default=0.0)
print(json.dumps({
    "run_id": rid,
    "status": st,
    "stage": row.get("stage"),
    "progress": row.get("progress"),
    "updated_at": ts,
    "file_count": len(files),
    "max_mtime": max_mtime
}))
'@
  return Invoke-PythonJson $pyCode @()
}

function Invoke-MonitoredBootstrap(
  [string]$ConfigFile,
  [string]$RunName
) {
  $stdoutLog = Join-Path $sessionDir "$RunName.stdout.log"
  $stderrLog = Join-Path $sessionDir "$RunName.stderr.log"
  Ensure-Directory (Split-Path -Parent $stdoutLog)

  if ($DryRun) {
    Set-Content -LiteralPath $stdoutLog -Value "DRY RUN: $PythonExe -m openbb_quant_ml.jobs.cli bootstrap --config $ConfigFile"
    Set-Content -LiteralPath $stderrLog -Value ""
    return [pscustomobject]@{ success = $true; stalled = $false; exit_code = 0; stdout = $stdoutLog; stderr = $stderrLog }
  }

  $argList = "-m openbb_quant_ml.jobs.cli bootstrap --config `"$ConfigFile`""
  $proc = Start-Process -FilePath $PythonExe -ArgumentList $argList -WorkingDirectory $repoAbs -PassThru -NoNewWindow -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog
  Write-Timeline "$RunName started (pid=$($proc.Id))"

  $lastFingerprint = ""
  $idleSince = $null
  $stalled = $false
  while (-not $proc.HasExited) {
    Start-Sleep -Seconds $PollSeconds
    $state = Get-LatestActiveRunFingerprint
    $currentFingerprint = ""
    if ($null -ne $state -and -not [string]::IsNullOrWhiteSpace([string]$state.run_id)) {
      $currentFingerprint = "$($state.run_id)|$($state.status)|$($state.progress)|$($state.file_count)|$($state.max_mtime)|$($state.updated_at)"
      Write-Timeline "$RunName monitor run_id=$($state.run_id) status=$($state.status) progress=$($state.progress) files=$($state.file_count)"
    } else {
      Write-Timeline "$RunName monitor active_run=none"
    }

    if ([string]::IsNullOrWhiteSpace($currentFingerprint)) {
      $idleSince = $null
      $lastFingerprint = ""
      continue
    }

    if ($currentFingerprint -eq $lastFingerprint) {
      if ($null -eq $idleSince) {
        $idleSince = Get-Date
      }
      $idleMinutes = ((Get-Date) - $idleSince).TotalMinutes
      if ($idleMinutes -ge $StallMinutes) {
        Write-Timeline "$RunName stall detected (idle=${idleMinutes}m) -> terminating process"
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $stalled = $true
        break
      }
    } else {
      $lastFingerprint = $currentFingerprint
      $idleSince = $null
    }
  }

  if (-not $proc.HasExited) {
    try {
      $proc.WaitForExit(2000) | Out-Null
    } catch {
      # no-op
    }
  }
  $exitCode = if ($stalled) { 124 } else { [int]$proc.ExitCode }
  return [pscustomobject]@{
    success = (-not $stalled) -and ($exitCode -eq 0)
    stalled = $stalled
    exit_code = $exitCode
    stdout = $stdoutLog
    stderr = $stderrLog
  }
}

function Test-UniverseQuality() {
  $pyCode = @'
import json
from pathlib import Path
import pandas as pd

base = Path("openbb_platform/extensions/quant_ml/openbb_quant_ml/universe")
russ = base / "russell1000.csv"
allin = base / "all_in_one.csv"
if not russ.exists() or not allin.exists():
    print(json.dumps({"ok": False, "error": "missing_universe_csv"}))
    raise SystemExit(0)

r = pd.read_csv(russ)
a = pd.read_csv(allin)
rset = sorted(set(str(x).strip().upper() for x in r["symbol"].tolist() if str(x).strip()))
aset = sorted(set(str(x).strip().upper() for x in a["symbol"].tolist() if str(x).strip()))
blocked = {"SPY","QQQ","IVV","VOO","DIA","IWM","SOXX","SMH"}
must = {"TLT","IEF","GLD","DBC","UUP","FXE"}
blocked_present = sorted([x for x in blocked if x in set(aset)])
must_missing = sorted([x for x in must if x not in set(aset)])
ok = (len(rset) >= 900) and (len(aset) >= 1200) and (not blocked_present) and (not must_missing)
print(json.dumps({
    "ok": ok,
    "russell1000_unique": len(rset),
    "all_in_one_unique": len(aset),
    "blocked_present": blocked_present,
    "must_missing": must_missing
}))
'@
  return Invoke-PythonJson $pyCode @()
}

function Ensure-PromotedPointer() {
  $pyCode = @'
import json
from pathlib import Path

from openbb_quant_ml.service.constants import PROMOTED_MODEL_PATH
from openbb_quant_ml.service.runtime_pointer import get_promoted_model, set_promoted_model_pointer

payload = get_promoted_model(model_name="lgbm_ranker")
run_id = payload.get("run_id")
if run_id and (not PROMOTED_MODEL_PATH.exists() or payload.get("source") != "runtime_pointer"):
    set_promoted_model_pointer(run_id=str(run_id), model_name="lgbm_ranker", source="overnight_manual_promote")
payload = get_promoted_model(model_name="lgbm_ranker")
print(json.dumps(payload, ensure_ascii=False))
'@
  return Invoke-PythonJson $pyCode @()
}

function Get-NewItems([string[]]$Before, [string[]]$After) {
  $beforeSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
  foreach ($item in $Before) { $null = $beforeSet.Add([string]$item) }
  $newItems = [System.Collections.Generic.List[string]]::new()
  foreach ($item in $After) {
    if (-not $beforeSet.Contains([string]$item)) {
      $newItems.Add([string]$item)
    }
  }
  return @($newItems.ToArray())
}

function Get-LatestDailyRuns([datetime]$SinceTime, [int]$Limit = 2) {
  $root = Join-Path $HOME ".openbb_platform\\quant_ml\\runs"
  if (-not (Test-Path -LiteralPath $root)) {
    return @()
  }
  $rows = Get-ChildItem -LiteralPath $root -Directory | Where-Object {
    $_.Name -like "dly-*" -and $_.LastWriteTime -ge $SinceTime
  } | Sort-Object LastWriteTime -Descending | Select-Object -First $Limit
  return @($rows | ForEach-Object { $_.FullName })
}

if ([string]::IsNullOrWhiteSpace($SessionId)) {
  $SessionId = Get-Date -Format "overnight-yyMMdd-HHmm"
}

$repoAbs = Resolve-Abs $RepoRoot
$configAbs = Resolve-Abs $ConfigPath
$outBaseAbs = Resolve-Abs $OutputBaseDir
$sessionDir = Join-Path $outBaseAbs $SessionId
Ensure-Directory $sessionDir
$timelinePath = Join-Path $sessionDir "timeline.log"
$runnerChecksPath = Join-Path $sessionDir "runner_checks.json"

if ($null -eq (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
  throw "Python executable not found: $PythonExe"
}

if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
  $env:PYTHONPATH = "openbb_platform/extensions/quant_ml"
}

$phases = [System.Collections.Generic.List[object]]::new()
Write-Timeline "session_start session_id=$SessionId"

Push-Location $repoAbs
try {
  # Phase 0
  $baselineLog = Join-Path $sessionDir "phase0_baseline.log"
  if ($DryRun) {
    Set-Content -LiteralPath $baselineLog -Value "DRY RUN"
  } else {
    @(
      "=== git status --short ===",
      (& git status --short),
      "=== latest runs ===",
      (& powershell -NoProfile -Command "Get-ChildItem `"$HOME\.openbb_platform\quant_ml\runs`" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 8 Name,LastWriteTime | Format-Table -AutoSize | Out-String"),
      "=== lock files ===",
      (& powershell -NoProfile -Command "Get-ChildItem `"$HOME\.openbb_platform\quant_ml\.locks`" -ErrorAction SilentlyContinue | Select-Object Name,LastWriteTime | Format-Table -AutoSize | Out-String")
    ) | Set-Content -LiteralPath $baselineLog -Encoding UTF8
  }
  Add-Phase $phases "phase0_baseline" "PASS" $baselineLog
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 1
  Write-Timeline "phase1_recover_state start"
  $recoverScript = Join-Path $repoAbs "qa/scripts/quant_ml_recover_state.ps1"
  $recoverLog = Join-Path $sessionDir "phase1_recover_state.log"
  $recoverResult = Run-CommandWithLog "phase1_recover_state" `
    "$recoverScript -OutputDir $sessionDir -PythonExe $PythonExe" `
    { & $recoverScript -OutputDir $sessionDir -PythonExe $PythonExe -StaleMinutes 30 -LockTtlHours 6 -DryRun:$DryRun 2>&1 | Tee-Object -FilePath $recoverLog | Out-Host } `
    $recoverLog `
    -ExecuteInDryRun
  if (-not $recoverResult.success) {
    Add-Phase $phases "phase1_recover_state" "FAIL" "recover script failed"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase1_recover_state failed"
  }
  $recoveryFile = Join-Path $sessionDir "recovery.json"
  $recoveryPayload = Get-Content -LiteralPath $recoveryFile -Raw -Encoding UTF8 | ConvertFrom-Json
  if ((-not $DryRun) -and ([int]$recoveryPayload.active_runs_after -ne 0)) {
    Write-Timeline "phase1_recover_state active runs remain -> aggressive cleanup pass (stale_minutes=5)"
    $recoverLog2 = Join-Path $sessionDir "phase1_recover_state_retry.log"
    $recoverResult2 = Run-CommandWithLog "phase1_recover_state_retry" `
      "$recoverScript -OutputDir $sessionDir -PythonExe $PythonExe -StaleMinutes 5 -LockTtlHours 6" `
      { & $recoverScript -OutputDir $sessionDir -PythonExe $PythonExe -StaleMinutes 5 -LockTtlHours 6 -DryRun:$false 2>&1 | Tee-Object -FilePath $recoverLog2 | Out-Host } `
      $recoverLog2
    if (-not $recoverResult2.success) {
      Add-Phase $phases "phase1_recover_state" "FAIL" "aggressive cleanup retry failed"
      Save-PhaseChecks $phases $runnerChecksPath
      throw "phase1_recover_state retry failed"
    }
    $recoveryPayload = Get-Content -LiteralPath $recoveryFile -Raw -Encoding UTF8 | ConvertFrom-Json
  }
  if ((-not $DryRun) -and ([int]$recoveryPayload.active_runs_after -ne 0)) {
    Add-Phase $phases "phase1_recover_state" "FAIL" "active_runs_after=$($recoveryPayload.active_runs_after)"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase1 gate failed: active runs remain"
  }
  $lockHealth = [string]($recoveryPayload.target_job_lock_health)
  if ((-not $DryRun) -and ($lockHealth -notin @("ok", "missing"))) {
    Add-Phase $phases "phase1_recover_state" "FAIL" "target_job_lock_health=$lockHealth"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase1 gate failed: lock health is $lockHealth"
  }
  if ($DryRun) {
    Add-Phase $phases "phase1_recover_state" "PASS" ("dry_run_active_runs_after=" + [string]$recoveryPayload.active_runs_after + ",lock_health=" + [string]$recoveryPayload.target_job_lock_health)
  } else {
    Add-Phase $phases "phase1_recover_state" "PASS" ("active_runs_after=0,lock_health=" + [string]$recoveryPayload.target_job_lock_health)
  }
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 2
  Write-Timeline "phase2_preflight start"
  $preflightLog = Join-Path $sessionDir "phase2_preflight.log"
  $preflightOk = $true
  if ($DryRun) {
    Set-Content -LiteralPath $preflightLog -Value "DRY RUN"
  } else {
    try {
      @(
        (& $PythonExe --version),
        (& node --version),
        (& npm --version),
        (& $PythonExe -c "import openbb_quant_ml, yaml, pandas; print('python_import_ok')")
      ) | Set-Content -LiteralPath $preflightLog -Encoding UTF8
    } catch {
      $_ | Out-String | Set-Content -LiteralPath $preflightLog -Encoding UTF8
      $preflightOk = $false
    }
  }
  if (-not $preflightOk) {
    Add-Phase $phases "phase2_preflight" "FAIL" $preflightLog
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase2 preflight failed"
  }
  Add-Phase $phases "phase2_preflight" "PASS" $preflightLog
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 3
  Write-Timeline "phase3_universe_refresh start"
  $refreshLog = Join-Path $sessionDir "phase3_universe_refresh.log"
  $refreshOk = $false
  for ($attempt = 1; $attempt -le 2; $attempt++) {
    $cmdResult = Run-CommandWithLog "phase3_universe_refresh_attempt_$attempt" `
      "$PythonExe -m openbb_quant_ml.tools.refresh_universes --only russell1000 all_in_one --no-validate" `
      { & $PythonExe -m openbb_quant_ml.tools.refresh_universes --only russell1000 all_in_one --no-validate 2>&1 | Tee-Object -FilePath $refreshLog -Append | Out-Host } `
      $refreshLog
    if ($cmdResult.success) {
      $q = Test-UniverseQuality
      $q | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $sessionDir "phase3_universe_quality.json") -Encoding UTF8
      if ($q.ok) {
        $refreshOk = $true
        break
      }
    }
    Write-Timeline "phase3 attempt=$attempt failed; retrying"
  }
  if (-not $refreshOk) {
    Add-Phase $phases "phase3_universe_refresh" "FAIL" "universe quality failed after retry"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase3 failed"
  }
  Add-Phase $phases "phase3_universe_refresh" "PASS" "russell>=900 and all_in_one>=1200"
  Save-PhaseChecks $phases $runnerChecksPath

  # Build profile configs
  $canaryCfg = Join-Path $sessionDir "ops_jobs_canary.yaml"
  $fullCfg = Join-Path $sessionDir "ops_jobs_full.yaml"
  Build-ProfileConfig $configAbs "canary" $canaryCfg
  Build-ProfileConfig $configAbs "full" $fullCfg

  # Phase 4 canary
  Write-Timeline "phase4_canary_bootstrap start"
  $trnBeforeCanary = Get-TrainingRunIds
  $canaryRun = Invoke-MonitoredBootstrap -ConfigFile $canaryCfg -RunName "phase4_canary_bootstrap"
  if (-not $canaryRun.success) {
    Write-LogTailToTimeline "phase4_stdout" $canaryRun.stdout 80
    Write-LogTailToTimeline "phase4_stderr" $canaryRun.stderr 80
    Add-Phase $phases "phase4_canary_bootstrap" "FAIL" "exit=$($canaryRun.exit_code), stalled=$($canaryRun.stalled)"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase4 canary failed"
  }
  $trnAfterCanary = Get-TrainingRunIds
  $newCanaryRuns = Get-NewItems $trnBeforeCanary $trnAfterCanary
  if ((-not $DryRun) -and ((@($newCanaryRuns)).Count -lt 1)) {
    Add-Phase $phases "phase4_canary_bootstrap" "FAIL" "no new trn-* run detected"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase4 canary produced no training run"
  }
  if ($DryRun) {
    Add-Phase $phases "phase4_canary_bootstrap" "PASS" "dry_run_skip_new_trn_check"
  } else {
    Add-Phase $phases "phase4_canary_bootstrap" "PASS" ("new_runs=" + ($newCanaryRuns -join ","))
  }
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 5 full bootstrap with one retry
  Write-Timeline "phase5_full_bootstrap start"
  $trnBeforeFull = Get-TrainingRunIds
  $fullOk = $false
  for ($attempt = 1; $attempt -le 2; $attempt++) {
    $fullRun = Invoke-MonitoredBootstrap -ConfigFile $fullCfg -RunName ("phase5_full_bootstrap_attempt_" + $attempt)
    if ($fullRun.success) {
      $fullOk = $true
      break
    }
    Write-LogTailToTimeline ("phase5_attempt_${attempt}_stdout") $fullRun.stdout 80
    Write-LogTailToTimeline ("phase5_attempt_${attempt}_stderr") $fullRun.stderr 80
    Write-Timeline "phase5 attempt=$attempt failed (stall=$($fullRun.stalled), exit=$($fullRun.exit_code))"
    if ($attempt -lt 2) {
      & (Join-Path $repoAbs "qa/scripts/quant_ml_recover_state.ps1") -OutputDir $sessionDir -PythonExe $PythonExe -StaleMinutes 30 -LockTtlHours 6 -DryRun:$DryRun | Out-Host
    }
  }
  if (-not $fullOk) {
    Add-Phase $phases "phase5_full_bootstrap" "FAIL" "full bootstrap failed after retry"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase5 full bootstrap failed"
  }
  $trnAfterFull = Get-TrainingRunIds
  $newFullRuns = Get-NewItems $trnBeforeFull $trnAfterFull
  Add-Phase $phases "phase5_full_bootstrap" "PASS" ("new_runs=" + ($newFullRuns -join ","))
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 6 promoted pointer
  Write-Timeline "phase6_promote_pointer start"
  $promoted = Ensure-PromotedPointer
  $promoted | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $sessionDir "phase6_promoted.json") -Encoding UTF8
  if ((-not $DryRun) -and ((-not $promoted.ready) -or [string]::IsNullOrWhiteSpace([string]$promoted.run_id))) {
    Add-Phase $phases "phase6_promote_pointer" "FAIL" "promoted ready=false or run_id missing"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase6 failed"
  }
  if ($DryRun) {
    Add-Phase $phases "phase6_promote_pointer" "PASS" ("dry_run_ready=" + [string]$promoted.ready + ",run_id=" + [string]$promoted.run_id)
  } else {
    Add-Phase $phases "phase6_promote_pointer" "PASS" ("run_id=" + [string]$promoted.run_id)
  }
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 7 verification suite
  Write-Timeline "phase7_verify_full start"
  $verifyScript = Join-Path $repoAbs "qa/scripts/quant_ml_verify_full.ps1"
  $verifyLog = Join-Path $sessionDir "phase7_verify_full.log"
  $verifyRun = Run-CommandWithLog "phase7_verify_full" `
    "$verifyScript -SessionId $SessionId -OutputDir $sessionDir -RepoRoot $repoAbs -PythonExe $PythonExe -ApiBaseUrl $ApiBaseUrl" `
    { & $verifyScript -SessionId $SessionId -OutputDir $sessionDir -RepoRoot $repoAbs -PythonExe $PythonExe -ApiBaseUrl $ApiBaseUrl -DryRun:$DryRun 2>&1 | Tee-Object -FilePath $verifyLog | Out-Host } `
    $verifyLog `
    -ExecuteInDryRun
  if (-not $verifyRun.success) {
    Add-Phase $phases "phase7_verify_full" "FAIL" "verification suite failed"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase7 failed"
  }
  Add-Phase $phases "phase7_verify_full" "PASS" "checks.json generated"
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 8 daily infer-only twice
  Write-Timeline "phase8_daily_infer start"
  $trnBeforeDaily = Get-TrainingRunIds
  $dailyStart = Get-Date
  $dailyLog = Join-Path $sessionDir "phase8_daily.log"
  $d1 = Run-CommandWithLog "phase8_daily_run_1" "$PythonExe -m openbb_quant_ml.jobs.cli daily --config $fullCfg" `
    { & $PythonExe -m openbb_quant_ml.jobs.cli daily --config $fullCfg 2>&1 | Tee-Object -FilePath $dailyLog -Append | Out-Host } `
    $dailyLog
  $d2 = Run-CommandWithLog "phase8_daily_run_2" "$PythonExe -m openbb_quant_ml.jobs.cli daily --config $fullCfg" `
    { & $PythonExe -m openbb_quant_ml.jobs.cli daily --config $fullCfg 2>&1 | Tee-Object -FilePath $dailyLog -Append | Out-Host } `
    $dailyLog
  if (-not ($d1.success -and $d2.success)) {
    Add-Phase $phases "phase8_daily_infer" "FAIL" "daily command failed"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase8 failed"
  }
  $trnAfterDaily = Get-TrainingRunIds
  $newDailyTrn = Get-NewItems $trnBeforeDaily $trnAfterDaily
  if ((@($newDailyTrn)).Count -gt 0) {
    Add-Phase $phases "phase8_daily_infer" "FAIL" ("daily created training runs: " + ($newDailyTrn -join ","))
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase8 failed: daily retraining detected"
  }
  $latestDailyRuns = Get-LatestDailyRuns -SinceTime $dailyStart -Limit 2
  $predictSecs = @()
  foreach ($runPath in $latestDailyRuns) {
    $tp = Join-Path $runPath "time_profile.json"
    if (Test-Path -LiteralPath $tp) {
      $obj = Get-Content -LiteralPath $tp -Raw -Encoding UTF8 | ConvertFrom-Json
      if ($null -ne $obj.predict) {
        if ($obj.predict -is [double] -or $obj.predict -is [int] -or $obj.predict -is [decimal]) {
          $predictSecs += [double]$obj.predict
        } elseif ($null -ne $obj.predict.elapsed_sec) {
          $predictSecs += [double]$obj.predict.elapsed_sec
        }
      }
    }
  }
  if ($predictSecs.Count -gt 0 -and ($predictSecs | Measure-Object -Maximum).Maximum -gt 180) {
    Add-Phase $phases "phase8_daily_infer" "FAIL" ("predict latency exceeded 180s: " + (($predictSecs | ForEach-Object { [Math]::Round($_, 3) }) -join ","))
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase8 failed: predict latency"
  }
  Add-Phase $phases "phase8_daily_infer" "PASS" ("predict_seconds=" + (($predictSecs | ForEach-Object { [Math]::Round($_, 3) }) -join ","))
  Save-PhaseChecks $phases $runnerChecksPath

  # Phase 9 collect report + optional push
  Write-Timeline "phase9_collect_report start"
  $collectLog = Join-Path $sessionDir "phase9_collect_report.log"
  $collectRun = Run-CommandWithLog "phase9_collect_report" `
    "$PythonExe qa/scripts/quant_ml_collect_report.py --session-dir $sessionDir" `
    { & $PythonExe "qa/scripts/quant_ml_collect_report.py" --session-dir $sessionDir 2>&1 | Tee-Object -FilePath $collectLog | Out-Host } `
    $collectLog `
    -ExecuteInDryRun
  if (-not $collectRun.success) {
    Add-Phase $phases "phase9_collect_report" "FAIL" "collect report failed"
    Save-PhaseChecks $phases $runnerChecksPath
    throw "phase9 report failed"
  }

  if ($EnablePush) {
    $statusLines = @(& git status --short)
    $unexpected = @(
      $statusLines | Where-Object {
        ($_ -notmatch "^\?\? logs/overnight/") -and
        ($_ -notmatch "^\?\? \.logs/") -and
        ($_ -notmatch "^\?\? \.tmp/") -and
        ($_ -notmatch "^\?\? logs/") -and
        ($_ -notmatch "^\?\? OpenBB/") -and
        ($_ -notmatch "^\?\? openbb_platform/core/openbb/\.build\.lock$")
      }
    )
    if ($unexpected.Count -gt 0) {
      Add-Phase $phases "phase9_conditional_push" "FAIL" "unexpected_worktree_changes"
      Save-PhaseChecks $phases $runnerChecksPath
      throw "conditional push blocked: unexpected worktree changes"
    }
    if (-not $DryRun) {
      & git push myrepo develop 2>&1 | Tee-Object -FilePath (Join-Path $sessionDir "phase9_git_push.log") | Out-Host
      if ($LASTEXITCODE -ne 0) {
        Add-Phase $phases "phase9_conditional_push" "FAIL" "git push failed"
        Save-PhaseChecks $phases $runnerChecksPath
        throw "git push failed"
      }
    }
    Add-Phase $phases "phase9_conditional_push" "PASS" "git push myrepo develop"
  } else {
    Add-Phase $phases "phase9_conditional_push" "SKIP" "EnablePush not set"
  }
  Save-PhaseChecks $phases $runnerChecksPath

  Write-Timeline "session_complete PASS"
} catch {
  Write-Timeline ("session_complete FAIL: " + $_.Exception.Message)
  Save-PhaseChecks $phases $runnerChecksPath
  throw
} finally {
  Pop-Location
}
