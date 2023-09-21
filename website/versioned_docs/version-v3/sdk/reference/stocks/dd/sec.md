---
title: sec
description: OpenBB SDK Function
---

# sec

Get SEC filings for a given stock ticker. [Source: Market Watch]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/marketwatch_model.py#L20)]

```python
openbb.stocks.dd.sec(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | SEC filings data |
---

