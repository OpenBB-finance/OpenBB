---
title: capm
description: OpenBB SDK Function
---

# capm

Provides information that relates to the CAPM model

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/quantitative_analysis/factors_model.py#L80)]

```python
openbb.stocks.qa.capm(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | A ticker symbol in string form | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[float, float] | The beta for a stock, The systematic risk for a stock |
---

