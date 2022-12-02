---
title: futures
description: OpenBB SDK Function
---

# futures

Get futures data.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/sdk_helpers.py#L8)]

```python
openbb.economy.futures(source: Any = "WSJ", future_type: str = "Indices")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| source | str | Data source for futures data.  From the following: WSJ, Finviz | WSJ | True |
| future_type | str | (Finviz only) Future type to get.  Can be: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies. | Indices | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of futures data. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
wsj_futures = openbb.economy.futures()
```

```
To sort by the largest percent change:
```
```python
futures_sorted = openbb.economy.futures().sort_values(by="%Chg", ascending=False)
```

```
FinViz provides different options for future types.  We can get Meats with the following command:
```
```python
meat_futures = openbb.economy.futures(source="Finviz", future_type="Meats")
```

---

