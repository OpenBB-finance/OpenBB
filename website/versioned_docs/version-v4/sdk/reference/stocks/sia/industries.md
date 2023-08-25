---
title: industries
description: OpenBB SDK Function
---

# industries

Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L69)]

```python
openbb.stocks.sia.industries(country: str = "", sector: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Filter retrieved industries by country |  | True |
| sector | str | Filter retrieved industries by sector |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible industries |
---

