[CmdletBinding()]
param(
  [ValidateSet("start", "status", "wait", "stop")]
  [string]$Mode = "start",
  [string]$RootPath = ".",
  [string]$RunId = "",
  [string]$OutputBaseDir = "logs/verification",
  [string]$ProviderConfigPath = "qa/config/provider_tiers.yaml",
  [string]$PythonCommand = "python",
  [string]$ApiHost = "127.0.0.1",
  [int]$ApiPort = 8000,
  [int]$ApiHealthTimeoutSeconds = 180,
  [switch]$SkipPythonIntegration,
  [switch]$SkipApiIntegration,
  [switch]$SkipCliIntegration,
  [switch]$DryRun,
  [int]$WaitTimeoutSeconds = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Convert-ToAbsolutePath {
  param([string]$PathValue)
  if ([string]::IsNullOrWhiteSpace($PathValue)) {
    return (Get-Location).Path
  }
  try {
    return (Resolve-Path -LiteralPath $PathValue -ErrorAction Stop).Path
  } catch {
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $PathValue))
  }
}

function Get-RootLabel {
  param([string]$PathValue)
  if ($PathValue -eq "." -or $PathValue -eq ".\") {
    return "tracked_root"
  }
  return ($PathValue -replace "[^A-Za-z0-9._-]", "_")
}

function Ensure-Directory {
  param([string]$PathValue)
  if (-not (Test-Path -LiteralPath $PathValue)) {
    New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
  }
}

function Convert-ToPsSingleQuotedLiteral {
  param([string]$Value)
  if ($null -eq $Value) {
    return "''"
  }
  return "'" + $Value.Replace("'", "''") + "'"
}

function Resolve-RunId {
  param(
    [string]$RequestedRunId,
    [string]$StateDir,
    [string]$ModeName
  )
  if (-not [string]::IsNullOrWhiteSpace($RequestedRunId)) {
    return $RequestedRunId
  }
  if ($ModeName -eq "start") {
    return (Get-Date -Format "yyyyMMdd_HHmmss")
  }
  $latest = Get-ChildItem -Path $StateDir -Filter "*.json" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  if ($null -eq $latest) {
    throw "No background run metadata found in $StateDir. Provide -RunId explicitly."
  }
  return [System.IO.Path]::GetFileNameWithoutExtension($latest.Name)
}

function Get-RunMetadata {
  param(
    [string]$StateDir,
    [string]$ResolvedRunId
  )
  $metaPath = Join-Path $StateDir "$ResolvedRunId.json"
  if (-not (Test-Path -LiteralPath $metaPath)) {
    throw "Run metadata not found: $metaPath"
  }
  $meta = Get-Content -LiteralPath $metaPath -Raw | ConvertFrom-Json
  return [pscustomobject]@{
    path = $metaPath
    data = $meta
  }
}

function Get-RunStatusObject {
  param([pscustomobject]$Meta)

  $processId = [int]$Meta.data.pid
  $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
  $isRunning = $null -ne $process
  $summaryPath = [string]$Meta.data.summary_path
  $summaryExists = Test-Path -LiteralPath $summaryPath
  $overallStatus = ""
  if ($summaryExists) {
    try {
      $summaryJson = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
      $overallStatus = [string]$summaryJson.overall_status
    } catch {
      $overallStatus = "UNKNOWN"
    }
  }

  return [ordered]@{
    run_id = [string]$Meta.data.run_id
    pid = $processId
    running = $isRunning
    summary_path = $summaryPath
    summary_exists = $summaryExists
    overall_status = $overallStatus
    stdout_path = [string]$Meta.data.stdout_path
    stderr_path = [string]$Meta.data.stderr_path
    metadata_path = [string]$Meta.path
    started_at = [string]$Meta.data.started_at
  }
}

$rootAbs = Convert-ToAbsolutePath -PathValue $RootPath
$outputBaseAbs = Convert-ToAbsolutePath -PathValue $OutputBaseDir
$stateDir = Join-Path $outputBaseAbs "_background"
Ensure-Directory -PathValue $stateDir
$resolvedRunId = Resolve-RunId -RequestedRunId $RunId -StateDir $stateDir -ModeName $Mode

if ($Mode -eq "start") {
  $gateScript = Join-Path $rootAbs "qa/scripts/run_integration_gate.ps1"
  if (-not (Test-Path -LiteralPath $gateScript)) {
    throw "Gate script not found: $gateScript"
  }

  $runLogDir = Join-Path $stateDir $resolvedRunId
  Ensure-Directory -PathValue $runLogDir
  $stdoutPath = Join-Path $runLogDir "stdout.log"
  $stderrPath = Join-Path $runLogDir "stderr.log"
  $rootLabel = Get-RootLabel -PathValue $RootPath
  $summaryPath = Join-Path (Join-Path (Join-Path $outputBaseAbs $resolvedRunId) $rootLabel) "integration\integration_gate.json"

  $commandSegments = @(
    "&",
    (Convert-ToPsSingleQuotedLiteral -Value $gateScript),
    "-RootPath",
    (Convert-ToPsSingleQuotedLiteral -Value $RootPath),
    "-RunId",
    (Convert-ToPsSingleQuotedLiteral -Value $resolvedRunId),
    "-OutputBaseDir",
    (Convert-ToPsSingleQuotedLiteral -Value $OutputBaseDir),
    "-ProviderConfigPath",
    (Convert-ToPsSingleQuotedLiteral -Value $ProviderConfigPath),
    "-PythonCommand",
    (Convert-ToPsSingleQuotedLiteral -Value $PythonCommand),
    "-ApiHost",
    (Convert-ToPsSingleQuotedLiteral -Value $ApiHost),
    "-ApiPort",
    "$ApiPort",
    "-ApiHealthTimeoutSeconds",
    "$ApiHealthTimeoutSeconds"
  )
  if ($SkipPythonIntegration) { $commandSegments += "-SkipPythonIntegration" }
  if ($SkipApiIntegration) { $commandSegments += "-SkipApiIntegration" }
  if ($SkipCliIntegration) { $commandSegments += "-SkipCliIntegration" }
  if ($DryRun) { $commandSegments += "-DryRun" }

  $commandText = $commandSegments -join " "
  $encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($commandText))
  $args = @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-EncodedCommand",
    $encodedCommand
  )

  $proc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList $args `
    -WorkingDirectory $rootAbs `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -PassThru

  $metaObj = [ordered]@{
    run_id = $resolvedRunId
    pid = $proc.Id
    root_path = $rootAbs
    output_base_dir = $outputBaseAbs
    summary_path = $summaryPath
    stdout_path = $stdoutPath
    stderr_path = $stderrPath
    started_at = (Get-Date).ToString("o")
    mode = "background"
  }
  $metaPath = Join-Path $stateDir "$resolvedRunId.json"
  $metaObj | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metaPath -Encoding utf8

  Write-Host ("Started integration gate in background. run_id={0} pid={1}" -f $resolvedRunId, $proc.Id)
  Write-Host ("Metadata: {0}" -f $metaPath)
  Write-Host ("Stdout:   {0}" -f $stdoutPath)
  Write-Host ("Stderr:   {0}" -f $stderrPath)
  Write-Host ("Summary:  {0}" -f $summaryPath)
  exit 0
}

$meta = Get-RunMetadata -StateDir $stateDir -ResolvedRunId $resolvedRunId

if ($Mode -eq "stop") {
  $processId = [int]$meta.data.pid
  $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
  if ($null -eq $process) {
    Write-Host ("Run {0} is not running (pid={1})." -f $resolvedRunId, $processId)
    exit 0
  }
  Stop-Process -Id $processId -Force -ErrorAction Stop
  Write-Host ("Stopped run {0} (pid={1})." -f $resolvedRunId, $processId)
  exit 0
}

if ($Mode -eq "wait") {
  $processId = [int]$meta.data.pid
  $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
  if ($null -ne $process) {
    if ($WaitTimeoutSeconds -gt 0) {
      $deadline = (Get-Date).AddSeconds($WaitTimeoutSeconds)
      while ((Get-Date) -lt $deadline) {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($null -eq $process) {
          break
        }
        Start-Sleep -Seconds 2
      }
      $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
      if ($null -ne $process) {
        throw "Timeout waiting for run $resolvedRunId (pid=$processId)."
      }
    } else {
      Wait-Process -Id $processId
    }
  }
}

$status = Get-RunStatusObject -Meta $meta
$statusJson = $status | ConvertTo-Json -Depth 4
Write-Output $statusJson

if ($Mode -eq "wait") {
  if (-not $status.summary_exists) {
    exit 1
  }
  if ($status.overall_status -eq "PASS") {
    exit 0
  }
  exit 1
}

exit 0
