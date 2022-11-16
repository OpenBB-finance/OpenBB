---
title: sectors
description: OpenBB SDK Function
---

# sectors

## stocks_sia_financedatabase_model.get_sectors

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py'
def get_sectors(industry: str, country: str) -> list:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L44)

Description: Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| industry | str | Filter retrieved sectors by industry | None | False |
| country | str | Filter retrieved sectors by country | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible sectors |

## Examples

