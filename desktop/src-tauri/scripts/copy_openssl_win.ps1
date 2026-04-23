# Copies OpenSSL runtime DLLs from the vcpkg install tree into desktop/src-tauri/
# so the Tauri bundler can pick them up via the `resources` entries in
# tauri.windows.conf.json. Invoked by the `openssl:copy` npm script and
# Tauri's beforeBuildCommand / beforeDevCommand hooks.
#
# Env vars:
#   VCPKG_ROOT                  - required; path to the vcpkg checkout.
#   OPENSSL_COPY_SKIP_EXISTING  - when set to "1", skip copy if target DLLs
#                                 already exist. The release workflow sets
#                                 this before invoking `tauri build` so the
#                                 hook does not clobber workflow-signed DLLs.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$srcTauriDir = Resolve-Path (Join-Path $scriptDir "..")

$vcpkgRoot = $env:VCPKG_ROOT
if ([string]::IsNullOrWhiteSpace($vcpkgRoot)) {
    Write-Error "[copy_openssl_win] VCPKG_ROOT is not set. Install OpenSSL via vcpkg and export VCPKG_ROOT before running."
    exit 1
}

$triplet = "x64-windows"

$binDir = Join-Path $vcpkgRoot "installed/$triplet/bin"
if (-not (Test-Path $binDir)) {
    Write-Error "[copy_openssl_win] vcpkg OpenSSL bin dir not found: $binDir. Did you run 'vcpkg install openssl:$triplet'?"
    exit 1
}

$targets = @(
    @{ Pattern = "libcrypto-3-*.dll"; Dest = "libcrypto-3-x64.dll" },
    @{ Pattern = "libssl-3-*.dll";    Dest = "libssl-3-x64.dll" }
)

$skipExisting = $env:OPENSSL_COPY_SKIP_EXISTING -eq "1"

foreach ($t in $targets) {
    $destPath = Join-Path $srcTauriDir $t.Dest

    if ($skipExisting -and (Test-Path $destPath)) {
        Write-Host "[copy_openssl_win] OPENSSL_COPY_SKIP_EXISTING=1 and $($t.Dest) already present; skipping."
        continue
    }

    $source = Get-ChildItem -Path $binDir -Filter $t.Pattern -File | Select-Object -First 1
    if ($null -eq $source) {
        Write-Error "[copy_openssl_win] No DLL matching '$($t.Pattern)' in $binDir."
        exit 1
    }

    Copy-Item -Path $source.FullName -Destination $destPath -Force
    Write-Host "[copy_openssl_win] Copied $($source.Name) -> $destPath"
}
