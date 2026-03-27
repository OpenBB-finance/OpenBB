param(
  [string]$RepoRoot = ".",
  [int]$TimeoutSeconds = 180,
  [bool]$ApiNoBuild = $true,
  [string]$ApiAuthUsername = "smoke",
  [string]$ApiAuthPassword = "smoke-pass",
  [bool]$Cleanup = $true
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Resolve-Abs {
  param([string]$Path)
  return (Resolve-Path -LiteralPath $Path).Path
}

function Get-FreeTcpPort {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
  $listener.Start()
  try {
    return ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
  }
  finally {
    $listener.Stop()
  }
}

function Get-BasicAuthHeader {
  param(
    [string]$Username,
    [string]$Password
  )
  $bytes = [System.Text.Encoding]::UTF8.GetBytes(("{0}:{1}" -f $Username, $Password))
  return "Basic " + [Convert]::ToBase64String($bytes)
}

function Stop-PortProcesses {
  param([int[]]$Ports)
  $pids = @(Get-NetTCPConnection -LocalPort $Ports -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
  foreach ($procId in $pids) {
    if (-not $procId) {
      continue
    }
    try {
      Stop-Process -Id $procId -Force -ErrorAction Stop
    }
    catch {
      Write-Warning ("Failed to stop PID {0}: {1}" -f $procId, $_.Exception.Message)
    }
  }
}

$repoAbs = Resolve-Abs $RepoRoot
$logsDir = Join-Path $repoAbs "logs\qa_startup_smoke"
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

$apiPort = Get-FreeTcpPort
$frontendPort = Get-FreeTcpPort
while ($frontendPort -eq $apiPort) {
  $frontendPort = Get-FreeTcpPort
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$consoleLog = Join-Path $logsDir ("startup_smoke_{0}.console.log" -f $stamp)
$startScript = Join-Path $repoAbs "start_all.ps1"
try {
  $startedAt = Get-Date
  & $startScript `
    -ApiPort $apiPort `
    -FrontendPort $frontendPort `
    -ApiAuthMode enabled `
    -ApiAuthUsername $ApiAuthUsername `
    -ApiAuthPassword $ApiAuthPassword `
    -ApiNoBuild:$ApiNoBuild *>&1 | Tee-Object -FilePath $consoleLog | Out-Null
  $elapsedSec = ((Get-Date) - $startedAt).TotalSeconds
  if ($elapsedSec -gt $TimeoutSeconds) {
    throw ("start_all.ps1 exceeded timeout budget ({0:N1}s > {1}s)." -f $elapsedSec, $TimeoutSeconds)
  }

  $probeUri = "http://127.0.0.1:{0}/api/v1/coverage/providers" -f $apiPort
  $unauthorizedStatus = 0
  try {
    Invoke-WebRequest -Uri $probeUri -UseBasicParsing -TimeoutSec 5 | Out-Null
    throw "Coverage probe unexpectedly succeeded without authentication."
  }
  catch {
    if ($_.Exception.Response) {
      $unauthorizedStatus = [int]$_.Exception.Response.StatusCode.value__
    }
    else {
      throw
    }
  }
  if ($unauthorizedStatus -ne 401) {
    throw "Expected 401 without auth, got $unauthorizedStatus."
  }

  $authorizedResponse = Invoke-WebRequest `
    -Uri $probeUri `
    -UseBasicParsing `
    -TimeoutSec 5 `
    -Headers @{ Authorization = (Get-BasicAuthHeader -Username $ApiAuthUsername -Password $ApiAuthPassword) }
  if ($authorizedResponse.StatusCode -lt 200 -or $authorizedResponse.StatusCode -ge 300) {
    throw "Expected authenticated 2xx response, got $($authorizedResponse.StatusCode)."
  }

  $frontendListening = $false
  $frontendDeadline = (Get-Date).AddSeconds(15)
  while ((Get-Date) -lt $frontendDeadline) {
    $conn = Get-NetTCPConnection -LocalPort $frontendPort -ErrorAction SilentlyContinue
    if ($conn) {
      $frontendListening = $true
      break
    }
    Start-Sleep -Milliseconds 500
  }
  if (-not $frontendListening) {
    throw "Frontend port $frontendPort did not begin listening."
  }

  Write-Host ("startup_smoke_pass api={0} frontend={1} auth=basic" -f $apiPort, $frontendPort)
}
finally {
  if ($Cleanup) {
    Stop-PortProcesses -Ports @($apiPort, $frontendPort)
  }
}
