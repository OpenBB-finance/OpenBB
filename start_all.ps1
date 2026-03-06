param(
  [int]$ApiPort = 6900,
  [int]$FrontendPort = 1470,
  [bool]$ApiNoBuild = $true,
  [ValidateSet("dev", "prod")]
  [string]$ApiDocsMode = "dev"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Test-ListeningPort {
  param([int]$Port)
  $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  return $null -ne $conn
}

function Wait-ListeningPort {
  param(
    [int]$Port,
    [int]$TimeoutSeconds = 30
  )
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if (Test-ListeningPort -Port $Port) {
      return $true
    }
    Start-Sleep -Milliseconds 500
  }
  return $false
}

function Test-ApiHealth {
  param(
    [int]$Port,
    [string]$DocsMode = "dev"
  )
  $uris = if ($DocsMode -eq "prod") {
    @(
      ("http://127.0.0.1:{0}/api/v1/coverage/providers" -f $Port),
      ("http://127.0.0.1:{0}/docs" -f $Port),
      ("http://127.0.0.1:{0}/api/v1/system" -f $Port),
      ("http://127.0.0.1:{0}/openapi.json" -f $Port)
    )
  }
  else {
    @(
      ("http://127.0.0.1:{0}/api/v1/coverage/providers" -f $Port),
      ("http://127.0.0.1:{0}/api/v1/system" -f $Port)
    )
  }
  foreach ($uri in $uris) {
    try {
      $response = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 4
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
        return $true
      }
    }
    catch {
      # Try next endpoint.
    }
  }
  return $false
}

function Wait-ApiHealth {
  param(
    [int]$Port,
    [int]$TimeoutSeconds = 180,
    [string]$DocsMode = "dev"
  )
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if (Test-ApiHealth -Port $Port -DocsMode $DocsMode) {
      return $true
    }
    Start-Sleep -Milliseconds 700
  }
  return $false
}

function Start-ShellProcess {
  param(
    [string]$FilePath,
    [string[]]$ArgumentList,
    [string]$WorkingDirectory,
    [string]$StdOutLog,
    [string]$StdErrLog
  )
  return Start-Process `
    -FilePath $FilePath `
    -WorkingDirectory $WorkingDirectory `
    -ArgumentList $ArgumentList `
    -RedirectStandardOutput $StdOutLog `
    -RedirectStandardError $StdErrLog `
    -PassThru
}

function Stop-LegacyStartAllShells {
  param([string]$ProjectRoot)
  $legacy = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object {
    $_.CommandLine -and
    $_.CommandLine -match "-NoExit" -and
    $_.CommandLine -match "startup_(api|frontend)" -and
    $_.CommandLine -match [Regex]::Escape($ProjectRoot)
  }
  foreach ($proc in $legacy) {
    try {
      Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
    }
    catch {
      Write-Warning ("Failed to stop legacy startup shell PID {0}: {1}" -f $proc.ProcessId, $_.Exception.Message)
    }
  }
  return @($legacy).Count
}

function Get-ShortPath {
  param([string]$Path)
  if ([string]::IsNullOrWhiteSpace($Path)) {
    return $Path
  }
  try {
    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
    return $resolved.Path
  }
  catch {
    return $Path
  }
}

function Get-LogTail {
  param([string]$Path)
  if (!(Test-Path $Path)) {
    return $null
  }
  try {
    $lines = Get-Content -Path $Path -Tail 20 -ErrorAction Stop
    if ($null -eq $lines) {
      return $null
    }
    return ($lines -join [Environment]::NewLine)
  }
  catch {
    return $null
  }
}

function Build-LogPair {
  param(
    [string]$LogDirectory,
    [string]$Prefix,
    [string]$Stamp
  )
  return @{
    Out = Join-Path $LogDirectory ("{0}_{1}.out.log" -f $Prefix, $Stamp)
    Err = Join-Path $LogDirectory ("{0}_{1}.err.log" -f $Prefix, $Stamp)
  }
}

$projectRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$desktopRoot = Join-Path $projectRoot "desktop"
$venvScripts = Join-Path $projectRoot ".venv\Scripts"
$apiExe = Join-Path $venvScripts "openbb-api.exe"
$npmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source

$activateScript = Join-Path $venvScripts "Activate.ps1"
$apiLogDir = Join-Path $projectRoot "logs"
$runStamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$apiLogs = Build-LogPair -LogDirectory $apiLogDir -Prefix "startup_api" -Stamp $runStamp
$frontendLogs = Build-LogPair -LogDirectory $apiLogDir -Prefix "startup_frontend" -Stamp $runStamp

if (!(Test-Path $activateScript)) {
  throw "Virtual environment was not found. Expected: $activateScript"
}
if (!(Test-Path $apiExe)) {
  throw "API executable was not found. Expected: $apiExe"
}
if (!(Test-Path (Join-Path $desktopRoot "package.json"))) {
  throw "Desktop package.json was not found. Expected desktop folder at: $desktopRoot"
}
if ([string]::IsNullOrWhiteSpace($npmCmd)) {
  throw "npm.cmd was not found in PATH. Install Node.js and reopen PowerShell."
}

New-Item -ItemType Directory -Path $apiLogDir -Force | Out-Null

# Auto-cleanup: remove log files older than 7 days and empty log files
$logCleanupThreshold = (Get-Date).AddDays(-7)
$cleanedCount = 0
Get-ChildItem -Path $apiLogDir -File -Recurse -ErrorAction SilentlyContinue | Where-Object {
  $_.LastWriteTime -lt $logCleanupThreshold -or $_.Length -eq 0
} | ForEach-Object {
  try { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction Stop; $cleanedCount++ } catch {}
}
if ($cleanedCount -gt 0) {
  Write-Host "Cleaned up $cleanedCount old/empty log file(s)."
}

$stoppedLegacyCount = Stop-LegacyStartAllShells -ProjectRoot $projectRoot
if ($stoppedLegacyCount -gt 0) {
  Write-Host "Stopped $stoppedLegacyCount legacy startup shell process(es)."
}

if (Test-ListeningPort -Port $ApiPort) {
  Write-Host "API port $ApiPort already in use. Skipping API launch."
}
else {
  $apiArgs = @("--host", "127.0.0.1", "--port", "$ApiPort", "--workers", "4")
  if ($ApiNoBuild) {
    $apiArgs += "--no-build"
  }
  $apiDocsEnvMode = if ($ApiDocsMode -eq "prod") { "full" } else { "disabled" }
  $previousApiDocsEnvMode = $env:OPENBB_API_DOCS_MODE
  $env:OPENBB_API_DOCS_MODE = $apiDocsEnvMode
  $apiProcess = Start-ShellProcess `
    -FilePath $apiExe `
    -ArgumentList $apiArgs `
    -WorkingDirectory $projectRoot `
    -StdOutLog $apiLogs.Out `
    -StdErrLog $apiLogs.Err
  if ($null -eq $previousApiDocsEnvMode) {
    Remove-Item Env:OPENBB_API_DOCS_MODE -ErrorAction SilentlyContinue
  }
  else {
    $env:OPENBB_API_DOCS_MODE = $previousApiDocsEnvMode
  }
  Write-Host ("Started API launcher process PID {0}" -f $apiProcess.Id)
  Write-Host ("OPENBB_API_DOCS_MODE={0}" -f $apiDocsEnvMode)
}

if (Test-ListeningPort -Port $FrontendPort) {
  Write-Host "Frontend port $FrontendPort already in use. Skipping frontend launch."
}
else {
  $frontendProcess = Start-ShellProcess `
    -FilePath $npmCmd `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory $desktopRoot `
    -StdOutLog $frontendLogs.Out `
    -StdErrLog $frontendLogs.Err
  Write-Host ("Started frontend launcher process PID {0}" -f $frontendProcess.Id)
}

$apiReady = Wait-ApiHealth -Port $ApiPort -TimeoutSeconds 180 -DocsMode $ApiDocsMode
$frontendReady = Wait-ListeningPort -Port $FrontendPort -TimeoutSeconds 45

if ($apiReady -and $frontendReady) {
  if ($ApiDocsMode -eq "prod") {
    try {
      Invoke-WebRequest -Uri ("http://127.0.0.1:{0}/openapi.json" -f $ApiPort) -UseBasicParsing -TimeoutSec 8 | Out-Null
      Write-Host "OpenAPI schema prewarmed (prod mode)."
    }
    catch {
      Write-Warning "OpenAPI schema prewarm failed."
    }
  }
  Write-Host "Started OpenBB API and Desktop dev server."
  Write-Host ("API docs mode: {0}" -f $ApiDocsMode)
  Write-Host "Open: http://localhost:$FrontendPort/quant"
  Write-Host ("API logs: {0} / {1}" -f (Get-ShortPath $apiLogs.Out), (Get-ShortPath $apiLogs.Err))
  Write-Host ("Frontend logs: {0} / {1}" -f (Get-ShortPath $frontendLogs.Out), (Get-ShortPath $frontendLogs.Err))
  exit 0
}

if (-not $apiReady) {
  Write-Warning ("API did not open port {0}. Check logs: {1} / {2}" -f $ApiPort, (Get-ShortPath $apiLogs.Out), (Get-ShortPath $apiLogs.Err))
  $apiErrTail = Get-LogTail -Path $apiLogs.Err
  if ($apiErrTail) {
    Write-Warning ("API stderr tail:`n{0}" -f $apiErrTail)
  }
}
if (-not $frontendReady) {
  Write-Warning ("Frontend did not open port {0}. Check logs: {1} / {2}" -f $FrontendPort, (Get-ShortPath $frontendLogs.Out), (Get-ShortPath $frontendLogs.Err))
  $frontendErrTail = Get-LogTail -Path $frontendLogs.Err
  if ($frontendErrTail) {
    Write-Warning ("Frontend stderr tail:`n{0}" -f $frontendErrTail)
  }
}

throw "One or more services failed to start. See logs in: $apiLogDir"
