---
title: countries
description: OpenBB SDK Function
---

# countries

## stocks_sia_financedatabase_model.get_countries

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py'
def get_countries(industry: str, sector: str) -> list:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L19)

Description: Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| industry | str | Filter retrieved countries by industry | None | False |
| sector | str | Filter retrieved countries by sector | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible countries |

## Examples

