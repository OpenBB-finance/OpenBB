[CmdletBinding()]
param(
  [string]$RunId = "",
  [string]$TargetsConfigPath = "qa/config/verification_targets.yaml",
  [string]$ProviderConfigPath = "qa/config/provider_tiers.yaml",
  [string]$OutputBaseDir = "logs/verification",
  [string[]]$PythonVersions = @("3.10", "3.11", "3.12", "3.13"),
  [int]$DesktopPort = 1470,
  [switch]$CiMode,
  [switch]$SkipPlatform,
  [switch]$SkipCli,
  [switch]$SkipDesktop,
  [switch]$SkipFrontendComponents,
  [switch]$SkipStaticQuality,
  [switch]$SkipUnitTests,
  [switch]$SkipIntegration,
  [switch]$SkipSmoke,
  [switch]$SkipPythonVersionGate,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function AbsPath([string]$PathValue) {
  if ([string]::IsNullOrWhiteSpace($PathValue)) {
    return (Get-Location).Path
  }
  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return [System.IO.Path]::GetFullPath($PathValue)
  }
  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $PathValue))
}

function EnsureDir([string]$PathValue) {
  if (-not (Test-Path -LiteralPath $PathValue)) {
    New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
  }
}

function ToBool([string]$Value) {
  return @("true", "1", "yes", "y") -contains $Value.Trim().ToLowerInvariant()
}

function RootLabel([string]$PathValue) {
  if ($PathValue -eq "." -or $PathValue -eq ".\") {
    return "tracked_root"
  }
  return ($PathValue -replace "[^A-Za-z0-9._-]", "_")
}

function ParseTargets([string]$ConfigPath) {
  if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "Missing config: $ConfigPath"
  }
  $targets = [System.Collections.Generic.List[object]]::new()
  $item = $null
  foreach ($line in Get-Content -LiteralPath $ConfigPath) {
    $trim = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trim) -or $trim.StartsWith("#") -or $trim -eq "roots:") {
      continue
    }
    if ($trim -match "^-\s*path:\s*(.+)$") {
      if ($null -ne $item) {
        $targets.Add([pscustomobject]$item)
      }
      $item = @{
        path = $Matches[1].Trim().Trim("'`"")
        ci_required = $false
        run_desktop = $false
        run_frontend_components = $false
        run_cli = $false
        run_platform = $false
      }
      continue
    }
    if ($null -eq $item) {
      continue
    }
    if ($trim -match "^(ci_required|run_desktop|run_frontend_components|run_cli|run_platform):\s*(.+)$") {
      $item[$Matches[1]] = ToBool($Matches[2].Trim().Trim("'`""))
    }
  }
  if ($null -ne $item) {
    $targets.Add([pscustomobject]$item)
  }
  return @($targets.ToArray())
}

function NewGate(
  [string]$Gate,
  [string]$Status,
  [string]$Root,
  [string]$Command,
  [string]$Log,
  [double]$Seconds,
  [string]$Notes
) {
  return [pscustomobject]@{
    timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
    gate = $Gate
    status = $Status
    root_label = $Root
    command = $Command
    log = $Log
    duration_seconds = [Math]::Round($Seconds, 3)
    notes = $Notes
  }
}

function RunCommand([string]$FilePath, [string[]]$CmdArgs, [string]$Cwd, [string]$LogFile, [switch]$DryMode) {
  EnsureDir (Split-Path -Parent $LogFile)
  $cmd = "$FilePath $($CmdArgs -join ' ')".Trim()
  if ($DryMode) {
    Set-Content -LiteralPath $LogFile -Value "DRY RUN: $cmd"
    return [pscustomobject]@{ exit_code = 0; cmd = $cmd; secs = 0.0; log = $LogFile }
  }
  $start = Get-Date
  $exit = 0
  Push-Location $Cwd
  try {
    $prevEap = $ErrorActionPreference
    try {
      $ErrorActionPreference = "Continue"
      $global:LASTEXITCODE = 0
      & $FilePath @CmdArgs 2>&1 | Tee-Object -FilePath $LogFile | Out-Host
      $exit = [int]$LASTEXITCODE
    } finally {
      $ErrorActionPreference = $prevEap
    }
  } catch {
    $_ | Out-String | Tee-Object -FilePath $LogFile -Append | Out-Null
    $exit = 1
  } finally {
    Pop-Location
  }
  $secs = ((Get-Date) - $start).TotalSeconds
  return [pscustomobject]@{ exit_code = $exit; cmd = $cmd; secs = $secs; log = $LogFile }
}

function RunGate(
  [System.Collections.Generic.List[object]]$List,
  [string]$Root,
  [string]$Gate,
  [string]$Cwd,
  [string]$LogFile,
  [string]$FilePath,
  [string[]]$CmdArgs,
  [switch]$WarnOnly
) {
  $run = RunCommand -FilePath $FilePath -CmdArgs $CmdArgs -Cwd $Cwd -LogFile $LogFile -DryMode:$DryRun
  $status = "PASS"
  if ($run.exit_code -ne 0) {
    $status = if ($WarnOnly) { "WARN" } else { "FAIL" }
  }
  $List.Add((NewGate $Gate $status $Root $run.cmd $run.log $run.secs ""))
  return $status
}

function PortOpen([string]$HostName, [int]$Port) {
  $client = $null
  try {
    $client = [System.Net.Sockets.TcpClient]::new()
    $async = $client.BeginConnect($HostName, $Port, $null, $null)
    if (-not $async.AsyncWaitHandle.WaitOne(400)) {
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

function WaitApi([int]$Port, [int]$Timeout = 120) {
  $deadline = (Get-Date).AddSeconds($Timeout)
  while ((Get-Date) -lt $deadline) {
    foreach ($uri in @("http://127.0.0.1:$Port/api/v1/system", "http://127.0.0.1:$Port/openapi.json", "http://127.0.0.1:$Port/docs")) {
      try {
        $r = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 6
        if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) {
          return $true
        }
      } catch {
        continue
      }
    }
    Start-Sleep -Milliseconds 700
  }
  return $false
}

if ([string]::IsNullOrWhiteSpace($RunId)) {
  $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
}

$repoRoot = AbsPath "."
$targetsPath = AbsPath $TargetsConfigPath
$providerPath = AbsPath $ProviderConfigPath
$outBase = AbsPath $OutputBaseDir
$runDir = Join-Path $outBase $RunId
EnsureDir $runDir

$global = [System.Collections.Generic.List[object]]::new()
$roots = [System.Collections.Generic.List[object]]::new()
$hasFail = $false

$targets = @(ParseTargets $targetsPath)
if ($CiMode) {
  $targets = @($targets | Where-Object { $_.ci_required })
}
if ((@($targets)).Count -eq 0) {
  throw "No targets to verify."
}

$riskLog = Join-Path $runDir "risk_areas.log"
if ($DryRun) {
  Set-Content -LiteralPath $riskLog -Value "DRY RUN"
  $global.Add((NewGate "baseline_risk_areas" "PASS" "global" "git status --short" $riskLog 0 ""))
} else {
  try {
    $lines = & git -C $repoRoot status --short
    $areas = $lines | ForEach-Object {
      if ($_.Length -ge 4) { (($_.Substring(3).Trim() -replace "\\", "/" -split "/")[0]) }
    } | Where-Object { $_ } | Sort-Object -Unique
    Set-Content -LiteralPath $riskLog -Value ("Changed top-level areas: " + ($areas -join ", "))
    $global.Add((NewGate "baseline_risk_areas" "PASS" "global" "git -C $repoRoot status --short" $riskLog 0 ""))
  } catch {
    $_ | Out-String | Set-Content -LiteralPath $riskLog
    $global.Add((NewGate "baseline_risk_areas" "WARN" "global" "git -C $repoRoot status --short" $riskLog 0 ""))
  }
}

$preflightDir = Join-Path $runDir "preflight"
EnsureDir $preflightDir

foreach ($tool in @("python", "node", "npm", "rustc", "cargo", "uv")) {
  $gate = "tool_$tool"
  $log = Join-Path $preflightDir "$gate.log"
  if ($null -eq (Get-Command $tool -ErrorAction SilentlyContinue)) {
    Set-Content -LiteralPath $log -Value "Missing command: $tool"
    $global.Add((NewGate $gate "FAIL" "global" $tool $log 0 ""))
    $hasFail = $true
    continue
  }
  $status = RunGate $global "global" $gate $repoRoot $log $tool @("--version")
  if ($status -eq "FAIL") { $hasFail = $true }
}

if (-not $SkipPythonVersionGate) {
  foreach ($version in $PythonVersions) {
    $gate = "python_$($version -replace '\.', '_')"
    $log = Join-Path $preflightDir "$gate.log"
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $py) {
      $status = RunGate $global "global" $gate $repoRoot $log $py.Source @("-$version", "--version")
    } else {
      $exe = "python$version"
      if ($null -eq (Get-Command $exe -ErrorAction SilentlyContinue)) {
        Set-Content -LiteralPath $log -Value "Missing: $exe"
        $global.Add((NewGate $gate "FAIL" "global" "$exe --version" $log 0 ""))
        $hasFail = $true
        continue
      }
      $status = RunGate $global "global" $gate $repoRoot $log $exe @("--version")
    }
    if ($status -eq "FAIL") { $hasFail = $true }
  }
}

if ($null -eq (Get-Command poetry -ErrorAction SilentlyContinue) -and $null -ne (Get-Command uv -ErrorAction SilentlyContinue)) {
  $status = RunGate $global "global" "install_poetry_with_uv" $repoRoot (Join-Path $preflightDir "install_poetry.log") "uv" @("tool", "install", "poetry")
  if ($status -eq "FAIL") { $hasFail = $true }
}
if ($null -eq (Get-Command nox -ErrorAction SilentlyContinue) -and $null -ne (Get-Command uv -ErrorAction SilentlyContinue)) {
  $status = RunGate $global "global" "install_nox_with_uv" $repoRoot (Join-Path $preflightDir "install_nox.log") "uv" @("tool", "install", "nox")
  if ($status -eq "FAIL") { $hasFail = $true }
}

$requiredWorkflows = @(
  ".github/workflows/test-unit-platform.yml",
  ".github/workflows/test-unit-cli.yml",
  ".github/workflows/test-unit-desktop-win64.yml",
  ".github/workflows/test-unit-desktop-winARM.yml",
  ".github/workflows/test-unit-desktop-osx64.yml",
  ".github/workflows/test-unit-desktop-osxARM.yml",
  ".github/workflows/general-linting.yml",
  ".github/workflows/test-integration-platform.yml",
  ".github/workflows/test-integration-cli.yml"
)
foreach ($wf in $requiredWorkflows) {
  $gate = "workflow_" + (($wf -replace "[^A-Za-z0-9]", "_").ToLowerInvariant())
  $log = Join-Path $preflightDir "$gate.log"
  if (Test-Path -LiteralPath (Join-Path $repoRoot $wf)) {
    Set-Content -LiteralPath $log -Value "Found: $wf"
    $global.Add((NewGate $gate "PASS" "global" "Test-Path $wf" $log 0 ""))
  } else {
    Set-Content -LiteralPath $log -Value "Missing: $wf"
    $global.Add((NewGate $gate "FAIL" "global" "Test-Path $wf" $log 0 ""))
    $hasFail = $true
  }
}

$noxFile = "nox"
$noxPrefix = @()
if ($null -eq (Get-Command nox -ErrorAction SilentlyContinue)) {
  $noxFile = "uv"
  $noxPrefix = @("tool", "run", "nox")
}
$psShell = "pwsh"
if ($null -eq (Get-Command $psShell -ErrorAction SilentlyContinue)) {
  $psShell = "powershell"
}

foreach ($target in $targets) {
  $root = RootLabel $target.path
  $rootPath = if ([System.IO.Path]::IsPathRooted($target.path)) { AbsPath $target.path } else { AbsPath (Join-Path $repoRoot $target.path) }
  $rootOut = Join-Path $runDir $root
  EnsureDir $rootOut
  $list = [System.Collections.Generic.List[object]]::new()
  $rootFail = $false

  if (-not (Test-Path -LiteralPath $rootPath)) {
    $log = Join-Path $rootOut "root_missing.log"
    Set-Content -LiteralPath $log -Value "Missing root: $rootPath"
    $list.Add((NewGate "root_exists" "FAIL" $root "Test-Path $rootPath" $log 0 ""))
    $rootFail = $true
    $hasFail = $true
    $roots.Add([pscustomobject]@{ root_path = $target.path; root_label = $root; ci_required = [bool]$target.ci_required; overall_status = "FAIL"; gates = @($list) })
    continue
  }

  $status = RunGate $list $root "baseline_git_status" $repoRoot (Join-Path $rootOut "baseline_git_status.log") "git" @("-C", $rootPath, "status", "--short") -WarnOnly
  if ($status -eq "FAIL") { $rootFail = $true }

  $doPlatform = [bool]$target.run_platform -and (-not $SkipPlatform)
  $doCli = [bool]$target.run_cli -and (-not $SkipCli)
  $doDesktop = [bool]$target.run_desktop -and (-not $SkipDesktop)
  $doFrontend = [bool]$target.run_frontend_components -and (-not $SkipFrontendComponents)

  if ($doPlatform) {
    $status = RunGate $list $root "deps_platform_install" $rootPath (Join-Path $rootOut "deps_platform_install.log") "python" @("openbb_platform/dev_install.py", "-e")
    if ($status -eq "FAIL") { $rootFail = $true }
  }
  if ($doCli) {
    $status = RunGate $list $root "deps_platform_cli_install" $rootPath (Join-Path $rootOut "deps_platform_cli_install.log") "python" @("openbb_platform/dev_install.py", "-e", "--cli")
    if ($status -eq "FAIL") { $rootFail = $true }
  }
  if ($doDesktop -and (Test-Path -LiteralPath (Join-Path $rootPath "desktop/package.json"))) {
    $status = RunGate $list $root "deps_desktop_npm_ci" (Join-Path $rootPath "desktop") (Join-Path $rootOut "deps_desktop_npm_ci.log") "npm" @("ci")
    if ($status -eq "FAIL") { $rootFail = $true }
  }
  if ($doFrontend) {
    foreach ($comp in @("frontend-components/plotly", "frontend-components/tables")) {
      if (Test-Path -LiteralPath (Join-Path $rootPath "$comp/package.json")) {
        $gate = "deps_" + (($comp -replace "[^A-Za-z0-9]", "_").ToLowerInvariant()) + "_npm_ci"
        $status = RunGate $list $root $gate (Join-Path $rootPath $comp) (Join-Path $rootOut "$gate.log") "npm" @("ci")
        if ($status -eq "FAIL") { $rootFail = $true }
      }
    }
  }

  if (-not $SkipStaticQuality) {
    if ($doPlatform -or $doCli) {
      $codespellSkip = ""
      if (Test-Path -LiteralPath (Join-Path $rootPath ".codespell.skip")) {
        $codespellSkip = ((Get-Content -LiteralPath (Join-Path $rootPath ".codespell.skip") | ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith("#") }) -join ",")
      }
      $codespellArgs = @("-m", "codespell", "--ignore-words=.codespell.ignore", "--quiet-level=2")
      if ($codespellSkip) { $codespellArgs += "--skip=$codespellSkip" }
      foreach ($item in @(
        @{ gate = "static_python_codespell"; args = $codespellArgs },
        @{ gate = "static_python_ruff"; args = @("-m", "ruff", "check", "openbb_platform", "cli") },
        @{ gate = "static_python_mypy"; args = @("-m", "mypy", "openbb_platform", "cli", "--ignore-missing-imports", "--scripts-are-modules", "--check-untyped-defs") },
        @{ gate = "static_python_pylint"; args = @("-m", "pylint", "openbb_platform", "cli") },
        @{ gate = "static_python_black"; args = @("-m", "black", "--check", "openbb_platform", "cli") }
      )) {
        $status = RunGate $list $root $item.gate $rootPath (Join-Path $rootOut "$($item.gate).log") "python" $item.args
        if ($status -eq "FAIL") { $rootFail = $true }
      }
    }
    if ($doDesktop -and (Test-Path -LiteralPath (Join-Path $rootPath "desktop"))) {
      foreach ($item in @(
        @{ gate = "static_desktop_cargo_fmt"; file = "cargo"; args = @("fmt", "--all", "--", "--check") },
        @{ gate = "static_desktop_cargo_clippy"; file = "cargo"; args = @("clippy", "--all-targets", "--all-features", "--", "-D", "warnings") },
        @{ gate = "static_desktop_npm_lint"; file = "npm"; args = @("run", "lint") },
        @{ gate = "static_desktop_tsc"; file = "npx"; args = @("tsc", "--noEmit") }
      )) {
        $status = RunGate $list $root $item.gate (Join-Path $rootPath "desktop") (Join-Path $rootOut "$($item.gate).log") $item.file $item.args
        if ($status -eq "FAIL") { $rootFail = $true }
      }
    }
  }

  if (-not $SkipUnitTests) {
    if ($doPlatform) {
      foreach ($py in $PythonVersions) {
        $gate = "unit_platform_py_" + ($py -replace "\.", "_")
        $args = @($noxPrefix + @("-f", ".github/scripts/noxfile.py", "-s", "unit_test_platform", "--python", $py))
        $status = RunGate $list $root $gate $rootPath (Join-Path $rootOut "$gate.log") $noxFile $args
        if ($status -eq "FAIL") { $rootFail = $true }
      }
      $status = RunGate $list $root "unit_targeted_python" $rootPath (Join-Path $rootOut "unit_targeted_python.log") "python" @("-m", "pytest", "openbb_platform/core/tests/app/test_extension_loader.py", "openbb_platform/extensions/quant_ml/tests/test_macro_fred_client.py")
      if ($status -eq "FAIL") { $rootFail = $true }
    }
    if ($doCli) {
      foreach ($py in $PythonVersions) {
        $gate = "unit_cli_py_" + ($py -replace "\.", "_")
        $args = @($noxPrefix + @("-f", ".github/scripts/noxfile.py", "-s", "unit_test_cli", "--python", $py))
        $status = RunGate $list $root $gate $rootPath (Join-Path $rootOut "$gate.log") $noxFile $args
        if ($status -eq "FAIL") { $rootFail = $true }
      }
    }
    if ($doDesktop -and (Test-Path -LiteralPath (Join-Path $rootPath "desktop"))) {
      foreach ($item in @(
        @{ gate = "unit_desktop_cargo_test"; file = "cargo"; args = @("test", "--all") },
        @{ gate = "unit_desktop_vitest"; file = "npm"; args = @("run", "test", "--", "--watch=false") },
        @{ gate = "unit_targeted_desktop_routes"; file = "npm"; args = @("run", "test", "--", "--watch=false", "src/tests/routes/__root.test.tsx", "src/tests/routes/macro.test.tsx", "src/tests/routes/execution.test.tsx", "src/tests/routes/ops.test.tsx") }
      )) {
        $status = RunGate $list $root $item.gate (Join-Path $rootPath "desktop") (Join-Path $rootOut "$($item.gate).log") $item.file $item.args
        if ($status -eq "FAIL") { $rootFail = $true }
      }
    }
    if ($doFrontend) {
      foreach ($comp in @("frontend-components/plotly", "frontend-components/tables")) {
        if (Test-Path -LiteralPath (Join-Path $rootPath "$comp/package.json")) {
          $gate = "unit_" + (($comp -replace "[^A-Za-z0-9]", "_").ToLowerInvariant()) + "_build"
          $status = RunGate $list $root $gate (Join-Path $rootPath $comp) (Join-Path $rootOut "$gate.log") "npm" @("run", "build")
          if ($status -eq "FAIL") { $rootFail = $true }
        }
      }
    }
  }

  if (-not $SkipIntegration -and ($doPlatform -or $doCli)) {
    $args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $repoRoot "qa/scripts/run_integration_gate.ps1"), "-RootPath", $rootPath, "-RunId", $RunId, "-OutputBaseDir", $outBase, "-ProviderConfigPath", $providerPath, "-PythonCommand", "python")
    if (-not $doPlatform) { $args += "-SkipPythonIntegration"; $args += "-SkipApiIntegration" }
    if (-not $doCli) { $args += "-SkipCliIntegration" }
    if ($DryRun) { $args += "-DryRun" }
    $status = RunGate $list $root "integration_gate" $repoRoot (Join-Path $rootOut "integration_gate.log") $psShell $args
    if ($status -eq "FAIL") { $rootFail = $true }
  }

  if (-not $SkipSmoke) {
    if ($doPlatform) {
      $smokeApiLog = Join-Path $rootOut "smoke_api_health.log"
      if ($DryRun) {
        Set-Content -LiteralPath $smokeApiLog -Value "DRY RUN"
        $list.Add((NewGate "smoke_api_health" "PASS" $root "openbb-api + health check" $smokeApiLog 0 ""))
      } else {
        $apiProcess = $null
        $started = $false
        $ok = $true
        try {
          if (-not (PortOpen "127.0.0.1" 8000)) {
            $apiExe = Join-Path $rootPath ".venv\Scripts\openbb-api.exe"
            if (-not (Test-Path -LiteralPath $apiExe)) {
              $apiExe = Join-Path $rootPath ".venv/bin/openbb-api"
            }
            if (-not (Test-Path -LiteralPath $apiExe)) {
              $cmd = Get-Command openbb-api -ErrorAction SilentlyContinue
              if ($null -ne $cmd) { $apiExe = $cmd.Source }
            }
            if (-not (Test-Path -LiteralPath $apiExe) -and [string]::IsNullOrWhiteSpace($apiExe)) {
              throw "openbb-api executable not found"
            }
            $apiProcess = Start-Process -FilePath $apiExe -ArgumentList @("--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $rootPath -RedirectStandardOutput (Join-Path $rootOut "smoke_api.stdout.log") -RedirectStandardError (Join-Path $rootOut "smoke_api.stderr.log") -PassThru
            $started = $true
          }
          if (-not (WaitApi -Port 8000 -Timeout 120)) {
            throw "API health check timeout"
          }
          Set-Content -LiteralPath $smokeApiLog -Value "API health check passed."
        } catch {
          $ok = $false
          $_ | Out-String | Set-Content -LiteralPath $smokeApiLog
        } finally {
          if ($started -and $null -ne $apiProcess) {
            Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
          }
        }
        $list.Add((NewGate "smoke_api_health" ($(if ($ok) { "PASS" } else { "FAIL" })) $root "openbb-api + health check" $smokeApiLog 0 ""))
        if (-not $ok) { $rootFail = $true }
      }

      $pySmoke = "from openbb import obb; assert hasattr(obb,'equity'); assert hasattr(obb,'economy'); assert hasattr(obb,'quant_ml') or hasattr(obb,'quantitative'); x=obb.equity.price.historical('AAPL',provider='yfinance',limit=1); assert x; print('ok')"
      $status = RunGate $list $root "smoke_python_domains" $rootPath (Join-Path $rootOut "smoke_python_domains.log") "python" @("-c", $pySmoke)
      if ($status -eq "FAIL") { $rootFail = $true }
    }

    if ($doCli) {
      $openbb = Get-Command openbb -ErrorAction SilentlyContinue
      if ($null -ne $openbb) {
        $status = RunGate $list $root "smoke_cli_help" $rootPath (Join-Path $rootOut "smoke_cli_help.log") $openbb.Source @("--help")
      } else {
        $status = RunGate $list $root "smoke_cli_help" $rootPath (Join-Path $rootOut "smoke_cli_help.log") "python" @("-m", "openbb_cli.cli", "--help")
      }
      if ($status -eq "FAIL") { $rootFail = $true }
    }

    if ($doDesktop -and (Test-Path -LiteralPath (Join-Path $rootPath "desktop"))) {
      $log = Join-Path $rootOut "smoke_desktop_devserver.log"
      if ($DryRun) {
        Set-Content -LiteralPath $log -Value "DRY RUN"
        $list.Add((NewGate "smoke_desktop_devserver" "PASS" $root "npm run dev -- --port $DesktopPort" $log 0 ""))
      } else {
        $dev = $null
        $ok = $true
        try {
          $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
          if ($null -eq $npm) { $npm = Get-Command npm -ErrorAction SilentlyContinue }
          if ($null -eq $npm) { throw "npm not found" }
          $dev = Start-Process -FilePath $npm.Source -ArgumentList @("run", "dev", "--", "--port", "$DesktopPort") -WorkingDirectory (Join-Path $rootPath "desktop") -RedirectStandardOutput (Join-Path $rootOut "smoke_desktop.stdout.log") -RedirectStandardError (Join-Path $rootOut "smoke_desktop.stderr.log") -PassThru
          $deadline = (Get-Date).AddSeconds(60)
          while ((Get-Date) -lt $deadline) {
            if (PortOpen "127.0.0.1" $DesktopPort) { break }
            Start-Sleep -Milliseconds 500
          }
          if (-not (PortOpen "127.0.0.1" $DesktopPort)) {
            throw "Desktop dev server did not open port $DesktopPort."
          }
          Set-Content -LiteralPath $log -Value "Desktop dev server reachable at $DesktopPort."
        } catch {
          $ok = $false
          $_ | Out-String | Set-Content -LiteralPath $log
        } finally {
          if ($null -ne $dev) { Stop-Process -Id $dev.Id -Force -ErrorAction SilentlyContinue }
        }
        $list.Add((NewGate "smoke_desktop_devserver" ($(if ($ok) { "PASS" } else { "FAIL" })) $root "npm run dev -- --port $DesktopPort" $log 0 ""))
        if (-not $ok) { $rootFail = $true }
      }
    }
  }

  $overall = if ($rootFail) { "FAIL" } else { "PASS" }
  if ($rootFail) { $hasFail = $true }
  $rootSummary = [pscustomobject]@{
    root_path = $target.path
    root_label = $root
    ci_required = [bool]$target.ci_required
    run_platform = [bool]$target.run_platform
    run_cli = [bool]$target.run_cli
    run_desktop = [bool]$target.run_desktop
    run_frontend_components = [bool]$target.run_frontend_components
    overall_status = $overall
    gates = @($list)
  }
  $roots.Add($rootSummary)
  $rootSummary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $rootOut "gates.json") -Encoding utf8
}

$summary = [ordered]@{
  run_id = $RunId
  generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  repo_root = $repoRoot
  output_directory = $runDir
  ci_mode = [bool]$CiMode
  dry_run = [bool]$DryRun
  python_versions = @($PythonVersions)
  provider_config = $providerPath
  verification_targets_config = $targetsPath
  overall_status = if ($hasFail) { "FAIL" } else { "PASS" }
  global_gates = @($global)
  roots = @($roots)
}
$summaryPath = Join-Path $runDir "run_summary.json"
$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summaryPath -Encoding utf8

$collect = RunCommand -FilePath "python" -CmdArgs @("qa/scripts/collect_results.py", "--run-dir", $runDir, "--output", (Join-Path $runDir "summary.json"), "--report", (Join-Path $repoRoot "docs/qa/full-verification.md")) -Cwd $repoRoot -LogFile (Join-Path $runDir "collect_results.log") -DryMode:$DryRun

if ($hasFail) {
  Write-Host "Full verification failed. See $summaryPath"
  exit 1
}

if ($collect.exit_code -ne 0) {
  Write-Host "Verification passed but result collection failed. See $summaryPath"
  exit 1
}

Write-Host "Full verification passed. See $summaryPath"
exit 0
