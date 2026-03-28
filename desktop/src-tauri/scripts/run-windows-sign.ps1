$requiredEnvVars = @(
    "GITHUB_WORKSPACE",
    "ESIGNER_USERNAME",
    "ESIGNER_PASSWORD",
    "ESIGNER_CREDENTIAL_ID",
    "ESIGNER_TOTP_SECRET"
)

$missing = @()
foreach ($name in $requiredEnvVars) {
    if ([string]::IsNullOrWhiteSpace((Get-Item -Path "Env:$name" -ErrorAction SilentlyContinue).Value)) {
        $missing += $name
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Skipping Windows signing. Missing environment: $($missing -join ', ')"
    exit 0
}

$scriptPath = Join-Path $PSScriptRoot "sign.ps1"
& powershell -ExecutionPolicy Bypass -File $scriptPath
exit $LASTEXITCODE
