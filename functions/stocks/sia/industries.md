---
title: industries
description: OpenBB SDK Function
---

# industries

## stocks_sia_financedatabase_model.get_industries

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py'
def get_industries(country: str, sector: str) -> list:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L69)

Description: Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Filter retrieved industries by country | None | False |
| sector | str | Filter retrieved industries by sector | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible industries |

## Examples

