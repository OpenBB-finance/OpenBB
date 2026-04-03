# Data Provider Suggestion: FinancialReports.eu

## Overview

[FinancialReports.eu](https://financialreports.eu) is a financial data API specializing in **regulatory filings and company disclosures** from 35 official sources across 30+ countries. It would complement OpenBB's existing data providers by adding global regulatory filing coverage — annual reports, interim reports, ESG disclosures, M&A announcements, and more.

## Why This Fits OpenBB

OpenBB aggregates data from dozens of providers, but filing coverage is primarily US-centric (SEC/EDGAR). FinancialReports.eu extends this to:

- **14M+ regulatory filings** from official regulators worldwide
- **33,000+ companies** with ISIN, LEI, and GICS industry classification
- **35 official sources**: SEC, FCA (UK), Euronext, EDINET (Japan), OPENDART (South Korea), SIX (Switzerland), BaFin (Germany), CNMV (Spain), AMF (France), and 26 more
- **11 standardized filing categories**: Financial Reporting, ESG Information, M&A/Partnerships/Legal, Debt/Equity Information, and more
- **Markdown endpoint** for LLM-ready text extraction from filings

## Integration Approach

### 1. OpenBB Data Provider Extension

FinancialReports.eu fits OpenBB's provider model — users bring their own API key. A provider extension could expose:

- `obb.equity.filings(symbol, source="financialreports")` — regulatory filings by company
- `obb.equity.filing_content(filing_id)` — filing text in Markdown for LLM analysis
- `obb.equity.filing_sources()` — list available regulatory sources

### 2. MCP Server Integration

FinancialReports.eu offers an [MCP server](https://financialreports.eu) compatible with Claude.ai and other AI platforms — similar to OpenBB's own AI agent integrations.

### 3. Python SDK

Official Python client available for direct integration:
```bash
pip install financial-reports-generated-client
```

## API Details

| Property | Value |
|---|---|
| **Base URL** | `https://api.financialreports.eu` |
| **API Docs** | [docs.financialreports.eu](https://docs.financialreports.eu/) |
| **Authentication** | API key via `X-API-Key` header |
| **Python SDK** | `pip install financial-reports-generated-client` |
| **Rate Limiting** | Burst limit + monthly quota (headers in responses) |
| **Format** | REST JSON (Markdown for filing content) |

### Key Endpoints

| Endpoint | Description |
|---|---|
| `GET /companies/` | Search 33K+ companies by ticker, ISIN, LEI, country, industry |
| `GET /filings/` | Search 14M+ filings by company, date, category, type, country |
| `GET /filings/{id}/markdown/` | Filing content as Markdown (LLM-ready) |
| `GET /companies/{id}/next-annual-report/` | Predicted next annual report date |
| `GET /sources/` | List all 35 regulatory data sources |
| `GET /filing-categories/` | 11 standardized disclosure categories |

### Code Example

```python
import requests

headers = {"X-API-Key": "your-api-key"}

# Search for a company by ISIN
resp = requests.get("https://api.financialreports.eu/companies/",
    headers=headers,
    params={"isin": "US0378331005", "page_size": 5}
)

# Fetch financial reporting filings
resp = requests.get("https://api.financialreports.eu/filings/",
    headers=headers,
    params={
        "company_isin": "US0378331005",
        "categories": "2",  # Financial Reporting
        "page_size": 10
    }
)

# Get filing content as Markdown for LLM analysis
resp = requests.get("https://api.financialreports.eu/filings/12345/markdown/",
    headers=headers
)
```

### Using the Python SDK

```python
from financial_reports_client import Client

client = Client(base_url="https://api.financialreports.eu")
client = client.with_headers({"X-API-Key": "your-api-key"})

from financial_reports_client.api.filings import filings_list
filings = filings_list.sync(client=client, company_isin="US0378331005", categories="2")
```

## Coverage Comparison

| OpenBB (current filing coverage) | + FinancialReports.eu |
|---|---|
| SEC/EDGAR (US) | 35 regulators across 30+ countries |
| US company filings | 33,000+ global companies |
| Raw filing documents | Markdown-converted text (LLM-ready) |
| — | Standardized filing categories across all sources |
| — | ESG disclosures, M&A, management changes |
| — | Predicted next annual report dates |
