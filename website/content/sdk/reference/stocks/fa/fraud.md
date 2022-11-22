---
title: fraud
description: OpenBB SDK Function
---

# fraud

Get fraud ratios based on fundamentals

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L594)]

```python
openbb.stocks.fa.fraud(symbol: str, detail: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| detail | bool | Whether to provide extra m-score details | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The fraud ratios |
---

