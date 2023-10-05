---
title: fwd
description: OpenBB SDK Function
---

# fwd

Gets forward rates from fxempire

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/fxempire_model.py#L14)]

```python
openbb.forex.fwd(to_symbol: str = "USD", from_symbol: str = "EUR")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | To currency | USD | True |
| from_symbol | str | From currency | EUR | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing forward rates |
---

