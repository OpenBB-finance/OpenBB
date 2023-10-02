---
title: countries
description: OpenBB SDK Function
---

# countries

Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L19)]

```python
openbb.stocks.sia.countries(industry: str = "", sector: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| industry | str | Filter retrieved countries by industry |  | True |
| sector | str | Filter retrieved countries by sector |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible countries |
---

