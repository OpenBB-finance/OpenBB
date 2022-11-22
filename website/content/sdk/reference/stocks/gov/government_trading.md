---
title: government_trading
description: OpenBB SDK Function
---

# government_trading

Returns the most recent transactions by members of government

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L25)]

```python
openbb.stocks.gov.government_trading(gov_type: str = "congress", symbol: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| gov_type | str | Type of government data between:<br/>'congress', 'senate', 'house', 'contracts', 'quarter-contracts' and 'corporate-lobbying' | congress | True |
| symbol | str | Ticker symbol to get congress trading data from |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most recent transactions by members of U.S. Congress |
---

