---
title: sectors
description: OpenBB SDK Function
---

# sectors

Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L44)]

```python
openbb.stocks.sia.sectors(industry: str = "", country: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| industry | str | Filter retrieved sectors by industry |  | True |
| country | str | Filter retrieved sectors by country |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible sectors |
---

