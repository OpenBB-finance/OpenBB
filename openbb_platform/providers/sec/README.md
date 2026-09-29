# OpenBB SEC Provider

Free, key-less access to U.S. **SEC EDGAR** data for the [OpenBB Platform](https://docs.openbb.co/platform) — filings, financial statements, fund holdings, ownership, and full-text search, with a built-in OpenBB Workspace backend.

No credentials or API key required. Responses are persisted to a local disk cache so repeated queries are fast and offline-friendly.

## Quick start

Launch the OpenBB Workspace backend with no prior install — [`uv`](https://docs.astral.sh/uv/) fetches the package and runs it in one step:

```bash
uvx openbb-sec serve --host 0.0.0.0 --port 6900
```

Then add `http://localhost:6900` as a custom backend in the OpenBB Workspace.

## Installation

```bash
pip install openbb-sec
```

A single install brings the provider, the OpenBB Workspace dashboards, the Filing Viewer MCP, and the `openbb-sec` command.

## Coverage

All endpoints are available under `obb.sec.*` in the Python/HTTP interface.

| Area | Endpoints |
| --- | --- |
| Filings & documents | `company_filings`, `latest_financial_reports`, `filing_headers`, `htm_file`, `full_text_search`, `rss_litigation`, `exhibit` |
| 10-K / 10-Q sections | `company_overview`, `risk_factors`, `legal_proceedings`, `disclosures`, `segment_revenue`, `financial_statements` |
| Proxy statement (DEF 14A) | `executive_compensation`, `pay_versus_performance`, `beneficial_ownership`, `management_profiles` |
| Funds | `nport_disclosure`, `nport_fund_metrics` |
| Reference & lookups | `cik_map`, `symbol_map`, `institutions_search`, `sic_search`, `schema_files` |

The SEC provider also implements standard models — financial statements (`balance_sheet`, `income_statement`, `cash_flow`, and their `*_growth`), `compare_company_facts`, `equity_search`, `equity_ftd`, `insider_trading`, `form_13f`, and `management_discussion_analysis`.
When `openbb-equity` / `openbb-etf` are installed these are reached as `obb.equity.*` / `obb.etf.*` with `provider="sec"`; when they are not, the same models register directly as `obb.sec.*`.

## Basic usage

```python
from openbb import obb

# Resolve identifiers
obb.sec.cik_map(symbol="AAPL")
obb.sec.symbol_map(query="0000320193")

# Filings and full-text search
obb.sec.company_filings(symbol="AAPL", form_type="10-K")
obb.sec.full_text_search(query="climate change", form_type="8-K")

# 10-K / 10-Q content (defaults to the latest filing)
obb.sec.risk_factors(symbol="AAPL")
obb.sec.financial_statements(symbol="AAPL", statement_type="balance")
obb.sec.segment_revenue(symbol="AAPL", calendar_year=2023)

# Proxy statement disclosures
obb.sec.executive_compensation(symbol="CAT")
obb.sec.pay_versus_performance(symbol="CAT")

# Fund holdings (N-PORT) and metrics
obb.sec.nport_disclosure(symbol="VTI")
obb.sec.nport_fund_metrics(symbol="VTI")
```

## OpenBB Workspace

The package ships ready-to-use OpenBB Workspace dashboards (`SEC Form 10-K/Q` and `SEC Filings`), a Filing Viewer that re-serves EDGAR documents for in-app rendering, and an MCP server that exposes the open document to the Workspace agent as text.

Launch a self-contained Workspace backend:

```bash
openbb-sec serve --host 0.0.0.0 --port 6900
```

## Cache management

The `openbb-sec` command also inspects and manages the disk cache:

```bash
openbb-sec info     # resolved cache folder, size limit, and disk usage
openbb-sec path     # print the resolved cache folder
openbb-sec clear    # empty the cache
```

The cache folder is resolved from, in order of precedence: the `--cache-dir` argument, the `OPENBB_SEC_CACHE_DIR` environment variable, the `cache_directory` preference from `openbb.toml` / user settings, then the OpenBB default (`~/OpenBBUserData/cache/sec`).

| Variable | Purpose | Default |
| --- | --- | --- |
| `OPENBB_SEC_CACHE_DIR` | SEC cache folder | `~/OpenBBUserData/cache/sec` |
| `OPENBB_SEC_CACHE_SIZE_LIMIT` | Max cache size (bytes or e.g. `"8GB"`) | `8GB` |
| `OPENBB_SEC_REQUESTS_PER_SECOND` | EDGAR request rate | `9` |
| `OPENBB_SEC_MCP_HOST` | Filing Viewer MCP host | `127.0.0.1` |
| `OPENBB_SEC_MCP_PORT` | Filing Viewer MCP port | `7769` |

## Documentation

Full documentation is available at [docs.openbb.co](https://docs.openbb.co/platform).
