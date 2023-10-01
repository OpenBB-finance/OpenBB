---
title: filter_stocks
description: OpenBB SDK Function
---

# filter_stocks

Filter stocks based on country, sector, industry, market cap and exclude exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L109)]

```python
openbb.stocks.sia.filter_stocks(country: str = None, sector: str = None, industry: str = None, marketcap: str = "", exclude_exchanges: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Search by country to find stocks matching the criteria. | None | True |
| sector | str | Search by sector to find stocks matching the criteria. | None | True |
| industry | str | Search by industry to find stocks matching the criteria. | None | True |
| marketcap | str | Select stocks based on the market cap. |  | True |
| exclude_exchanges | bool | When you wish to include different exchanges use this boolean. | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of filtered stocks |
---

