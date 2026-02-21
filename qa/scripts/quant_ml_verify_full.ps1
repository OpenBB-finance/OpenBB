[CmdletBinding()]
param(
  [string]$SessionId = "",
  [string]$OutputDir = "",
  [string]$RepoRoot = ".",
  [string]$PythonExe = ".\\.venv\\Scripts\\python.exe",
  [string]$ApiBaseUrl = "http://127.0.0.1:6900",
  [switch]$SkipApiSmoke,
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

function Add-Check(
  [System.Collections.Generic.List[object]]$Checks,
  [string]$Name,
  [string]$Status,
  [string]$Command,
  [string]$LogPath,
  [double]$DurationSec,
  [string]$Detail
) {
  $Checks.Add([pscustomobject]@{
      timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
      name = $Name
      status = $Status
      command = $Command
      log = $LogPath
      duration_seconds = [Math]::Round($DurationSec, 3)
      detail = $Detail
    })
}

function Run-LoggedCommand(
  [string]$Name,
  [string]$Command,
  [scriptblock]$Action,
  [string]$LogPath,
  [System.Collections.Generic.List[object]]$Checks
) {
  Ensure-Directory (Split-Path -Parent $LogPath)
  if ($DryRun) {
    Set-Content -LiteralPath $LogPath -Value "DRY RUN: $Command"
    Add-Check $Checks $Name "PASS" $Command $LogPath 0 "dry_run"
    return $true
  }

  $start = Get-Date
  $exitCode = 0
  $oldErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    & $Action
    $exitCode = [int]$LASTEXITCODE
  } catch {
    $_ | Out-String | Tee-Object -FilePath $LogPath -Append | Out-Null
    $exitCode = 1
  } finally {
    $ErrorActionPreference = $oldErrorActionPreference
  }
  $secs = ((Get-Date) - $start).TotalSeconds
  if ($exitCode -eq 0) {
    Add-Check $Checks $Name "PASS" $Command $LogPath $secs ""
    return $true
  }
  Add-Check $Checks $Name "FAIL" $Command $LogPath $secs "exit_code=$exitCode"
  return $false
}

function Invoke-PythonJson([string]$PyCode) {
  $oldErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    $lines = $PyCode | & $PythonExe -
  } finally {
    $ErrorActionPreference = $oldErrorActionPreference
  }
  if ($LASTEXITCODE -ne 0) {
    throw "python helper failed with exit code $LASTEXITCODE"
  }
  $jsonText = ($lines | Select-Object -Last 1)
  if ([string]::IsNullOrWhiteSpace($jsonText)) {
    throw "python helper returned empty output"
  }
  return ($jsonText | ConvertFrom-Json)
}

function Get-VerificationTelemetry() {
  $pyCode = @'
import json
from datetime import datetime, timezone
from pathlib import Path

heartbeat_gap_sec_max = 0.0
root = Path.home() / ".openbb_platform" / "quant_ml" / "runs"
if root.exists():
    for log_path in root.glob("*/logs.jsonl"):
        last_ts = None
        try:
            lines = log_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for line in lines:
            try:
                row = json.loads(line)
            except Exception:
                continue
            if str(row.get("level", "")).lower() != "heartbeat":
                continue
            ts = str(row.get("timestamp", ""))
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            if last_ts is not None:
                gap = (dt - last_ts).total_seconds()
                if gap > heartbeat_gap_sec_max:
                    heartbeat_gap_sec_max = float(gap)
            last_ts = dt

registry_conflict_retries = 0
try:
    from openbb_quant_ml.service.storage import get_registry_write_stats
    stats = get_registry_write_stats()
    registry_conflict_retries = int(stats.get("atomic_replace_retries", 0))
except Exception:
    registry_conflict_retries = 0

print(json.dumps({
    "heartbeat_gap_sec_max": round(float(heartbeat_gap_sec_max), 3),
    "registry_conflict_retries": int(registry_conflict_retries),
}))
'@
  return Invoke-PythonJson $pyCode
}

if ([string]::IsNullOrWhiteSpace($SessionId)) {
  $SessionId = Get-Date -Format "overnight-yyyyMMdd-HHmm"
}

$repoAbs = Resolve-Abs $RepoRoot
$resolvedOutput = if ([string]::IsNullOrWhiteSpace($OutputDir)) {
  Resolve-Abs (Join-Path "logs/overnight" $SessionId)
} else {
  Resolve-Abs $OutputDir
}
Ensure-Directory $resolvedOutput
$verifyDir = Join-Path $resolvedOutput "verification"
Ensure-Directory $verifyDir

$checks = [System.Collections.Generic.List[object]]::new()
$allPass = $true

if ($null -eq (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
  throw "Python executable not found: $PythonExe"
}

Push-Location $repoAbs
try {
  $allPass = (Run-LoggedCommand `
      "pytest_refresh_universes" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_refresh_universes.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_refresh_universes.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_refresh_universes.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_refresh_universes.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "pytest_run_id_policy" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_run_id_policy.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_run_id_policy.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_run_id_policy.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_run_id_policy.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "pytest_stale_policy" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_stale_policy.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_stale_policy.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_stale_policy.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_stale_policy.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "pytest_run_registry_merge_write" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_run_registry_merge_write.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_run_registry_merge_write.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_run_registry_merge_write.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_run_registry_merge_write.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "pytest_data_loader_resilience" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_data_loader_resilience.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_data_loader_resilience.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_data_loader_resilience.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_data_loader_resilience.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "pytest_ranker_ic_constant_groups" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_ranker_ic_constant_groups.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_ranker_ic_constant_groups.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_ranker_ic_constant_groups.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_ranker_ic_constant_groups.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "pytest_universe_csv_min_counts" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_universe_csv_min_counts.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_universe_csv_min_counts.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_universe_csv_min_counts.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_universe_csv_min_counts.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "pytest_jobs_lock" `
      "$PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_jobs_lock.py -q" `
      { & $PythonExe -m pytest openbb_platform/extensions/quant_ml/tests/test_jobs_lock.py -q 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "pytest_jobs_lock.log") | Out-Host } `
      (Join-Path $verifyDir "pytest_jobs_lock.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "frontend_tsc" `
      "npx tsc --noEmit (desktop)" `
      { Push-Location "desktop"; try { & npx tsc --noEmit 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "frontend_tsc.log") | Out-Host } finally { Pop-Location } } `
      (Join-Path $verifyDir "frontend_tsc.log") `
      $checks) -and $allPass

  $allPass = (Run-LoggedCommand `
      "frontend_quant_route_test" `
      "npm --prefix desktop run test -- src/tests/routes/quant.test.tsx" `
      { & npm --prefix desktop run test -- src/tests/routes/quant.test.tsx 2>&1 | Tee-Object -FilePath (Join-Path $verifyDir "frontend_quant_route_test.log") | Out-Host } `
      (Join-Path $verifyDir "frontend_quant_route_test.log") `
      $checks) -and $allPass

  if (-not $SkipApiSmoke) {
    $apiChecks = @(
      @{ name = "api_ops_status"; path = "/api/v1/quant_ml/ops/status" },
      @{ name = "api_model_promoted"; path = "/api/v1/quant_ml/model/promoted" },
      @{ name = "api_portfolio_current"; path = "/api/v1/quant_ml/portfolio/current" },
      @{ name = "api_risk_limits"; path = "/api/v1/quant_ml/risk/limits" }
    )
    foreach ($api in $apiChecks) {
      $name = [string]$api.name
      $path = [string]$api.path
      $log = Join-Path $verifyDir "$name.log"
      $url = "$ApiBaseUrl$path"
      if ($DryRun) {
        Set-Content -LiteralPath $log -Value "DRY RUN: GET $url"
        Add-Check $checks $name "PASS" "GET $url" $log 0 "dry_run"
        continue
      }
      $start = Get-Date
      try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20
        $code = [int]$resp.StatusCode
        $resp.Content | Set-Content -LiteralPath $log -Encoding UTF8
        $secs = ((Get-Date) - $start).TotalSeconds
        if ($code -ge 200 -and $code -lt 300) {
          Add-Check $checks $name "PASS" "GET $url" $log $secs "status_code=$code"
        } else {
          Add-Check $checks $name "FAIL" "GET $url" $log $secs "status_code=$code"
          $allPass = $false
        }
      } catch {
        $_ | Out-String | Set-Content -LiteralPath $log -Encoding UTF8
        $secs = ((Get-Date) - $start).TotalSeconds
        Add-Check $checks $name "FAIL" "GET $url" $log $secs "request_failed"
        $allPass = $false
      }
    }
  }
} finally {
  Pop-Location
}

$overallStatus = if ($allPass) { "PASS" } else { "FAIL" }
$failureCategory = $null
if (-not $allPass) {
  $failureCategory = ($checks | Where-Object { $_.status -eq "FAIL" } | Select-Object -First 1).name
}

$summary = [pscustomobject]@{
  session_id = $SessionId
  generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  overall_status = $overallStatus
  failure_category = $failureCategory
  heartbeat_gap_sec_max = 0.0
  registry_conflict_retries = 0
  checks = @($checks.ToArray())
}

try {
  $telemetry = Get-VerificationTelemetry
  $summary.heartbeat_gap_sec_max = [double]$telemetry.heartbeat_gap_sec_max
  $summary.registry_conflict_retries = [int]$telemetry.registry_conflict_retries
} catch {
  $summary.heartbeat_gap_sec_max = 0.0
  $summary.registry_conflict_retries = 0
}

$checksPath = Join-Path $resolvedOutput "checks.json"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $checksPath -Encoding UTF8
Write-Host "Verification checks written: $checksPath"
if (-not $allPass) {
  throw "quant_ml_verify_full failed; see $checksPath"
}
