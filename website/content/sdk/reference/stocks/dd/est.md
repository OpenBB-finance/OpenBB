---
title: est
description: OpenBB SDK Function
---

# est

Get analysts' estimates for a given ticker. [Source: Business Insider]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/business_insider_model.py#L76)]

```python
openbb.stocks.dd.est(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get analysts' estimates | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Year estimates |
---

