[CmdletBinding()]
param(
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
  [switch]$DryRun
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

function Convert-ToRepoRelativePath {
  param(
    [string]$RootAbsPath,
    [string]$TargetAbsPath
  )
  $rootNorm = ([System.IO.Path]::GetFullPath($RootAbsPath)).TrimEnd("\", "/")
  $targetNorm = [System.IO.Path]::GetFullPath($TargetAbsPath)
  if ($targetNorm.StartsWith($rootNorm, [System.StringComparison]::OrdinalIgnoreCase)) {
    return $targetNorm.Substring($rootNorm.Length).TrimStart("\", "/") -replace "\\", "/"
  }
  return $targetNorm -replace "\\", "/"
}

function Convert-ToBool {
  param([string]$Value)
  return @("true", "1", "yes", "y") -contains $Value.Trim().ToLowerInvariant()
}

function Get-ProviderTiers {
  param([string]$ConfigPath)

  if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "Provider tier config not found: $ConfigPath"
  }

  $core = [System.Collections.Generic.List[string]]::new()
  $extended = [System.Collections.Generic.List[string]]::new()
  $retryMax = 2
  $retryDelay = 10
  $section = ""

  foreach ($line in Get-Content -LiteralPath $ConfigPath) {
    $trim = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trim) -or $trim.StartsWith("#")) {
      continue
    }

    if ($trim -eq "core_blocking:") {
      $section = "core"
      continue
    }
    if ($trim -eq "extended_quarantine:") {
      $section = "extended"
      continue
    }
    if ($trim -eq "retry_policy:") {
      $section = "retry"
      continue
    }

    if ($trim -match "^-\s*(.+)$") {
      $provider = $Matches[1].Trim().Trim("'`"")
      if ($section -eq "core") {
        $core.Add($provider)
      } elseif ($section -eq "extended") {
        $extended.Add($provider)
      }
      continue
    }

    if ($section -eq "retry" -and $trim -match "^max_retries:\s*(\d+)$") {
      $retryMax = [int]$Matches[1]
      continue
    }
    if ($section -eq "retry" -and $trim -match "^retry_delay_seconds:\s*(\d+)$") {
      $retryDelay = [int]$Matches[1]
      continue
    }
  }

  return [pscustomobject]@{
    core_blocking = @($core)
    extended_quarantine = @($extended)
    retry_policy = [pscustomobject]@{
      max_retries = $retryMax
      retry_delay_seconds = $retryDelay
    }
  }
}

function Test-ListeningPort {
  param(
    [string]$HostName,
    [int]$Port
  )
  $client = $null
  try {
    $client = [System.Net.Sockets.TcpClient]::new()
    $async = $client.BeginConnect($HostName, $Port, $null, $null)
    $wait = $async.AsyncWaitHandle.WaitOne(400)
    if (-not $wait) {
      return $false
    }
    $null = $client.EndConnect($async)
    return $client.Connected
  } catch {
    return $false
  } finally {
    if ($null -ne $client) {
      $client.Dispose()
    }
  }
}

function Test-ApiHealth {
  param(
    [string]$HostName,
    [int]$Port
  )
  $uris = @(
    "http://$HostName`:$Port/api/v1/system",
    "http://$HostName`:$Port/openapi.json",
    "http://$HostName`:$Port/docs"
  )
  foreach ($uri in $uris) {
    try {
      $response = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 6
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
        return $true
      }
    } catch {
      continue
    }
  }
  return $false
}

function Wait-ApiHealth {
  param(
    [string]$HostName,
    [int]$Port,
    [int]$TimeoutSeconds
  )
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if (Test-ApiHealth -HostName $HostName -Port $Port) {
      return $true
    }
    Start-Sleep -Milliseconds 700
  }
  return $false
}

function Get-ApiExecutable {
  param([string]$RootAbsPath)
  $candidateWindows = Join-Path $RootAbsPath ".venv\Scripts\openbb-api.exe"
  if (Test-Path -LiteralPath $candidateWindows) {
    return $candidateWindows
  }
  $candidateUnix = Join-Path $RootAbsPath ".venv/bin/openbb-api"
  if (Test-Path -LiteralPath $candidateUnix) {
    return $candidateUnix
  }
  $command = Get-Command openbb-api -ErrorAction SilentlyContinue
  if ($null -ne $command) {
    return $command.Source
  }
  return $null
}

function Get-DetectedProviders {
  param(
    [string[]]$FilesToScan,
    [string[]]$KnownProviders
  )
  $detected = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

  foreach ($file in $FilesToScan) {
    if (-not (Test-Path -LiteralPath $file)) {
      continue
    }
    $content = Get-Content -LiteralPath $file -Raw -ErrorAction SilentlyContinue
    if ([string]::IsNullOrWhiteSpace($content)) {
      continue
    }
    foreach ($provider in $KnownProviders) {
      $pattern = "(?i)(^|[^a-z0-9_])" + [Regex]::Escape($provider) + "([^a-z0-9_]|$)"
      if ([Regex]::IsMatch($content, $pattern)) {
        $null = $detected.Add($provider)
      }
    }
  }

  return @($detected | Sort-Object)
}

function Invoke-PytestWithRetries {
  param(
    [string]$SuiteName,
    [string]$WorkingDirectory,
    [string[]]$PytestArguments,
    [int]$MaxRetries,
    [int]$RetryDelaySeconds,
    [string]$SuiteOutputDirectory,
    [string]$PythonExe,
    [switch]$DryRunMode
  )

  Ensure-Directory -PathValue $SuiteOutputDirectory
  $attemptLogs = [System.Collections.Generic.List[string]]::new()
  $junitPath = Join-Path $SuiteOutputDirectory "$SuiteName.junit.xml"

  for ($attempt = 0; $attempt -le $MaxRetries; $attempt++) {
    $attemptLog = Join-Path $SuiteOutputDirectory ("$SuiteName.attempt_{0}.log" -f $attempt)
    $attemptLogs.Add($attemptLog)

    if ($DryRunMode) {
      Set-Content -LiteralPath $attemptLog -Value "DRY RUN: $PythonExe -m pytest $($PytestArguments -join ' ')"
      return [pscustomobject]@{
        suite = $SuiteName
        status = "PASS"
        attempts = ($attempt + 1)
        exit_code = 0
        junit_xml = $junitPath
        logs = @($attemptLogs)
      }
    }

    Push-Location $WorkingDirectory
    try {
      $prevEap = $ErrorActionPreference
      try {
        $ErrorActionPreference = "Continue"
        $global:LASTEXITCODE = 0
        & $PythonExe -m pytest @PytestArguments 2>&1 | Tee-Object -FilePath $attemptLog | Out-Host
        $exitCode = [int]$LASTEXITCODE
      } finally {
        $ErrorActionPreference = $prevEap
      }
    } finally {
      Pop-Location
    }

    if ($exitCode -eq 0) {
      return [pscustomobject]@{
        suite = $SuiteName
        status = "PASS"
        attempts = ($attempt + 1)
        exit_code = 0
        junit_xml = $junitPath
        logs = @($attemptLogs)
      }
    }

    if ($attempt -lt $MaxRetries) {
      Start-Sleep -Seconds $RetryDelaySeconds
    }
  }

  return [pscustomobject]@{
    suite = $SuiteName
    status = "FAIL"
    attempts = ($MaxRetries + 1)
    exit_code = 1
    junit_xml = $junitPath
    logs = @($attemptLogs)
  }
}

if ([string]::IsNullOrWhiteSpace($RunId)) {
  $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
}

$rootAbs = Convert-ToAbsolutePath -PathValue $RootPath
$providerConfigAbs = Convert-ToAbsolutePath -PathValue $ProviderConfigPath
$outputBaseAbs = Convert-ToAbsolutePath -PathValue $OutputBaseDir
$rootLabel = Get-RootLabel -PathValue $RootPath
$runRootDir = Join-Path (Join-Path $outputBaseAbs $RunId) $rootLabel
$integrationDir = Join-Path $runRootDir "integration"

Ensure-Directory -PathValue $integrationDir

if (-not (Test-Path -LiteralPath $rootAbs)) {
  throw "Root path does not exist: $rootAbs"
}

$tiers = Get-ProviderTiers -ConfigPath $providerConfigAbs
$knownProviders = @($tiers.core_blocking + $tiers.extended_quarantine | Sort-Object -Unique)
$retryMax = [int]$tiers.retry_policy.max_retries
$retryDelaySeconds = [int]$tiers.retry_policy.retry_delay_seconds

$suiteResults = [System.Collections.Generic.List[object]]::new()
$apiProcess = $null
$apiStartedByScript = $false

try {
  if (-not $SkipApiIntegration -and -not $DryRun) {
    if (-not (Test-ListeningPort -HostName $ApiHost -Port $ApiPort)) {
      $apiExe = Get-ApiExecutable -RootAbsPath $rootAbs
      if ([string]::IsNullOrWhiteSpace($apiExe)) {
        throw "Cannot run API integration tests: openbb-api executable not found."
      }

      $apiStdOut = Join-Path $integrationDir "api.stdout.log"
      $apiStdErr = Join-Path $integrationDir "api.stderr.log"
      $apiProcess = Start-Process `
        -FilePath $apiExe `
        -ArgumentList @("--host", $ApiHost, "--port", "$ApiPort") `
        -WorkingDirectory $rootAbs `
        -RedirectStandardOutput $apiStdOut `
        -RedirectStandardError $apiStdErr `
        -PassThru
      $apiStartedByScript = $true

      if (-not (Wait-ApiHealth -HostName $ApiHost -Port $ApiPort -TimeoutSeconds $ApiHealthTimeoutSeconds)) {
        throw "API server did not become healthy within $ApiHealthTimeoutSeconds seconds."
      }
    }
  }

  if (-not $SkipPythonIntegration) {
    $pythonTargets = @(
      (Join-Path $rootAbs "openbb_platform/core/integration"),
      (Join-Path $rootAbs "openbb_platform/extensions"),
      (Join-Path $rootAbs "openbb_platform/obbject_extensions/charting/integration")
    ) | Where-Object { Test-Path -LiteralPath $_ } | ForEach-Object {
      Convert-ToRepoRelativePath -RootAbsPath $rootAbs -TargetAbsPath $_
    }

    if ($pythonTargets.Count -gt 0) {
      $junitPath = Join-Path $integrationDir "python_integration.junit.xml"
      $args = @("-m", "integration", "--maxfail=0", "--durations=20", "--junitxml", $junitPath) + $pythonTargets
      $result = Invoke-PytestWithRetries `
        -SuiteName "python_integration" `
        -WorkingDirectory $rootAbs `
        -PytestArguments $args `
        -MaxRetries $retryMax `
        -RetryDelaySeconds $retryDelaySeconds `
        -SuiteOutputDirectory $integrationDir `
        -PythonExe $PythonCommand `
        -DryRunMode:$DryRun
      $suiteResults.Add($result)
    } else {
      $suiteResults.Add([pscustomobject]@{
        suite = "python_integration"
        status = "SKIP"
        attempts = 0
        exit_code = 0
        junit_xml = ""
        logs = @()
      })
    }
  }

  if (-not $SkipApiIntegration) {
    $apiFiles = [System.Collections.Generic.List[string]]::new()
    $apiRoot = Join-Path $rootAbs "openbb_platform/extensions"
    if (Test-Path -LiteralPath $apiRoot) {
      Get-ChildItem -Path $apiRoot -Recurse -Filter "test_*_api.py" -File | ForEach-Object {
        $apiFiles.Add((Convert-ToRepoRelativePath -RootAbsPath $rootAbs -TargetAbsPath $_.FullName))
      }
    }
    $chartingApiFile = Join-Path $rootAbs "openbb_platform/obbject_extensions/charting/integration/test_charting_api.py"
    if (Test-Path -LiteralPath $chartingApiFile) {
      $apiFiles.Add((Convert-ToRepoRelativePath -RootAbsPath $rootAbs -TargetAbsPath $chartingApiFile))
    }

    if ($apiFiles.Count -gt 0) {
      $junitPath = Join-Path $integrationDir "api_integration.junit.xml"
      $args = @("-m", "integration", "--maxfail=0", "--durations=20", "--junitxml", $junitPath) + @($apiFiles | Sort-Object -Unique)
      $result = Invoke-PytestWithRetries `
        -SuiteName "api_integration" `
        -WorkingDirectory $rootAbs `
        -PytestArguments $args `
        -MaxRetries $retryMax `
        -RetryDelaySeconds $retryDelaySeconds `
        -SuiteOutputDirectory $integrationDir `
        -PythonExe $PythonCommand `
        -DryRunMode:$DryRun
      $suiteResults.Add($result)
    } else {
      $suiteResults.Add([pscustomobject]@{
        suite = "api_integration"
        status = "SKIP"
        attempts = 0
        exit_code = 0
        junit_xml = ""
        logs = @()
      })
    }
  }

  if (-not $SkipCliIntegration) {
    $cliIntegrationPath = Join-Path $rootAbs "cli/integration"
    if (Test-Path -LiteralPath $cliIntegrationPath) {
      $junitPath = Join-Path $integrationDir "cli_integration.junit.xml"
      $target = Convert-ToRepoRelativePath -RootAbsPath $rootAbs -TargetAbsPath $cliIntegrationPath
      $args = @("-m", "integration", "--maxfail=0", "--durations=20", "--junitxml", $junitPath, $target)
      $result = Invoke-PytestWithRetries `
        -SuiteName "cli_integration" `
        -WorkingDirectory $rootAbs `
        -PytestArguments $args `
        -MaxRetries $retryMax `
        -RetryDelaySeconds $retryDelaySeconds `
        -SuiteOutputDirectory $integrationDir `
        -PythonExe $PythonCommand `
        -DryRunMode:$DryRun
      $suiteResults.Add($result)
    } else {
      $suiteResults.Add([pscustomobject]@{
        suite = "cli_integration"
        status = "SKIP"
        attempts = 0
        exit_code = 0
        junit_xml = ""
        logs = @()
      })
    }
  }
} finally {
  if ($apiStartedByScript -and $null -ne $apiProcess) {
    try {
      Stop-Process -Id $apiProcess.Id -Force -ErrorAction Stop
    } catch {
      Write-Warning ("Failed to stop API process PID {0}: {1}" -f $apiProcess.Id, $_.Exception.Message)
    }
  }
}

$coreFailures = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$extendedFailures = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$unknownProviderFailures = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$unknownSuiteFailures = [System.Collections.Generic.List[string]]::new()

foreach ($suite in $suiteResults) {
  if ($suite.status -ne "FAIL") {
    continue
  }

  $scanFiles = [System.Collections.Generic.List[string]]::new()
  foreach ($logPath in $suite.logs) {
    $scanFiles.Add($logPath)
  }
  if (-not [string]::IsNullOrWhiteSpace($suite.junit_xml)) {
    $scanFiles.Add($suite.junit_xml)
  }
  $detectedProviders = Get-DetectedProviders -FilesToScan @($scanFiles) -KnownProviders $knownProviders
  if ($detectedProviders.Count -eq 0) {
    $unknownSuiteFailures.Add($suite.suite)
    continue
  }

  foreach ($provider in $detectedProviders) {
    if ($tiers.core_blocking -contains $provider) {
      $null = $coreFailures.Add($provider)
    } elseif ($tiers.extended_quarantine -contains $provider) {
      $null = $extendedFailures.Add($provider)
    } else {
      $null = $unknownProviderFailures.Add($provider)
    }
  }
}

$blockingFailures = (
  $coreFailures.Count -gt 0 -or
  $unknownProviderFailures.Count -gt 0 -or
  $unknownSuiteFailures.Count -gt 0
)

$quarantineReport = [ordered]@{
  run_id = $RunId
  root_path = $rootAbs
  root_label = $rootLabel
  core_provider_failures = @($coreFailures | Sort-Object)
  extended_provider_failures = @($extendedFailures | Sort-Object)
  unknown_provider_failures = @($unknownProviderFailures | Sort-Object)
  unknown_suite_failures = @($unknownSuiteFailures)
  retry_policy = [ordered]@{
    max_retries = $retryMax
    retry_delay_seconds = $retryDelaySeconds
  }
  suites = @($suiteResults)
}

$gateSummary = [ordered]@{
  run_id = $RunId
  root_path = $rootAbs
  root_label = $rootLabel
  output_directory = $integrationDir
  dry_run = [bool]$DryRun
  overall_status = if ($blockingFailures) { "FAIL" } else { "PASS" }
  policy = [ordered]@{
    core_blocking = @($tiers.core_blocking)
    extended_quarantine = @($tiers.extended_quarantine)
    retry_policy = [ordered]@{
      max_retries = $retryMax
      retry_delay_seconds = $retryDelaySeconds
    }
  }
  quarantine = $quarantineReport
}

$quarantinePath = Join-Path $integrationDir "quarantine_report.json"
$summaryPath = Join-Path $integrationDir "integration_gate.json"
$quarantineReport | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $quarantinePath -Encoding utf8
$gateSummary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summaryPath -Encoding utf8

if ($blockingFailures) {
  Write-Host "Integration gate failed. See $summaryPath"
  exit 1
}

Write-Host "Integration gate passed. See $summaryPath"
exit 0
