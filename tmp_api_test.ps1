$base = "http://127.0.0.1:6900"
$endpoints = @(
    "/api/v1/quant_ml/run/latest/meta",
    "/api/v1/quant_ml/portfolio/policy",
    "/api/v1/quant_ml/macro/regime",
    "/api/v1/quant_ml/macro/alerts",
    "/api/v1/quant_ml/macro/regime/scheduler/status",
    "/api/v1/quant_ml/ops/status",
    "/api/v1/quant_ml/model/promoted"
)

foreach ($ep in $endpoints) {
    $url = "$base$ep"
    Write-Host "--- $ep ---"
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        Write-Host ("  Status: {0}" -f $r.StatusCode)
        $body = $r.Content
        if ($body.Length -gt 300) { $body = $body.Substring(0, 300) + "..." }
        Write-Host ("  Body: {0}" -f $body)
    }
    catch {
        $statusCode = "CONNECTION_ERROR"
        $detail = $_.Exception.Message
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            try {
                $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
                $detail = $reader.ReadToEnd()
                $reader.Close()
            }
            catch {}
        }
        Write-Host ("  Status: {0}" -f $statusCode)
        $detailShort = $detail
        if ($detail.Length -gt 400) { $detailShort = $detail.Substring(0, 400) + "..." }
        Write-Host ("  Detail: {0}" -f $detailShort)
    }
    Write-Host ""
}
