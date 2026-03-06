# OpenBB Quant ML ?¬ìš© ê°€?´ë“œ (v4 ?µí•© ë°˜ì˜)

?‘ì„±?? 2026-02-28  
?€???Œí¬?¸ë¦¬: `OpenBB-develop`  
ê¸°ì?: ?„ì¬ ì½”ë“œ êµ¬í˜„ ?íƒœ (`start_all.ps1`, `quant_ml_router.py`, `macro_router.py`, `desktop/src/*`)

## 1. ë¹ ë¥¸ ?œì‘

### 1.1 ê¶Œì¥ ?¤í–‰ (ë°±ì—”??+ ?„ë¡ ???™ì‹œ)

```powershell
cd "C:\Users\yygg1\OneDrive\ë°”íƒ• ?”ë©´\bot\OpenBB-develop"
.\start_all.ps1
```

?•ìƒ ?œì‘ ??
1. API: `http://127.0.0.1:6900/docs`
2. Frontend: `http://localhost:1470/quant`

`start_all.ps1` ?ë™ ì²˜ë¦¬:
1. ê¸°ì¡´ ?ˆê±°??startup shell ?•ë¦¬
2. OpenBB API ?¤í–‰ (`.venv\Scripts\openbb-api.exe`)
3. Desktop dev server ?¤í–‰ (`npm run dev`)
4. ?¬ìŠ¤ì²´í¬/?¬íŠ¸ ?•ì¸
5. ë¡œê·¸ ?Œì¼ ê²½ë¡œ ì¶œë ¥

### 1.2 ?˜ë™ ?¤í–‰

ë°±ì—”??

```powershell
cd "C:\Users\yygg1\OneDrive\ë°”íƒ• ?”ë©´\bot\OpenBB-develop"
.\.venv\Scripts\openbb-api.exe --host 127.0.0.1 --port 6900 --no-build
```

?„ë¡ ??

```powershell
cd "C:\Users\yygg1\OneDrive\ë°”íƒ• ?”ë©´\bot\OpenBB-develop\desktop"
if (!(Test-Path .\node_modules)) { npm ci }
npm run dev -- --port 1470
```

### 1.3 ?íƒœ ?•ì¸

```powershell
Invoke-WebRequest "http://127.0.0.1:6900/docs" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://localhost:1470/quant" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

????`200`?´ë©´ ?•ìƒ?…ë‹ˆ??

## 2. ?”ë©´ êµ¬ì„±

### 2.1 Quant Lab (`/quant`)

?µì‹¬ ?™ìŠµ/? í˜¸/ë°±í…Œ?¤íŠ¸ ?”ë©´?…ë‹ˆ??

ì£¼ìš” ?¤ì •:
1. `Model`: `lgbm_ranker | xgb_lstm | catboost_ranker`
2. `Data Provider`: `yfinance | fmp | polygon`
3. `Fundamental Momentum` (?¬ë¬´ ?¼ì²˜ ? ê?)
4. `Fundamental Provider` (ë¯¸ì?????data provider?€ ?™ì¼)
5. `Market Sentiment (preview)` (?€??? ê? ?œê³µ, ë°±ì—”??no-op ê²½ë¡œ ?¬í•¨)
6. `Purging Mode`: `legacy_month_cutoff | strict_label_overlap | purged_group_kfold`
7. `HPO`: `thorough` ?„ë¦¬?‹ì—???œì„±

### 2.2 Dashboard (`/dashboard`)

??
1. `Summary`
2. `Performance`
3. `Risk`
4. `Portfolio`
5. `Model`
6. `Regime`

`Regime` ???œê³µ:
1. LIVE ?°ê²° ?íƒœ
2. ?„ì¬ ?ˆì§ ?íƒœ ì¹´ë“œ
3. 5ì¶??ˆì´??4. HMM ?€?„ë¼??5. ?„í™˜ ?´ë²¤???Œì´ë¸?6. ë§¤í¬ë¡??Œë¦¼ ?¨ë„
7. ?˜ë™ ê°±ì‹  ë²„íŠ¼ (`/macro/regime/refresh`)

## 3. ?°ì´??ê²½ë¡œ (Core ?°ì„  + fallback)

### 3.1 ì£¼ì‹ ê°€ê²??°ì´??(`service/data_loader.py`)

`load_symbol_prices(..., provider="...")`:
1. providerê°€ `yfinance`ê°€ ?„ë‹ˆë©?`obb.equity.price.historical(...)` ?°ì„ 
2. ?¤íŒ¨/ë¹??°ì´????`yfinance.download(...)` fallback
3. ìºì‹œ ë³‘í•© ??`update_data_version(..., source=<?¤ì‚¬??provider>)` ê¸°ë¡

?µì‹¬:
1. `to_df()`/`to_dataframe()` ëª¨ë‘ ì²˜ë¦¬
2. normalize ì»¬ëŸ¼: `date/open/high/low/close/volume/symbol`
3. fallback ë°œìƒ ??warning ë¡œê·¸ ê¸°ë¡

### 3.2 FRED ?°ì´??(`service/macro_update.py`, `service/macro_catalog.py`)

?°ì„ ?œìœ„:
1. `obb.economy.fred_series` / `obb.economy.fred_search`
2. ?¤íŒ¨ ??`macro_fred_client.py` (deprecated fallback)
3. ë¡œì»¬ DB ìºì‹œ fallback

ì°¸ê³ :
1. `macro_fred_client.py`???„ì¬ ?? œê°€ ?„ë‹ˆ??fallback-only ?©ë„ë¡?? ì??©ë‹ˆ??

## 4. ?™ìŠµ ?”ì²­ ?¤í‚¤ë§??µì‹¬

`TrainRequest` ì£¼ìš” ?„ë“œ:
1. `provider: str = "yfinance"`
2. `fundamental_provider: str | None`
3. `feature_config.include_fundamentals: bool`
4. `feature_config.include_sentiment: bool`
5. `hpo_config` + ?ˆê±°??`enable_hpo/hpo_n_trials`
6. `symbols` ìµœë? 5000ê°??œí•œ

## 5. Quant API ?µì‹¬ ?”ë“œ?¬ì¸??
ê¸°ë³¸ prefix: `/api/v1/quant_ml`

1. `POST /train`
2. `GET /runs/list`
3. `GET /runs/{run_id}`
4. `GET /runs/{run_id}/stream` (SSE)
5. `POST /signals`
6. `POST /backtest`
7. `POST /backtest/walkforward`
8. `GET /backtest/walkforward/{job_id}`
9. `GET /portfolio/policy`
10. `GET /run/latest/meta`
11. `GET /run/latest/risk`
12. `GET /run/latest/exposures`
13. `GET /run/latest/constraints`

## 6. Macro / Regime API

Macro canonical prefix: `/api/v1/quant_ml/macro`  
Macro alias prefix: `/api/v1/macro`

1. `GET /macro/regime`
2. `GET /macro/alerts`
3. `GET /macro/regime/transitions`
4. `GET /macro/regime/hmm`
5. `GET /macro/regime/stream` (SSE)
6. `GET /macro/regime/scheduler/status`
7. `POST /macro/regime/refresh`

## 7. Regime ?¤ì?ì¤„ëŸ¬

`service/regime_scheduler.py` ê¸°ì?:
1. 30ë¶?ê°„ê²© ?œì¥ ?°ì´??ê°±ì‹  (`SPY/HYG/TLT/VIX/GLD/DBC`)
2. ë§¤ì¼ 07:00 KST FRED ê¸°ë³¸ ?œë¦¬ì¦?ê°±ì‹ 
3. lazy singleton ?œì‘ (`stream/status/refresh` ?¸ì¶œ ???ë™ ?œì‘)
4. `atexit` cleanup ?±ë¡
5. `apscheduler` ë¯¸ì„¤ì¹???scheduler ë¹„í™œ??+ warning ë¡œê·¸

## 8. ë¡œê·¸ ?„ì¹˜

1. `logs/startup_api_<timestamp>.out.log`
2. `logs/startup_api_<timestamp>.err.log`
3. `logs/startup_frontend_<timestamp>.out.log`
4. `logs/startup_frontend_<timestamp>.err.log`

## 9. ?´ì˜ ?ê? ì²´í¬ë¦¬ìŠ¤??
1. API ?°ê²°: `/docs` 200
2. Front ?°ê²°: `/quant` 200
3. ìµœê·¼ run ëª©ë¡: `/runs/list`
4. ìµœì‹  run ë©”í?: `/run/latest/meta`
5. ?•ì±… ?•ì¸: `/portfolio/policy`
6. Macro health: `/api/v1/quant_ml/macro/health`
7. Regime stream ?°ê²° ?•ì¸

## 10. ?¸ëŸ¬ë¸”ìŠˆ??
### 10.1 ?œë²„ê°€ ??????
```powershell
netstat -ano | findstr :6900
netstat -ano | findstr :1470
```

### 10.2 Provider ?¤íŒ¨

1. `fmp/polygon` ?¤íŒ¨ ??ê°€ê²??°ì´?°ëŠ” `yfinance` fallback ê°€??2. fallback warning ë¡œê·¸ê°€ ?¨ëŠ”ì§€ ?•ì¸

### 10.3 HMM unavailable

1. `/macro/regime/hmm`ê°€ `insufficient_data`ë©?`hmmlearn` ?¤ì¹˜ ?•ì¸
2. transitions/scores APIê°€ ?•ìƒ?¸ì? ë¶„ë¦¬ ?•ì¸

## 11. ê¶Œì¥ ?‘ì† URL

1. Quant Lab: `http://localhost:1470/quant`
2. Dashboard(Regime ??: `http://localhost:1470/dashboard?tab=regime`
3. Macro ?˜ì´ì§€: `http://localhost:1470/macro`
4. API Docs: `http://127.0.0.1:6900/docs`

## 12. ?€ ?œì? API ?œí”Œë¦?
?„ë˜ ?œí”Œë¦¿ì? ?€ ê³µí†µ ?¤í–‰ ?¨í„´?…ë‹ˆ??  
?´ì˜/QA/ê°œë°œ ëª¨ë‘ ?™ì¼??ë³€?˜ëª…/?œì„œë¥??¬ìš©?©ë‹ˆ??

### 12.0 ?ë™???¤í¬ë¦½íŠ¸

?œí”Œë¦¿ì„ ë°”ë¡œ ?¤í–‰?˜ë ¤ë©??„ë˜ ?¤í¬ë¦½íŠ¸ë¥??¬ìš©?˜ì„¸??

1. ?Œì¼: `qa/scripts/quant_api_templates.ps1`
2. ?„ì?ë§?

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\qa\scripts\quant_api_templates.ps1 -Action help
```

3. ë¹ ë¥¸ ?ê?:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\qa\scripts\quant_api_templates.ps1 -Action quick-check
```

### 12.1 ê³µí†µ ?˜ê²½ë³€???œí”Œë¦?(PowerShell)

```powershell
$BASE_URL = "http://127.0.0.1:6900"
$QUANT = "$BASE_URL/api/v1/quant_ml"
$MACRO = "$QUANT/macro"
$RUN_ID = "<RUN_ID>"
$MODEL = "lgbm_ranker"   # lgbm_ranker | xgb_lstm | catboost_ranker
```

### 12.2 ê³µí†µ ?¸ì¶œ ?¬í¼ (PowerShell)

```powershell
function Invoke-QuantGet {
  param([string]$Url)
  Invoke-RestMethod -Method GET -Uri $Url -TimeoutSec 60
}

function Invoke-QuantPost {
  param([string]$Url, [object]$Body)
  Invoke-RestMethod -Method POST -Uri $Url -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 20) -TimeoutSec 120
}
```

### 12.3 ?™ìŠµ ?”ì²­ ?œí”Œë¦?(PowerShell)

```powershell
$trainBody = @{
  symbols = @("AAPL","MSFT","NVDA","AMZN")
  date_range = @{
    start = "2021-01-01"
    end = "2026-02-28"
  }
  provider = "fmp"
  fundamental_provider = "fmp"
  include_macro_features = $true
  macro_feature_subset = @("z_252","yoy","mom_3","slope")
  feature_config = @{
    include_fundamentals = $true
    include_sentiment = $false
    include_regime_features = $true
  }
  walk_forward_config = @{
    purging_mode = "purged_group_kfold"
    purged_n_splits = 5
    purged_embargo_pct = 0.01
  }
  hpo_config = @{
    enabled = $true
    n_trials = 25
    timeout_sec = 1800
    objective_metric = "val_ic"
    random_state = 42
  }
}

$trainRes = Invoke-QuantPost "$QUANT/train" $trainBody
$RUN_ID = $trainRes.run_id
$RUN_ID
```

### 12.4 ?™ìŠµ ?”ì²­ ?œí”Œë¦?(curl)

```bash
curl -X POST "http://127.0.0.1:6900/api/v1/quant_ml/train" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL","MSFT","NVDA","AMZN"],
    "date_range": {"start":"2021-01-01","end":"2026-02-28"},
    "provider": "fmp",
    "fundamental_provider": "fmp",
    "feature_config": {
      "include_fundamentals": true,
      "include_sentiment": false,
      "include_regime_features": true
    }
  }'
```

### 12.5 ?¤í–‰ ?íƒœ/SSE ?œí”Œë¦?
PowerShell:

```powershell
Invoke-QuantGet "$QUANT/runs/list?limit=20"
Invoke-QuantGet "$QUANT/runs/$RUN_ID"
```

curl SSE:

```bash
curl -N "http://127.0.0.1:6900/api/v1/quant_ml/runs/<RUN_ID>/stream?poll_interval_sec=1&max_seconds=600"
```

### 12.6 Signals/Backtest ÅÛÇÃ¸´
```powershell
$signalBody = @{
  run_id = $RUN_ID
  model_name = $MODEL
  top_k = 20
  score_threshold = 0.5
  balanced_long_short = $false
}
Invoke-QuantPost "$QUANT/signals" $signalBody

$backtestBody = @{
  run_id = $RUN_ID
  model_name = $MODEL
  start = "2024-01-01"
  end = "2026-02-28"
  rebalance = "monthly"
  constraints = @{
    max_weight = 0.05
    long_only = $true
    risk_aversion = 3.0
    lookback_days = 126
    optimizer_mode = "mv"
    turnover_limit = 1.0
    gross_exposure_max = 1.5
    net_exposure_min = 0.0
    net_exposure_max = 1.0
    sector_max_weight = 0.35
  }
  cost_bps = 10
  slippage_bps = 2
  entry_price = "next_open"
  exit_price = "close"
  portfolio_mode = "long_only"
  mu_mapping = "quantile_mean_return"
}
Invoke-QuantPost "$QUANT/backtest" $backtestBody
```

¼Óµµ °ü·Ã Âü°í:
1. µ¿ÀÏ ÆÄ¶ó¹ÌÅÍ(µ¿ÀÏ `run_id/model/start/end/constraints`)·Î ÀçÈ£ÃâÇÏ¸é ÀúÀåµÈ backtest artifact Ä³½Ã°¡ »ç¿ëµË´Ï´Ù.
2. `start/end` ¶Ç´Â `constraints`°¡ ¹Ù²î¸é »õ·Î °è»êµË´Ï´Ù.
### 12.7 Walkforward ?œí”Œë¦?
```powershell
$wfBody = @{
  run_id = $RUN_ID
  model_name = $MODEL
  date_range = @{ start = "2021-01-01"; end = "2026-02-28" }
}
$wf = Invoke-QuantPost "$QUANT/backtest/walkforward" $wfBody
$jobId = $wf.job_id
Invoke-QuantGet "$QUANT/backtest/walkforward/$jobId"
```

### 12.8 Macro/Regime ?œí”Œë¦?
```powershell
Invoke-QuantGet "$MACRO/regime?freq=W&fill=ffill"
Invoke-QuantGet "$MACRO/regime/transitions?threshold=10"
Invoke-QuantGet "$MACRO/regime/hmm?n_states=4"
Invoke-QuantGet "$MACRO/regime/scheduler/status"
Invoke-QuantPost "$MACRO/regime/refresh" @{}
```

Macro SSE:

```bash
curl -N "http://127.0.0.1:6900/api/v1/quant_ml/macro/regime/stream?interval_sec=60"
```

### 12.9 ?´ì˜ ë©”í? ?œí”Œë¦?
```powershell
Invoke-QuantGet "$QUANT/run/latest/meta?model_name=$MODEL"
Invoke-QuantGet "$QUANT/run/latest/risk?model_name=$MODEL"
Invoke-QuantGet "$QUANT/run/latest/exposures?model_name=$MODEL"
Invoke-QuantGet "$QUANT/run/latest/constraints?model_name=$MODEL"
```

### 12.10 ?ëŸ¬ ?‘ë‹µ ?œì? ?•ì¸

```powershell
try {
  Invoke-QuantGet "$QUANT/runs/not_exists"
} catch {
  $_.Exception.Message
}
```

ê²€ì¦??¬ì¸??
1. `404`: ?†ëŠ” run_id
2. `400`: ?˜ëª»???Œë¼ë¯¸í„°
3. `429`: `/train` ê³¼í˜¸ì¶?(rate limit)

## 13. ?ë™???´ì˜

### 13.1 ?Œë¦¼ ?¤ì • (`jobs/steps/notify.py`)

?™ìŠµ/ê²€ì¦?Job ?„ë£Œ ???Œë¦¼???„ì†¡?©ë‹ˆ??

?¤ì • ë°©ë²• (?˜ê²½ë³€???ëŠ” `ops_jobs.yaml`):

```powershell
$env:NOTIFY_CHANNELS = "slack,discord"
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/..."
$env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
```

ì§€??ì±„ë„:
1. **Slack** ??Incoming Webhook
2. **Discord** ??Embed Webhook
3. **Webhook** ??ë²”ìš© JSON POST

### 13.2 ? íƒ??ë°±í•„ (`jobs/steps/backfill_if_needed.py`)

ë§¤ì¼ ?¤í–‰ ???„ì²´ ?œì¥ ?°ì´?°ë? ?¤ì‹œ ë°›ì? ?Šê³ , ?¤ë˜???¬ë³¼ë§?? ë³„ ?…ë°?´íŠ¸?©ë‹ˆ??

`ops_jobs.yaml` ?¤ì •:

```yaml
daily:
  backfill_staleness_days: 3    # 3???´ìƒ ë¯¸ê°±?????¬ë‹¤?´ë¡œ??  backfill_force_full: false    # trueë¡??¤ì • ???„ì²´ ?…ë°?´íŠ¸
```

### 13.3 ?´ì˜ Job ?¤ì • (`config/ops_jobs.yaml`)

| ì£¼ê¸° | ì£¼ìš” ?‘ì—… |
|------|----------|
| `daily` | ?œì¥ ?°ì´??ê°±ì‹ , ?ˆì¸¡ ê°±ì‹ , ?Œë¦¼ |
| `weekly` | ëª¨ë¸ ?¬í•™??(LightGBM, HPO 8?? |
| `monthly` | ?•ì¥ ?™ìŠµ (HPO 20?? 5??lookback) |

## 14. QA / ê²€ì¦?
?ì„¸ ê°€?´ë“œ: `qa/README.md`

ì£¼ìš” ëª…ë ¹??

```powershell
# ?„ì²´ ?„ë¡œ?íŠ¸ ê²€ì¦?.\qa\scripts\run_full_verification.ps1

# Quant ML ?„ìš© ê²€ì¦?.\qa\scripts\quant_ml_verify_full.ps1

# ?„ë¡œë°”ì´???µí•© ?ŒìŠ¤??.\qa\scripts\run_integration_gate.ps1

# ê³„ì•½ ?¸ë²¤? ë¦¬ ?ì„±
python qa\scripts\quant_ml_contract_inventory.py
python qa\scripts\quant_ml_frontend_contract_inventory.py
```

## 15. ì°¸ê³ 

??ë¬¸ì„œ??2026-02-28 ê¸°ì? ?Œí¬?¸ë¦¬ ?¤ì œ êµ¬í˜„??ë°˜ì˜?©ë‹ˆ??  
?”ë“œ?¬ì¸???¤í‚¤ë§?ë³€ê²???ë³?ë¬¸ì„œ??`12. ?€ ?œì? API ?œí”Œë¦?ë¶€??ë¨¼ì? ê°±ì‹ ?˜ì„¸??


## 16. P1 Dashboard and Docs Mode Update (2026-02-28)

### 16.1 Core vs Full snapshot profile

`GET /api/v1/quant_ml/runs/{run_id}/snapshot` now supports:

1. `profile=core`
2. `profile=full` (default, backward compatible)

`core` profile is optimized for first paint and skips heavy calculations.
`full` profile keeps existing behavior for detailed tabs and diagnostics.

### 16.2 Bootstrap endpoint profile

`GET /api/v1/quant_ml/dashboard/bootstrap` now supports:

1. `snapshot_profile=core` (default)
2. `snapshot_profile=full`

Recommended default:

1. initial dashboard load: `snapshot_profile=core`
2. tab-level details: request `full` snapshot or tab-specific endpoints lazily

### 16.3 API docs mode by environment

Server-level docs mode is now controlled by:

1. `OPENBB_API_DOCS_MODE=disabled`
2. `OPENBB_API_DOCS_MODE=full`

`start_all.ps1` mapping:

1. `-ApiDocsMode dev` -> `OPENBB_API_DOCS_MODE=disabled`
2. `-ApiDocsMode prod` -> `OPENBB_API_DOCS_MODE=full`

Behavior:

1. disabled: `/docs`, `/redoc`, `/openapi.json` are disabled
2. full: docs and openapi are enabled

### 16.4 Startup examples

```powershell
# dev: low-latency startup, docs disabled
.\start_all.ps1 -ApiDocsMode dev

# prod-like: docs enabled + openapi prewarm
.\start_all.ps1 -ApiDocsMode prod
```


