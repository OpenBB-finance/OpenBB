---
title: filter_stocks
description: OpenBB SDK Function
---

# filter_stocks

## stocks_sia_financedatabase_model.filter_stocks

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py'
def filter_stocks(country: str, sector: str, industry: str, marketcap: str, exclude_exchanges: bool) -> list:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L109)

Description: Filter stocks based on country, sector, industry, market cap and exclude exchanges.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Search by country to find stocks matching the criteria. | None | False |
| sector | str | Search by sector to find stocks matching the criteria. | None | False |
| industry | str | Search by industry to find stocks matching the criteria. | None | False |
| marketcap | str | Select stocks based on the market cap. | None | False |
| exclude_exchanges | bool | When you wish to include different exchanges use this boolean. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of filtered stocks |

## Examples

