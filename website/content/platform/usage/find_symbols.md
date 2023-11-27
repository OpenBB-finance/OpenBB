---
title: Finding Symbols
sidebar_position: 3
description: This page provides comprehensive information about finding stocks in the
  with the OpenBB Platform.  Search companies from different sources, and filter results.
  This guide is intended to introduce some methods for searching, screening, and discovery.
keywords:
- stocks
- companies
- how to find
- stocks from India
- countries
- regions
- screen
- search
- ticker
- sector
- industry
- market caps
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Finding Symbols - Usage | OpenBB Platform Docs" />

Finding the ticker symbol, security identifier, the sector, and other metadata is easy if you know where to look.  This guide is intended to introduce some methods for searching, screening, and discovery.

:::note
For maximum coverage and functionality, install OpenBB with `[all]` packages.

The examples on this page will assume that the OpenBB Platform has been installed, the environment is active, and it has been imported into a Python session.

```python
from openbb import obb
```

If the installation is fresh, or an extension was just installed, the Python interface will need to be rebuilt. It will only take a few moments to complete.
:::

The simplest way to find a ticker for a company is with a simple fuzzy query.

## Search the SEC

Perform a quick search using the `openbb-sec` provider.

### Find a Company

Use an empty string, `""`, to return the complete list - over 10,000.

```python
all_companies = obb.equity.search("", provider="sec")

len(all_companies.results)
```

```bash
Out: 10840
```

The SEC sorts this list by market cap.  Applying the `to_df()` method to `all_companies` will show Apple on top

```python
all_companies.to_df().head(10)
```

| symbol   | name                   |     cik |
|:---------|:-----------------------|--------:|
| AAPL     | Apple Inc.             |  320193 |
| MSFT     | MICROSOFT CORP         |  789019 |
| GOOGL    | Alphabet Inc.          | 1652044 |
| AMZN     | AMAZON COM INC         | 1018724 |
| NVDA     | NVIDIA CORP            | 1045810 |
| META     | Meta Platforms, Inc.   | 1326801 |
| BRK-B    | BERKSHIRE HATHAWAY INC | 1067983 |
| TSLA     | Tesla, Inc.            | 1318605 |
| LLY      | ELI LILLY & Co         |   59478 |
| V        | VISA INC.              | 1403161 |

:::tip
This endpoint can be used to map a ticker symbol to a CIK number.
:::

### Find an Institution

Some reporting companies, like investment trusts and insurance companies, do not have a ticker symbol directly associated with them. Filers in the US will have a CIK number, used to retrieve documents from the SEC.

```python
obb.regulators.sec.institutions_search("Berkshire Hathaway").to_df()
```

| name                                             |        cik |
|:-------------------------------------------------|-----------:|
| BERKSHIRE HATHAWAY ENERGY CO                     | 0001081316 |
| BERKSHIRE HATHAWAY FINANCE CORP                  | 0001274791 |
| BERKSHIRE HATHAWAY HOME STATE INSURANCE CO.       | 0000829771 |
| BERKSHIRE HATHAWAY INC /DE/                      | 0000109694 |
| BERKSHIRE HATHAWAY INC/DE                        | 0000109694 |
| BERKSHIRE HATHAWAY INC                           | 0001067983 |
| BERKSHIRE HATHAWAY LIFE INSURANCE CO OF NEBRASKA | 0001015867 |
| LMZ & BERKSHIRE HATHAWAY CO                      | 0001652795 |

### Find a Filing

Search for filings by CIK or ticker symbol.

```python
homestate_filings = obb.equity.fundamental.filings(cik="0000829771", provider="sec")

homestate_filings.to_df().iloc[-1]
```

|                         | 2023-11-14                                                                                  |
|:------------------------|:-----------------------------------------------------------------------------------------------------|
| type                    | 13F-NT                                                                                               |
| link                    | https://www.sec.gov/Archives/edgar/data/0000829771/000095012323010929/xslForm13F_X02/primary_doc.xml |
| report_date             | 2023-09-30                                                                                           |
| accepted_date           | 2023-11-14 16:15:06+00:00                                                                            |
| act                     | 34                                                                                                   |
| primary_doc_description |                                                                                                      |
| primary_doc             | xslForm13F_X02/primary_doc.xml                                                                       |
| accession_number        | 0000950123-23-010929                                                                                 |
| file_number             | 028-02226                                                                                            |
| film_number             | 231406391                                                                                            |
| is_inline_xbrl          | 0                                                                                                    |
| is_xbrl                 | 0                                                                                                    |
| size                    | 2960                                                                                                 |
| complete_submission_url | https://www.sec.gov/Archives/edgar/data/0000829771/0000950123-23-010929.txt                          |
| filing_detail_url       | https://www.sec.gov/Archives/edgar/data/0000829771/0000950123-23-010929-index.htm                    |

Or, search by form type.

```python
obb.equity.fundamental.filings("AAPL", type="4", provider="sec").to_df().iloc[-1]
```

|                         | 2023-11-14                                                                                    |
|:------------------------|:---------------------------------------------------------------------------------------------------------|
| type                    | 4                                                                                                        |
| link                    | https://www.sec.gov/Archives/edgar/data/0000320193/000032019323000109/xslF345X05/wk-form4_1700004649.xml |
| report_date             | 2023-11-10                                                                                               |
| accepted_date           | 2023-11-14 18:31:09+00:00                                                                                |
| primary_doc_description | FORM 4                                                                                                   |
| primary_doc             | xslF345X05/wk-form4_1700004649.xml                                                                       |
| accession_number        | 0000320193-23-000109                                                                                     |
| is_inline_xbrl          | 0                                                                                                        |
| is_xbrl                 | 0                                                                                                        |
| size                    | 5066                                                                                                     |
| complete_submission_url | https://www.sec.gov/Archives/edgar/data/0000320193/0000320193-23-000109.txt                              |
| filing_detail_url       | https://www.sec.gov/Archives/edgar/data/0000320193/0000320193-23-000109-index.htm                        |

## Screen Markets

Screeners provide a targeted search, a tool for comparison and discovery. Find stocks from around the world with the screener endpoint, and the `openbb-fmp` provider.

### Find Stocks From India

```python
results = obb.equity.screener(country="IN", provider="fmp").to_df()
len(results)
```

```bash
Out: 1821
```

### Search by Sector

```python
results = obb.equity.screener(country="IN", sector="Financial Services", provider="fmp").to_df()
len(results)
```

```bash
Out: 190
```

```python
results.iloc[0]
```

| symbol               | HDFCBANK.NS                      |
|:---------------------|:---------------------------------|
| name                 | HDFC Bank Limited                |
| market_cap           | 11344796293939                   |
| sector               | Financial Services               |
| industry             | Banks—Regional                   |
| beta                 | 0.714285                         |
| price                | 1505.1                           |
| last_annual_dividend | 19.0                             |
| volume               | 11850413                         |
| exchange             | NSE                              |
| exchange_name        | National Stock Exchange of India |
| country              | IN                               |
| is_etf               | False                            |
| actively_trading     | True                             |

### Search by Industry

```python
results = obb.equity.screener(country="IN", industry="manufacturing").to_df()
len(results)
```

```bash
Out: 119
```

```python
results.iloc[0]
```

| symbol               | PAGEIND.NS                       |
|:---------------------|:---------------------------------|
| name                 | Page Industries Limited          |
| market_cap           | 418222172840                     |
| sector               | Consumer Cyclical                |
| industry             | Apparel Manufacturing            |
| beta                 | 0.462                            |
| price                | 37495.6                          |
| last_annual_dividend | 300.0                            |
| volume               | 12166                            |
| exchange             | NSE                              |
| exchange_name        | National Stock Exchange of India |
| country              | IN                               |
| is_etf               | False                            |
| actively_trading     | True                             |

### Search by Exchange

Some countries, like America, have multiple exchanges. Narrow the search by combining two or more parameters. The example below finds the companies listed on the American Stock Exchange (AMEX) that are domiciled in China.

```python
obb.equity.screener(exchange="amex", country="CN").to_df()
```

| symbol   | name                              |   market_cap | sector             | industry                               |   beta |   price |   volume | exchange   | exchange_name           | country   | is_etf   | actively_trading   |
|:---------|:----------------------------------|-------------:|:-------------------|:---------------------------------------|-------:|--------:|---------:|:-----------|:------------------------|:----------|:---------|:-------------------|
| AMBO     | Ambow Education Holding Ltd.      |      4041842 | Consumer Defensive | Education & Training Services          |  0.448 |  0.1425 |   203994 | AMEX       | American Stock Exchange | CN        | False    | True               |
| ITP      | IT Tech Packaging, Inc.           |      2945282 | Basic Materials    | Paper & Paper Products                 | -0.1   |  0.2926 |    14954 | AMEX       | American Stock Exchange | CN        | False    | True               |
| DXF      | Dunxin Financial Holdings Limited |      1291625 | Financial Services | Credit Services                        |  1.632 |  0.325  |  2829238 | AMEX       | American Stock Exchange | CN        | False    | True               |
| CPHI     | China Pharma Holdings, Inc.       |      1024379 | Healthcare         | Drug Manufacturers—Specialty & Generic |  0.875 |  0.0896 |   539863 | AMEX       | American Stock Exchange | CN        | False    | True               |

### Filter by Metric

Applying some filters refines and targets the search. The example below finds listing on the NYSE domiciled in the USA, with a market cap between $100-300 billion, and exhibiting a beta value of less than 0.5

```python
obb.equity.screener(
  exchange="nyse",
  mktcap_min=100000000000,
  mktcap_max=300000000000,
  country="us",
  beta_max=0.5,
  provider="fmp",
).to_df()
```

| symbol   | name                        |   market_cap | sector                 | industry                   |   beta |   price |   last_annual_dividend |   volume | exchange   | exchange_name           | country   | is_etf   | actively_trading   |
|:---------|:----------------------------|-------------:|:-----------------------|:---------------------------|-------:|--------:|-----------------------:|---------:|:-----------|:------------------------|:----------|:---------|:-------------------|
| MRK      | Merck & Co., Inc.           | 258192673024 | Healthcare             | Drug Manufacturers—General |  0.375 |  101.75 |                   2.92 |  6760568 | NYSE       | New York Stock Exchange | US        | False    | True               |
| VZ       | Verizon Communications Inc. | 152314546478 | Communication Services | Telecom Services           |  0.391 |   36.23 |                   2.66 | 14960968 | NYSE       | New York Stock Exchange | US        | False    | True               |

## Find an Index

List all indices from a source with:

```python
indices = obb.index.available(provider="yfinance").to_df()

len(indices)
```

```bash
Out: 274
```

Filter the list down by querying the DataFrame.

```python
indices[indices["name"].str.contains("ASX 200")]
```

| name                                                  | code              | symbol   |
|:------------------------------------------------------|:------------------|:---------|
| S&P/ASX 200 Index (AUD)                               | au_asx200         | ^AXJO    |
| S&P/ASX 200 Energy Sector Index (AUD)                 | au_energy         | ^AXEJ    |
| S&P/ASX 200 Resources Sector Index (AUD)              | au_resources      | ^AXJR    |
| S&P/ASX 200 Materials Sector Index (AUD)              | au_materials      | ^AXMJ    |
| S&P/ASX 200 Industrials Sector Index (AUD)            | au_industrials    | ^AXNJ    |
| S&P/ASX 200 Consumer Discretionary Sector Index (AUD) | au_discretionary  | ^AXDJ    |
| S&P/ASX 200 Consumer Staples Sector Index (AUD)       | au_staples        | ^AXSJ    |
| S&P/ASX 200 Health Care Sector Index (AUD)            | au_health         | ^AXHJ    |
| S&P/ASX 200 Financials Sector Index (AUD)             | au_financials     | ^AXFJ    |
| S&P/ASX 200 A-REIT Industry Index (AUD)               | au_reit           | ^AXPJ    |
| S&P/ASX 200 Info Tech Sector Index (AUD)              | au_tech           | ^AXIJ    |
| S&P/ASX 200 Communications Sector Index (AUD)         | au_communications | ^AXTJ    |
| S&P/ASX 200 Utilities Sector Index (AUD)              | au_utilities      | ^AXUJ    |

:::tip
With the `openbb-yfinance` extension, index time series can be loaded using the ticker symbol or short code.  Non-American indices have a code beginning with the two-letter country code.

```python
(
    obb.index.market("au_utilities", provider="yfinance").to_df().tail(1)
    == obb.index.market("^AXUJ", provider="yfinance").to_df().tail(1)
)
```

| date                |   open |   high |   low |   close |   volume |
|:--------------------|-------:|-------:|------:|--------:|---------:|
| 2023-11-17 |  True |  True |  True |  True |  True |

:::

The examples above show demonstrate the most basic ways to find ticker symbols with the OpenBB Platform. Create your own custom scripts for discovery by combining these with other methods.
