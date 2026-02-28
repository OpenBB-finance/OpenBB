# OpenBB 接入说明（面向第三方项目）

> 生成时间：2026-01-24 22:28:49

## 1. 基础信息
- Base URL: `http://127.0.0.1:6900`
- REST 文档: `/docs`
- OpenAPI: `/openapi.json`
- 覆盖字典（数据源映射）: `/api/v1/coverage/providers` 与 `/api/v1/coverage/commands`
- MCP（如需）：`http://127.0.0.1:8011/mcp`（streamable-http）
- Provider 原生能力（高级）：`/api/v1/provider/catalog` 与 `/api/v1/provider/query`

## 1.1 Docker 运行说明（当前环境）
服务与端口（来自 docker-compose）：
- 服务名 `openbb-api`（容器名同名）：对外端口 `6900` → 容器 `6900`
- 服务名 `openbb-mcp`（容器名同名）：对外端口 `8011` → 容器 `8011`

容器内调用（从其它容器访问宿主）建议使用：
- OpenBB API: `http://host.docker.internal:6900`
- OpenBB MCP: `http://host.docker.internal:8011/mcp`

常用启动/检查：
```bash
# 启动/重启
cd /Volumes/PSSD/Projects/OpenBB
/usr/local/bin/docker compose -f docker-compose.yml up -d

# 查看运行状态/端口
/usr/local/bin/docker ps --format 'table {{.Names}}	{{.Status}}	{{.Ports}}'

# 快速检查（宿主机）
curl -s http://127.0.0.1:6900/openapi.json > /dev/null
curl -sS -X POST http://127.0.0.1:8011/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  --data '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"clientInfo":{"name":"healthcheck","version":"0.1"},"protocolVersion":"2024-11-05","capabilities":{}}}' \
  | head -n 5 > /dev/null
```

> 构建提示：如无法拉取基础镜像，可在构建时指定本地镜像作为 BASE_IMAGE。
>
> 备注：本仓库当前 `openbb-mcp` 容器默认使用 `streamable-http`。如果你的客户端只支持 SSE，
> 需要把 `openbb-mcp` 以 `--transport sse` 启动，并使用 `/mcp/sse/` 作为 URL（否则会 404）。

## 1.2 LangBot 通过 MCP 接入（Streamable HTTP）
LangBot 插件的 MCP 客户端需要选择 **HTTP/Streamable**（不要选 SSE），并填写：
- URL：`http://host.docker.internal:8011/mcp`

常见报错与处理：
- 报错：`streamablehttp_client() got an unexpected keyword argument 'http_client'`
  - 原因：LangBot 容器里 `mcp` 包版本过旧（旧版 streamable-http client 不支持 `http_client` 参数）
  - 解决：在 LangBot 容器内升级 `mcp>=1.25.0` 并重启 LangBot
    ```bash
    docker exec -i langbot /app/.venv/bin/pip install -U 'mcp>=1.25.0'
    docker restart langbot langbot_plugin_runtime
    ```
  - 验证（容器内可达性 + 初始化成功）：
    ```bash
    docker exec -i langbot /app/.venv/bin/python - <<'PY'
    import json, urllib.request
    url='http://host.docker.internal:8011/mcp'
    body={"jsonrpc":"2.0","id":"1","method":"initialize",
          "params":{"clientInfo":{"name":"langbot","version":"0.1"},
          "protocolVersion":"2024-11-05","capabilities":{}}}
    req=urllib.request.Request(url, data=json.dumps(body).encode(),
                               headers={"Content-Type":"application/json",
                                        "Accept":"application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.status, resp.headers.get("mcp-session-id"))
    PY
    ```

## 1.3 MCP 最小化工具 + 全量双语 Skills（已启用）
为同时兼顾“低噪声”和“全覆盖调用”，当前 `openbb-mcp` 采用以下组合：

- 保留分类：`economy,equity,fixedincome,provider,regulators`
- 保留管理工具：`admin,prompt`
- 其余分类默认不暴露给 MCP 客户端
- 启用双语 server prompts（EN/ZH）：
  - 13 个业务技能（如 `market-router` / `macro-monitor` / `china-market`）
  - 155 个逐工具技能封装（`skill-<tool_name>`），覆盖当前全部 MCP tools
  - 合计 168 个 prompts（自动生成）

对应 `docker-compose.yml` 环境变量：

```yaml
OPENBB_MCP_DEFAULT_TOOL_CATEGORIES: economy,equity,fixedincome,provider,regulators
OPENBB_MCP_ALLOWED_TOOL_CATEGORIES: economy,equity,fixedincome,provider,regulators
OPENBB_MCP_INCLUDE_TAGS: economy,equity,fixedincome,provider,regulators,admin,prompt
OPENBB_MCP_SERVER_PROMPTS_FILE: /app/config/mcp_server_prompts_bilingual_full.json
```

实测（当前实例）：
- 全量模式约 `271` tools
- 最小模式约 `155` tools（包含 regulators）

可复用文件：
- Prompt 配置：`build/config/mcp_server_prompts_bilingual_full.json`
- 生成脚本：`build/config/generate_mcp_skillpack.py`
- 清单说明：`build/config/mcp_skillpack_manifest.md`

如需恢复全量，可改回：

```yaml
OPENBB_MCP_DEFAULT_TOOL_CATEGORIES: all
OPENBB_MCP_INCLUDE_TAGS:
```

## 1.4 P0 默认选源与元信息规范
- `provider` 省略时：默认按 `auto` 走服务端策略引擎。
- `provider=auto`：显式开启自动选源与回退链。
- 选源优先级（当前策略）：质量/权威优先，并结合凭证可用性；失败后按候选链回退。

统一返回（标准 API 响应）：
- `extra.meta.route`
- `extra.meta.provider_requested`
- `extra.meta.provider_used`
- `extra.meta.provider_candidates`
- `extra.meta.fallback_trace`
- `extra.meta.confidence`
- `extra.meta.selection_reason`（含 `mode`、`scored_providers`、`health_source`、`strategy_source`）

P2（策略配置化）：
- 默认策略为内置配置；可通过 `OPENBB_PROVIDER_STRATEGY_PATH` 指向外部 JSON 覆盖：
  - `provider_priority`
  - `route_policy_bonus`
  - `credential_ready_bonus`
  - `credential_missing_penalty`
  - `health_weights`

## 2. 数据源字典（动态获取）
用于让调用方快速确认“数据源 → 可用接口 / 接口 → 可用数据源”。

```bash
# provider -> routes
curl -s http://127.0.0.1:6900/api/v1/coverage/providers

# route -> providers
curl -s http://127.0.0.1:6900/api/v1/coverage/commands
```

## 2.1 Provider 原生接口字典（高级/全量）
用于对接“官方 API 很多、OpenBB 标准模型尚未覆盖”的场景（如 Tushare/Wind）。

```bash
# 查看 provider 原生分类与方法（Wind/Tushare）
curl -s 'http://127.0.0.1:6900/api/v1/provider/catalog?provider=tushare'
curl -s 'http://127.0.0.1:6900/api/v1/provider/catalog?provider=wind'

# 直接调用 provider 原生接口（Raw Query）
# - tushare: method=api_name, kwargs=pro.query 的参数（例如 daily/income 等）
curl -s -X POST 'http://127.0.0.1:6900/api/v1/provider/query' \\
  -H 'Content-Type: application/json' \\
  --data '{\"provider\":\"tushare\",\"method\":\"daily\",\"args\":[],\"kwargs\":{\"ts_code\":\"000001.SZ\",\"start_date\":\"20240102\",\"end_date\":\"20240105\"}}'

# - wind: method=WindPy 方法（wsd/wss/wsi/wset/edb），args/kwargs 按 WindPy 规范传
curl -s -X POST 'http://127.0.0.1:6900/api/v1/provider/query' \\
  -H 'Content-Type: application/json' \\
  --data '{\"provider\":\"wind\",\"method\":\"wsd\",\"args\":[\"000001.SZ\",\"close\",\"2024-01-02\",\"2024-01-05\",\"\"],\"kwargs\":{}}'
```

> Wind 说明：如果 OpenBB 跑在 Docker 里，通常容器内无法直接安装/授权 WindPy。建议在“已安装并鉴权 WindPy 的宿主机/专用机器”上运行 Wind Gateway，然后让容器通过 HTTP 调用：
>
> - 容器侧环境变量（OpenBB API/MCP 容器都要设置）：`OPENBB_WIND_GATEWAY_URL=http://host.docker.internal:9901`
> - 宿主机启动网关（二选一）：
>   - 方式 A：如果你的 Python 环境里已安装 `openbb-wind`（并满足其 OpenBB 依赖），直接运行：`openbb-wind-gateway --host 0.0.0.0 --port 9901`
>   - 方式 B（推荐，最少依赖）：只要 WindPy 可用 + 本仓库代码即可运行（示例以 macOS 为主）：
>
>     ```bash
>     # 1) 选择一个能 import WindPy 的 Python（确保你已在该环境完成 WindPy 鉴权）
>     PY=/opt/homebrew/bin/python3
>
>     # 2) 建 venv 并安装网关依赖
>     $PY -m venv .wind-gateway-venv
>     source .wind-gateway-venv/bin/activate
>     pip install 'fastapi>=0.110' 'uvicorn[standard]>=0.27'
>
>     # 3) 把 WindPy 所在目录和本仓库 wind provider 目录加入 PYTHONPATH
>     WINDPY_SITE="$($PY -c 'import WindPy, os; print(os.path.dirname(WindPy.__file__))')"
>     export PYTHONPATH="$PWD/openbb_platform/providers/wind:$WINDPY_SITE"
>
>     # 4) 启动（对外暴露 9901）
>     uvicorn openbb_wind.gateway.app:app --host 0.0.0.0 --port 9901
>     ```

## 3. 快速请求示例
```bash
# 股票历史（省略 provider，默认 auto）
curl -s 'http://127.0.0.1:6900/api/v1/equity/price/historical?symbol=AAPL&start_date=2024-01-01&end_date=2024-01-31'

# 股票历史（显式 auto）
curl -s 'http://127.0.0.1:6900/api/v1/equity/price/historical?provider=auto&symbol=AAPL&start_date=2024-01-01&end_date=2024-01-31'

# 宏观 GDP 增速（IMF）
curl -s 'http://127.0.0.1:6900/api/v1/economy/indicators?provider=imf&symbol=WEO%3A%3ANGDP_RPCH&country=USA&start_date=2020-01-01&end_date=2024-12-31'

# Tushare Pro 日线（A股示例，symbol=000001 可自动推断交易所）
curl -s 'http://127.0.0.1:6900/api/v1/equity/price/historical?provider=tushare&symbol=000001&start_date=2024-01-01&end_date=2024-01-31'

# Tushare Pro 公司概况（如需明确交易所，可传 exchange=SH/SZ/BJ 或带后缀）
curl -s 'http://127.0.0.1:6900/api/v1/equity/profile?provider=tushare&symbol=000001'

# 代码类型提示（ETF/指数等建议传 asset_type=etf/index 或显式 exchange）
# 例如：...&symbol=510300&asset_type=etf 或 ...&symbol=000300&asset_type=index&exchange=SH

# Tushare Pro ETF 日线
curl -s 'http://127.0.0.1:6900/api/v1/etf/historical?provider=tushare&symbol=510300&asset_type=etf&start_date=2024-01-01&end_date=2024-01-31'

# Tushare Pro 指数日线
curl -s 'http://127.0.0.1:6900/api/v1/index/price/historical?provider=tushare&symbol=000300&asset_type=index&exchange=SH&start_date=2024-01-01&end_date=2024-01-31'

# Tushare Pro 财报（资产负债表/利润表/现金流）
curl -s 'http://127.0.0.1:6900/api/v1/equity/fundamental/balance?provider=tushare&symbol=000001&limit=4'
curl -s 'http://127.0.0.1:6900/api/v1/equity/fundamental/income?provider=tushare&symbol=000001&limit=4'
curl -s 'http://127.0.0.1:6900/api/v1/equity/fundamental/cash?provider=tushare&symbol=000001&limit=4'

# Tushare Pro 分红历史
curl -s 'http://127.0.0.1:6900/api/v1/equity/fundamental/dividends?provider=tushare&symbol=000001&start_date=2020-01-01&end_date=2024-12-31'

# ETF 热门（WSJ）
curl -s 'http://127.0.0.1:6900/api/v1/etf/discovery/gainers?provider=wsj&limit=5&sort=desc'
```

## 4. 响应结构与错误处理
- 常见响应结构：`{ id, results, provider, warnings, chart, extra }`
- P0 推荐读取：`extra.meta`（选源与回退可观测字段）
- 典型错误：
  - `400 Missing credential`：缺少 API Key/权限
  - `422 Validation Error`：参数不合法/缺必填
  - `500`：上游数据源或参数逻辑异常

## 4.1 每日真实业务回归（P0）
用于验证“自动选源 + 统一 meta + 准确性可证明”。

```bash
cd /Users/lichengyin/Desktop/Projects/OpenBB
python3 build/quality/run_daily_regression.py --base-url http://127.0.0.1:6900
```

产物：
- 用例库：`build/quality/daily_regression_cases.json`
- 报告目录：`build/quality/reports/`
- 说明：`build/quality/README.md`

## 5. 凭证配置（如需付费/受限源）
- 推荐写入：`~/.openbb_platform/user_settings.json` 的 `credentials` 字段
- 例如：`tushare_api_key`, `alpha_vantage_api_key`, `polygon_api_key`
- 或通过环境变量注入（容器环境）

## 6. Providers → Routes（当前服务实时快照）
| Provider | Routes |
|---|---|
| `alpha_vantage` | /equity/fundamental/historical_eps, /equity/price/historical, /etf/historical |
| `benzinga` | /equity/estimates/price_target, /equity/estimates/analyst_search, /news/world, /news/company |
| `biztoc` | /news/world |
| `bls` | /economy/survey/bls_series, /economy/survey/bls_search |
| `cboe` | /derivatives/options/chains, /derivatives/futures/curve, /equity/price/quote, /equity/price/historical, /equity/search, /etf/historical, /index/price/historical, /index/constituents, /index/snapshots, /index/available, /index/search |
| `cftc` | /regulators/cftc/cot_search, /regulators/cftc/cot |
| `congress_gov` | /uscongress/bills, /uscongress/bill_info, /uscongress/bill_text |
| `deribit` | /derivatives/options/chains, /derivatives/futures/historical, /derivatives/futures/curve, /derivatives/futures/instruments, /derivatives/futures/info |
| `ecb` | /currency/reference_rates, /economy/balance_of_payments, /fixedincome/government/yield_curve |
| `econdb` | /economy/gdp/nominal, /economy/gdp/real, /economy/shipping/port_volume, /economy/country_profile, /economy/available_indicators, /economy/indicators, /economy/export_destinations, /fixedincome/government/yield_curve |
| `eia` | /commodity/petroleum_status_report, /commodity/short_term_energy_outlook |
| `famafrench` | /famafrench/factors, /famafrench/us_portfolio_returns, /famafrench/regional_portfolio_returns, /famafrench/country_portfolio_returns, /famafrench/international_index_returns, /famafrench/breakpoints |
| `federal_reserve` | /economy/money_measures, /economy/central_bank_holdings, /economy/primary_dealer_positioning, /economy/primary_dealer_fails, /economy/fomc_documents, /fixedincome/rate/sofr, /fixedincome/rate/effr, /fixedincome/rate/overnight_bank_funding, /fixedincome/government/yield_curve, /fixedincome/government/treasury_rates |
| `finra` | /equity/darkpool/otc, /equity/shorts/short_interest |
| `finviz` | /equity/compare/groups, /equity/estimates/price_target, /equity/fundamental/metrics, /equity/price/performance, /equity/screener, /equity/profile, /etf/price_performance |
| `fmp` | /crypto/price/historical, /crypto/search, /currency/price/historical, /currency/search, /currency/snapshots, /economy/calendar, /economy/risk_premium, /equity/calendar/ipo, /equity/calendar/dividend, /equity/calendar/splits, /equity/calendar/events, /equity/calendar/earnings, /equity/compare/peers, /equity/estimates/price_target, /equity/estimates/historical, /equity/estimates/consensus, /equity/estimates/forward_ebitda, /equity/estimates/forward_eps, /equity/discovery/gainers, /equity/discovery/losers, /equity/discovery/active, /equity/discovery/filings, /equity/fundamental/balance, /equity/fundamental/balance_growth, /equity/fundamental/cash, /equity/fundamental/cash_growth, /equity/fundamental/dividends, /equity/fundamental/historical_eps, /equity/fundamental/employee_count, /equity/fundamental/income, /equity/fundamental/income_growth, /equity/fundamental/metrics, /equity/fundamental/management, /equity/fundamental/management_compensation, /equity/fundamental/ratios, /equity/fundamental/revenue_per_geography, /equity/fundamental/revenue_per_segment, /equity/fundamental/filings, /equity/fundamental/historical_splits, /equity/fundamental/transcript, /equity/fundamental/esg_score, /equity/ownership/major_holders, /equity/ownership/institutional, /equity/ownership/insider_trading, /equity/ownership/share_statistics, /equity/ownership/government_trades, /equity/price/quote, /equity/price/historical, /equity/price/performance, /equity/screener, /equity/profile, /equity/market_snapshots, /equity/historical_market_cap, /etf/search, /etf/historical, /etf/info, /etf/sectors, /etf/countries, /etf/price_performance, /etf/holdings, /etf/nport_disclosure, /etf/equity_exposure, /fixedincome/government/yield_curve, /fixedincome/government/treasury_rates, /index/price/historical, /index/constituents, /index/available, /news/world, /news/company |
| `fred` | /commodity/price/spot, /economy/survey/sloos, /economy/survey/university_of_michigan, /economy/survey/economic_conditions_chicago, /economy/survey/manufacturing_outlook_texas, /economy/survey/manufacturing_outlook_ny, /economy/survey/nonfarm_payrolls, /economy/cpi, /economy/balance_of_payments, /economy/fred_search, /economy/fred_series, /economy/fred_release_table, /economy/fred_regional, /economy/retail_prices, /economy/pce, /fixedincome/rate/ameribor, /fixedincome/rate/sonia, /fixedincome/rate/sofr, /fixedincome/rate/iorb, /fixedincome/rate/effr, /fixedincome/rate/effr_forecast, /fixedincome/rate/estr, /fixedincome/rate/ecb, /fixedincome/rate/dpcredit, /fixedincome/rate/overnight_bank_funding, /fixedincome/spreads/tcm, /fixedincome/spreads/tcm_effr, /fixedincome/spreads/treasury_effr, /fixedincome/government/yield_curve, /fixedincome/government/tips_yields, /fixedincome/corporate/hqm, /fixedincome/corporate/spot_rates, /fixedincome/corporate/commercial_paper, /fixedincome/bond_indices, /fixedincome/mortgage_indices |
| `government_us` | /commodity/psd_data, /commodity/psd_report, /commodity/weather_bulletins, /commodity/weather_bulletins_download, /fixedincome/government/treasury_auctions, /fixedincome/government/treasury_prices |
| `imf` | /economy/shipping/port_info, /economy/shipping/port_volume, /economy/shipping/chokepoint_info, /economy/shipping/chokepoint_volume, /economy/cpi, /economy/available_indicators, /economy/indicators, /economy/direction_of_trade |
| `intrinio` | /currency/search, /derivatives/options/chains, /derivatives/options/unusual, /derivatives/options/snapshots, /economy/fred_series, /equity/calendar/ipo, /equity/estimates/consensus, /equity/estimates/forward_sales, /equity/estimates/forward_ebitda, /equity/estimates/forward_eps, /equity/estimates/forward_pe, /equity/fundamental/balance, /equity/fundamental/cash, /equity/fundamental/reported_financials, /equity/fundamental/dividends, /equity/fundamental/search_attributes, /equity/fundamental/latest_attributes, /equity/fundamental/historical_attributes, /equity/fundamental/income, /equity/fundamental/metrics, /equity/fundamental/ratios, /equity/fundamental/filings, /equity/ownership/insider_trading, /equity/ownership/share_statistics, /equity/price/quote, /equity/price/historical, /equity/search, /equity/profile, /equity/market_snapshots, /equity/historical_market_cap, /etf/search, /etf/historical, /etf/info, /etf/price_performance, /etf/holdings, /index/price/historical, /news/world, /news/company |
| `multpl` | /index/sp500_multiples |
| `nasdaq` | /economy/calendar, /equity/calendar/ipo, /equity/calendar/dividend, /equity/calendar/earnings, /equity/discovery/top_retail, /equity/fundamental/dividends, /equity/fundamental/filings, /equity/search, /equity/screener |
| `oecd` | /economy/gdp/forecast, /economy/gdp/nominal, /economy/gdp/real, /economy/cpi, /economy/unemployment, /economy/composite_leading_indicator, /economy/share_price_index, /economy/house_price_index, /economy/interest_rates |
| `polygon` | /crypto/price/historical, /currency/price/historical, /currency/search, /currency/snapshots, /equity/fundamental/balance, /equity/fundamental/cash, /equity/fundamental/income, /equity/price/nbbo, /equity/price/historical, /equity/market_snapshots, /etf/historical, /index/price/historical, /news/company |
| `sec` | /equity/compare/company_facts, /equity/discovery/latest_financial_reports, /equity/fundamental/filings, /equity/fundamental/management_discussion_analysis, /equity/ownership/insider_trading, /equity/ownership/form_13f, /equity/shorts/fails_to_deliver, /equity/search, /etf/nport_disclosure, /regulators/sec/filing_headers, /regulators/sec/htm_file, /regulators/sec/cik_map, /regulators/sec/institutions_search, /regulators/sec/schema_files, /regulators/sec/symbol_map, /regulators/sec/rss_litigation, /regulators/sec/sic_search |
| `seeking_alpha` | /equity/calendar/earnings, /equity/estimates/forward_sales, /equity/estimates/forward_eps |
| `stockgrid` | /equity/shorts/short_volume |
| `tiingo` | /crypto/price/historical, /currency/price/historical, /equity/fundamental/trailing_dividend_yield, /equity/price/historical, /etf/historical, /news/world, /news/company |
| `tmx` | /derivatives/options/chains, /equity/calendar/earnings, /equity/estimates/consensus, /equity/discovery/gainers, /equity/fundamental/dividends, /equity/fundamental/filings, /equity/ownership/insider_trading, /equity/price/quote, /equity/price/historical, /equity/search, /equity/profile, /etf/search, /etf/historical, /etf/info, /etf/sectors, /etf/countries, /etf/holdings, /fixedincome/government/treasury_prices, /fixedincome/corporate/bond_prices, /index/constituents, /index/snapshots, /index/available, /index/sectors, /news/company |
| `tradier` | /derivatives/options/chains, /equity/price/quote, /equity/price/historical, /equity/search, /etf/historical |
| `tradingeconomics` | /economy/calendar |
| `tushare` | /equity/price/historical, /equity/profile, /equity/fundamental/balance, /equity/fundamental/income, /equity/fundamental/cash, /equity/fundamental/dividends, /etf/historical, /index/price/historical |
| `wsj` | /etf/discovery/gainers, /etf/discovery/losers, /etf/discovery/active |
| `yfinance` | /crypto/price/historical, /currency/price/historical, /derivatives/options/chains, /derivatives/futures/historical, /derivatives/futures/curve, /equity/estimates/consensus, /equity/discovery/gainers, /equity/discovery/losers, /equity/discovery/active, /equity/discovery/undervalued_large_caps, /equity/discovery/undervalued_growth, /equity/discovery/aggressive_small_caps, /equity/discovery/growth_tech, /equity/fundamental/balance, /equity/fundamental/cash, /equity/fundamental/dividends, /equity/fundamental/income, /equity/fundamental/metrics, /equity/fundamental/management, /equity/ownership/share_statistics, /equity/price/quote, /equity/price/historical, /equity/screener, /equity/profile, /etf/historical, /etf/info, /index/price/historical, /index/available, /news/company |

## 7. Routes → Providers（当前服务实时快照）
| Route | Providers |
|---|---|
| `/commodity/petroleum_status_report` | eia |
| `/commodity/price/spot` | fred |
| `/commodity/psd_data` | government_us |
| `/commodity/psd_report` | government_us |
| `/commodity/short_term_energy_outlook` | eia |
| `/commodity/weather_bulletins` | government_us |
| `/commodity/weather_bulletins_download` | government_us |
| `/crypto/price/historical` | fmp, polygon, tiingo, yfinance |
| `/crypto/search` | fmp |
| `/currency/price/historical` | fmp, polygon, tiingo, yfinance |
| `/currency/reference_rates` | ecb |
| `/currency/search` | fmp, intrinio, polygon |
| `/currency/snapshots` | fmp, polygon |
| `/derivatives/futures/curve` | cboe, deribit, yfinance |
| `/derivatives/futures/historical` | deribit, yfinance |
| `/derivatives/futures/info` | deribit |
| `/derivatives/futures/instruments` | deribit |
| `/derivatives/options/chains` | cboe, deribit, intrinio, tmx, tradier, yfinance |
| `/derivatives/options/snapshots` | intrinio |
| `/derivatives/options/unusual` | intrinio |
| `/economy/available_indicators` | econdb, imf |
| `/economy/balance_of_payments` | ecb, fred |
| `/economy/calendar` | fmp, nasdaq, tradingeconomics |
| `/economy/central_bank_holdings` | federal_reserve |
| `/economy/composite_leading_indicator` | oecd |
| `/economy/country_profile` | econdb |
| `/economy/cpi` | fred, imf, oecd |
| `/economy/direction_of_trade` | imf |
| `/economy/export_destinations` | econdb |
| `/economy/fomc_documents` | federal_reserve |
| `/economy/fred_regional` | fred |
| `/economy/fred_release_table` | fred |
| `/economy/fred_search` | fred |
| `/economy/fred_series` | fred, intrinio |
| `/economy/gdp/forecast` | oecd |
| `/economy/gdp/nominal` | econdb, oecd |
| `/economy/gdp/real` | econdb, oecd |
| `/economy/house_price_index` | oecd |
| `/economy/indicators` | econdb, imf |
| `/economy/interest_rates` | oecd |
| `/economy/money_measures` | federal_reserve |
| `/economy/pce` | fred |
| `/economy/primary_dealer_fails` | federal_reserve |
| `/economy/primary_dealer_positioning` | federal_reserve |
| `/economy/retail_prices` | fred |
| `/economy/risk_premium` | fmp |
| `/economy/share_price_index` | oecd |
| `/economy/shipping/chokepoint_info` | imf |
| `/economy/shipping/chokepoint_volume` | imf |
| `/economy/shipping/port_info` | imf |
| `/economy/shipping/port_volume` | econdb, imf |
| `/economy/survey/bls_search` | bls |
| `/economy/survey/bls_series` | bls |
| `/economy/survey/economic_conditions_chicago` | fred |
| `/economy/survey/manufacturing_outlook_ny` | fred |
| `/economy/survey/manufacturing_outlook_texas` | fred |
| `/economy/survey/nonfarm_payrolls` | fred |
| `/economy/survey/sloos` | fred |
| `/economy/survey/university_of_michigan` | fred |
| `/economy/unemployment` | oecd |
| `/equity/calendar/dividend` | fmp, nasdaq |
| `/equity/calendar/earnings` | fmp, nasdaq, seeking_alpha, tmx |
| `/equity/calendar/events` | fmp |
| `/equity/calendar/ipo` | fmp, intrinio, nasdaq |
| `/equity/calendar/splits` | fmp |
| `/equity/compare/company_facts` | sec |
| `/equity/compare/groups` | finviz |
| `/equity/compare/peers` | fmp |
| `/equity/darkpool/otc` | finra |
| `/equity/discovery/active` | fmp, yfinance |
| `/equity/discovery/aggressive_small_caps` | yfinance |
| `/equity/discovery/filings` | fmp |
| `/equity/discovery/gainers` | fmp, tmx, yfinance |
| `/equity/discovery/growth_tech` | yfinance |
| `/equity/discovery/latest_financial_reports` | sec |
| `/equity/discovery/losers` | fmp, yfinance |
| `/equity/discovery/top_retail` | nasdaq |
| `/equity/discovery/undervalued_growth` | yfinance |
| `/equity/discovery/undervalued_large_caps` | yfinance |
| `/equity/estimates/analyst_search` | benzinga |
| `/equity/estimates/consensus` | fmp, intrinio, tmx, yfinance |
| `/equity/estimates/forward_ebitda` | fmp, intrinio |
| `/equity/estimates/forward_eps` | fmp, intrinio, seeking_alpha |
| `/equity/estimates/forward_pe` | intrinio |
| `/equity/estimates/forward_sales` | intrinio, seeking_alpha |
| `/equity/estimates/historical` | fmp |
| `/equity/estimates/price_target` | benzinga, finviz, fmp |
| `/equity/fundamental/balance` | fmp, intrinio, polygon, tushare, yfinance |
| `/equity/fundamental/balance_growth` | fmp |
| `/equity/fundamental/cash` | fmp, intrinio, polygon, tushare, yfinance |
| `/equity/fundamental/cash_growth` | fmp |
| `/equity/fundamental/dividends` | fmp, intrinio, nasdaq, tmx, tushare, yfinance |
| `/equity/fundamental/employee_count` | fmp |
| `/equity/fundamental/esg_score` | fmp |
| `/equity/fundamental/filings` | fmp, intrinio, nasdaq, sec, tmx |
| `/equity/fundamental/historical_attributes` | intrinio |
| `/equity/fundamental/historical_eps` | alpha_vantage, fmp |
| `/equity/fundamental/historical_splits` | fmp |
| `/equity/fundamental/income` | fmp, intrinio, polygon, tushare, yfinance |
| `/equity/fundamental/income_growth` | fmp |
| `/equity/fundamental/latest_attributes` | intrinio |
| `/equity/fundamental/management` | fmp, yfinance |
| `/equity/fundamental/management_compensation` | fmp |
| `/equity/fundamental/management_discussion_analysis` | sec |
| `/equity/fundamental/metrics` | finviz, fmp, intrinio, yfinance |
| `/equity/fundamental/ratios` | fmp, intrinio |
| `/equity/fundamental/reported_financials` | intrinio |
| `/equity/fundamental/revenue_per_geography` | fmp |
| `/equity/fundamental/revenue_per_segment` | fmp |
| `/equity/fundamental/search_attributes` | intrinio |
| `/equity/fundamental/trailing_dividend_yield` | tiingo |
| `/equity/fundamental/transcript` | fmp |
| `/equity/historical_market_cap` | fmp, intrinio |
| `/equity/market_snapshots` | fmp, intrinio, polygon |
| `/equity/ownership/form_13f` | sec |
| `/equity/ownership/government_trades` | fmp |
| `/equity/ownership/insider_trading` | fmp, intrinio, sec, tmx |
| `/equity/ownership/institutional` | fmp |
| `/equity/ownership/major_holders` | fmp |
| `/equity/ownership/share_statistics` | fmp, intrinio, yfinance |
| `/equity/price/historical` | alpha_vantage, cboe, fmp, intrinio, polygon, tiingo, tmx, tradier, tushare, yfinance |
| `/equity/price/nbbo` | polygon |
| `/equity/price/performance` | finviz, fmp |
| `/equity/price/quote` | cboe, fmp, intrinio, tmx, tradier, yfinance |
| `/equity/profile` | finviz, fmp, intrinio, tmx, tushare, yfinance |
| `/equity/screener` | finviz, fmp, nasdaq, yfinance |
| `/equity/search` | cboe, intrinio, nasdaq, sec, tmx, tradier |
| `/equity/shorts/fails_to_deliver` | sec |
| `/equity/shorts/short_interest` | finra |
| `/equity/shorts/short_volume` | stockgrid |
| `/etf/countries` | fmp, tmx |
| `/etf/discovery/active` | wsj |
| `/etf/discovery/gainers` | wsj |
| `/etf/discovery/losers` | wsj |
| `/etf/equity_exposure` | fmp |
| `/etf/historical` | alpha_vantage, cboe, fmp, intrinio, polygon, tiingo, tmx, tradier, tushare, yfinance |
| `/etf/holdings` | fmp, intrinio, tmx |
| `/etf/info` | fmp, intrinio, tmx, yfinance |
| `/etf/nport_disclosure` | fmp, sec |
| `/etf/price_performance` | finviz, fmp, intrinio |
| `/etf/search` | fmp, intrinio, tmx |
| `/etf/sectors` | fmp, tmx |
| `/famafrench/breakpoints` | famafrench |
| `/famafrench/country_portfolio_returns` | famafrench |
| `/famafrench/factors` | famafrench |
| `/famafrench/international_index_returns` | famafrench |
| `/famafrench/regional_portfolio_returns` | famafrench |
| `/famafrench/us_portfolio_returns` | famafrench |
| `/fixedincome/bond_indices` | fred |
| `/fixedincome/corporate/bond_prices` | tmx |
| `/fixedincome/corporate/commercial_paper` | fred |
| `/fixedincome/corporate/hqm` | fred |
| `/fixedincome/corporate/spot_rates` | fred |
| `/fixedincome/government/tips_yields` | fred |
| `/fixedincome/government/treasury_auctions` | government_us |
| `/fixedincome/government/treasury_prices` | government_us, tmx |
| `/fixedincome/government/treasury_rates` | federal_reserve, fmp |
| `/fixedincome/government/yield_curve` | ecb, econdb, federal_reserve, fmp, fred |
| `/fixedincome/mortgage_indices` | fred |
| `/fixedincome/rate/ameribor` | fred |
| `/fixedincome/rate/dpcredit` | fred |
| `/fixedincome/rate/ecb` | fred |
| `/fixedincome/rate/effr` | federal_reserve, fred |
| `/fixedincome/rate/effr_forecast` | fred |
| `/fixedincome/rate/estr` | fred |
| `/fixedincome/rate/iorb` | fred |
| `/fixedincome/rate/overnight_bank_funding` | federal_reserve, fred |
| `/fixedincome/rate/sofr` | federal_reserve, fred |
| `/fixedincome/rate/sonia` | fred |
| `/fixedincome/spreads/tcm` | fred |
| `/fixedincome/spreads/tcm_effr` | fred |
| `/fixedincome/spreads/treasury_effr` | fred |
| `/index/available` | cboe, fmp, tmx, yfinance |
| `/index/constituents` | cboe, fmp, tmx |
| `/index/price/historical` | cboe, fmp, intrinio, polygon, tushare, yfinance |
| `/index/search` | cboe |
| `/index/sectors` | tmx |
| `/index/snapshots` | cboe, tmx |
| `/index/sp500_multiples` | multpl |
| `/news/company` | benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance |
| `/news/world` | benzinga, biztoc, fmp, intrinio, tiingo |
| `/regulators/cftc/cot` | cftc |
| `/regulators/cftc/cot_search` | cftc |
| `/regulators/sec/cik_map` | sec |
| `/regulators/sec/filing_headers` | sec |
| `/regulators/sec/htm_file` | sec |
| `/regulators/sec/institutions_search` | sec |
| `/regulators/sec/rss_litigation` | sec |
| `/regulators/sec/schema_files` | sec |
| `/regulators/sec/sic_search` | sec |
| `/regulators/sec/symbol_map` | sec |
| `/uscongress/bill_info` | congress_gov |
| `/uscongress/bill_text` | congress_gov |
| `/uscongress/bills` | congress_gov |

## 8. 备注
- 数据源/接口清单会随 OpenBB 版本更新而变化，以覆盖字典与 OpenAPI 为准。
