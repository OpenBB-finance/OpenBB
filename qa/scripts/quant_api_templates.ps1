[CmdletBinding()]
param(
  [string]$BaseUrl = "http://127.0.0.1:6900",
  [ValidateSet(
    "help",
    "quick-check",
    "runs-list",
    "train-sample",
    "run-status",
    "signals",
    "backtest",
    "walkforward-start",
    "walkforward-status",
    "macro-snapshot",
    "macro-refresh",
    "latest-meta",
    "print-sse-urls"
  )]
  [string]$Action = "help",
  [string]$RunId = "",
  [string]$JobId = "",
  [ValidateSet("lgbm_ranker", "xgb_lstm", "catboost_ranker")]
  [string]$Model = "lgbm_ranker",
  [string]$Provider = "yfinance",
  [string]$FundamentalProvider = "",
  [string]$StartDate = "2021-01-01",
  [string]$EndDate = (Get-Date -Format "yyyy-MM-dd"),
  [string[]]$Symbols = @("AAPL", "MSFT", "NVDA", "AMZN"),
  [int]$TopK = 20,
  [double]$ScoreThreshold = 0.5,
  [switch]$BalancedLongShort,
  [switch]$IncludeFundamentals,
  [switch]$IncludeSentiment,
  [int]$WalkforwardMinHistoryDays = 126
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$QUANT_PREFIX = "/api/v1/quant_ml"
$MACRO_PREFIX = "$QUANT_PREFIX/macro"
$QUANT_BASE = "$BaseUrl$QUANT_PREFIX"
$MACRO_BASE = "$BaseUrl$MACRO_PREFIX"

function Write-Section {
  param([string]$Title)
  Write-Host ""
  Write-Host "=== $Title ==="
}

function Show-Usage {
  Write-Host "Quant API templates script"
  Write-Host ""
  Write-Host "Base arguments:"
  Write-Host "  -BaseUrl http://127.0.0.1:6900"
  Write-Host "  -Model lgbm_ranker|xgb_lstm|catboost_ranker"
  Write-Host "  -RunId <run_id>"
  Write-Host ""
  Write-Host "Actions:"
  Write-Host "  help"
  Write-Host "  quick-check"
  Write-Host "  runs-list"
  Write-Host "  train-sample"
  Write-Host "  run-status"
  Write-Host "  signals"
  Write-Host "  backtest"
  Write-Host "  walkforward-start"
  Write-Host "  walkforward-status"
  Write-Host "  macro-snapshot"
  Write-Host "  macro-refresh"
  Write-Host "  latest-meta"
  Write-Host "  print-sse-urls"
  Write-Host ""
  Write-Host "Examples:"
  Write-Host "  .\qa\scripts\quant_api_templates.ps1 -Action quick-check"
  Write-Host "  .\qa\scripts\quant_api_templates.ps1 -Action train-sample -Provider fmp -IncludeFundamentals"
  Write-Host "  .\qa\scripts\quant_api_templates.ps1 -Action run-status -RunId <RUN_ID>"
  Write-Host "  .\qa\scripts\quant_api_templates.ps1 -Action signals -RunId <RUN_ID> -Model lgbm_ranker"
  Write-Host "  .\qa\scripts\quant_api_templates.ps1 -Action macro-snapshot"
}

function Write-Json {
  param([Parameter(ValueFromPipeline = $true)]$Value)
  $Value | ConvertTo-Json -Depth 20
}

function Invoke-QuantGet {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [int]$TimeoutSec = 60
  )
  Invoke-RestMethod -Method GET -Uri $Url -TimeoutSec $TimeoutSec
}

function Invoke-QuantPost {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)]$Body,
    [int]$TimeoutSec = 120
  )
  $json = $Body | ConvertTo-Json -Depth 20
  Invoke-RestMethod -Method POST -Uri $Url -ContentType "application/json" -Body $json -TimeoutSec $TimeoutSec
}

function Require-RunId {
  if ([string]::IsNullOrWhiteSpace($RunId)) {
    throw "RunId is required for action '$Action'."
  }
}

function New-TrainBody {
  $featureConfig = @{
    include_fundamentals = [bool]$IncludeFundamentals
    include_sentiment = [bool]$IncludeSentiment
    include_regime_features = $true
  }

  return @{
    symbols = $Symbols
    date_range = @{
      start = $StartDate
      end = $EndDate
    }
    provider = $Provider
    include_macro_features = $true
    macro_feature_subset = @("z_252", "yoy", "mom_3", "slope")
    feature_config = $featureConfig
    walk_forward_config = @{
      purging_mode = "purged_group_kfold"
      purged_n_splits = 5
      purged_embargo_pct = 0.01
    }
  } + $(if ([string]::IsNullOrWhiteSpace($FundamentalProvider)) { @{} } else { @{ fundamental_provider = $FundamentalProvider } })
}

function Build-LatestMetaQuery {
  $query = @()
  if (-not [string]::IsNullOrWhiteSpace($RunId)) {
    $query += "run_id=$([Uri]::EscapeDataString($RunId))"
  }
  if (-not [string]::IsNullOrWhiteSpace($Model)) {
    $query += "model_name=$([Uri]::EscapeDataString($Model))"
  }
  if ($query.Count -eq 0) {
    return ""
  }
  return "?$($query -join '&')"
}

try {
  switch ($Action) {
    "help" {
      Show-Usage
      break
    }

    "quick-check" {
      Write-Section "Connectivity"
      $docs = Invoke-WebRequest -Uri "$BaseUrl/docs" -UseBasicParsing -TimeoutSec 20
      Write-Host "docs status: $($docs.StatusCode)"

      Write-Section "Quant endpoints"
      $runs = Invoke-QuantGet "$QUANT_BASE/runs/list?limit=5"
      Write-Host "runs.list status: ok"
      $runs | Write-Json

      $health = Invoke-QuantGet "$QUANT_BASE/health"
      Write-Host "quant health status: $($health.status)"

      Write-Section "Macro endpoints"
      $macroHealth = Invoke-QuantGet "$MACRO_BASE/health"
      Write-Host "macro health status: $($macroHealth.status)"

      $scheduler = Invoke-QuantGet "$MACRO_BASE/regime/scheduler/status"
      Write-Host "scheduler running: $($scheduler.running)"
      break
    }

    "runs-list" {
      Invoke-QuantGet "$QUANT_BASE/runs/list?limit=20" | Write-Json
      break
    }

    "train-sample" {
      Write-Section "Train request"
      $body = New-TrainBody
      $body | Write-Json
      Write-Section "Train response"
      $res = Invoke-QuantPost "$QUANT_BASE/train" $body
      $res | Write-Json
      break
    }

    "run-status" {
      Require-RunId
      Invoke-QuantGet "$QUANT_BASE/runs/$RunId" | Write-Json
      break
    }

    "signals" {
      Require-RunId
      $body = @{
        run_id = $RunId
        model_name = $Model
        top_k = $TopK
        score_threshold = $ScoreThreshold
        balanced_long_short = [bool]$BalancedLongShort
      }
      Invoke-QuantPost "$QUANT_BASE/signals" $body | Write-Json
      break
    }

    "backtest" {
      Require-RunId
      $body = @{
        run_id = $RunId
        model_name = $Model
        start_date = $StartDate
        end_date = $EndDate
      }
      Invoke-QuantPost "$QUANT_BASE/backtest" $body | Write-Json
      break
    }

    "walkforward-start" {
      Require-RunId
      $body = @{
        run_id = $RunId
        model_name = $Model
        start_date = $StartDate
        end_date = $EndDate
        min_history_days = $WalkforwardMinHistoryDays
      }
      Invoke-QuantPost "$QUANT_BASE/backtest/walkforward" $body | Write-Json
      break
    }

    "walkforward-status" {
      if ([string]::IsNullOrWhiteSpace($JobId)) {
        throw "JobId is required for action 'walkforward-status'."
      }
      Invoke-QuantGet "$QUANT_BASE/backtest/walkforward/$JobId" | Write-Json
      break
    }

    "macro-snapshot" {
      Write-Section "Regime latest"
      Invoke-QuantGet "$MACRO_BASE/regime?freq=W&fill=ffill" | Write-Json
      Write-Section "Regime transitions"
      Invoke-QuantGet "$MACRO_BASE/regime/transitions?threshold=10" | Write-Json
      Write-Section "Regime HMM"
      Invoke-QuantGet "$MACRO_BASE/regime/hmm?n_states=4" | Write-Json
      break
    }

    "macro-refresh" {
      Invoke-QuantPost "$MACRO_BASE/regime/refresh" @{} | Write-Json
      break
    }

    "latest-meta" {
      $query = Build-LatestMetaQuery
      Write-Section "run/latest/meta"
      Invoke-QuantGet "$QUANT_BASE/run/latest/meta$query" | Write-Json
      Write-Section "run/latest/risk"
      Invoke-QuantGet "$QUANT_BASE/run/latest/risk$query" | Write-Json
      Write-Section "run/latest/exposures"
      Invoke-QuantGet "$QUANT_BASE/run/latest/exposures$query" | Write-Json
      Write-Section "run/latest/constraints"
      Invoke-QuantGet "$QUANT_BASE/run/latest/constraints$query" | Write-Json
      break
    }

    "print-sse-urls" {
      Write-Section "SSE URLs"
      if (-not [string]::IsNullOrWhiteSpace($RunId)) {
        Write-Host "run stream:"
        Write-Host "$QUANT_BASE/runs/$RunId/stream?poll_interval_sec=1&max_seconds=600"
      } else {
        Write-Host "run stream: set -RunId to print run stream URL"
      }
      Write-Host "macro regime stream:"
      Write-Host "$MACRO_BASE/regime/stream?interval_sec=60"
      break
    }
  }
} catch {
  Write-Error $_
  exit 1
}
